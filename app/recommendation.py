import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
from .models import Rating, Product


class CFRecommender:
    def __init__(self, k=5, dist_func=cosine_similarity, CF=1):
        self.k = k
        self.dist_func = dist_func
        self.CF = CF  # 1 cho lọc cộng tác người dùng, 0 cho sản phẩm
        self.Ybar_data = None
        self.mean = None
        self.Ybar = None
        self.S = None
        self.product_to_index = {}

    def fetch_data(self):
        """
        Lấy dữ liệu đánh giá từ cơ sở dữ liệu Django
        """
        ratings = Rating.objects.all().values("rating", "customer_id", "product_id")
        df = pd.DataFrame(list(ratings))
        if df.empty:
            return None
        return df[["customer_id", "product_id", "rating"]].values

    def normalize_Y(self, Y_data):
        """
        Chuẩn hóa dữ liệu đánh giá
        """
        if Y_data is None:
            raise ValueError("Không có dữ liệu đánh giá để chuẩn hóa.")

        # Ép kiểu customer_id và product_id thành integer
        Y_data = Y_data.astype(int)

        users = Y_data[:, 0]  # Cột user_id
        products = Y_data[:, 1]  # Cột product_id
        self.mean = np.zeros(np.max(users) + 1)  # Mảng trung bình cho mỗi user
        self.Ybar_data = Y_data.copy()  # Tạo bản sao dữ liệu đánh giá

        for n in range(len(self.mean)):
            ids = np.where(users == n)[0]  # Tìm tất cả các đánh giá của user n
            ratings = Y_data[ids, 2]  # Lấy tất cả các đánh giá của user n
            m = np.mean(ratings) if len(ratings) > 0 else 0  # Trung bình các đánh giá
            self.mean[n] = m  # Gán giá trị trung bình
            self.Ybar_data[ids, 2] = ratings - self.mean[n]  # Chuẩn hóa các đánh giá

        # Tạo mapping cho product IDs
        unique_products = np.unique(products)
        self.product_to_index = {
            product_id: index for index, product_id in enumerate(unique_products)
        }
        product_indices = np.array(
            [self.product_to_index[prod_id] for prod_id in products]
        )

        # Tạo ma trận sparse từ dữ liệu đánh giá đã chuẩn hóa
        self.Ybar = sparse.coo_matrix((self.Ybar_data[:, 2], (product_indices, users)))
        self.Ybar = self.Ybar.tocsr()  # Chuyển đổi sang định dạng CSR

    def similarity(self):
        """
        Tính toán ma trận tương đồng giữa các người dùng
        """
        if self.Ybar is None:
            raise ValueError("Ma trận Ybar chưa được khởi tạo.")
        self.S = self.dist_func(self.Ybar.T, self.Ybar.T)  # Tính cosine similarity

    def fit(self):
        """
        Khởi chạy quá trình huấn luyện mô hình
        """
        Y_data = self.fetch_data()  # Lấy dữ liệu đánh giá từ cơ sở dữ liệu
        if Y_data is None or len(Y_data) == 0:
            raise ValueError("Không có dữ liệu đánh giá để huấn luyện mô hình.")
        self.normalize_Y(Y_data)  # Chuẩn hóa dữ liệu đánh giá
        self.similarity()  # Tính toán ma trận tương đồng

    def predict(self, user_id, product_id):
        """
        Dự đoán đánh giá cho một người dùng và một sản phẩm nhất định.
        """
        user_id = int(user_id)  # Chuyển đổi thành số nguyên
        product_id = int(product_id)  # Chuyển đổi thành số nguyên

        # Kiểm tra chỉ số
        if user_id >= self.Ybar.shape[1]:
            raise IndexError("Chỉ số người dùng vượt quá giới hạn.")
        if product_id not in self.product_to_index:
            raise IndexError("Chỉ số sản phẩm vượt quá giới hạn.")

        product_index = self.product_to_index[product_id]
        user_ratings = self.Ybar[:, user_id].toarray().flatten()
        sim_users = self.S[user_id]  # Lấy độ tương đồng của người dùng
        ratings = self.Ybar[product_index, :].toarray().flatten()

        if np.abs(sim_users).sum() > 0:
            pred = sim_users.dot(ratings) / np.abs(sim_users).sum()
        else:
            pred = 0  # Đặt giá trị dự đoán là 0 nếu không có user tương đồng

        return pred

    def recommend(self, user_id):
        """
        Gợi ý sản phẩm cho người dùng mà người dùng đó chưa đánh giá.
        """
        if self.S is None:
            raise ValueError("Mô hình chưa được huấn luyện.")

        user_id = int(user_id)  # Chuyển đổi thành số nguyên

        # Kiểm tra chỉ số người dùng
        if user_id >= self.Ybar.shape[1]:
            raise IndexError("Chỉ số người dùng vượt quá giới hạn.")

        user_ratings = self.Ybar[:, user_id].toarray().flatten()
        rated_items = set(np.where(user_ratings > 0)[0])  # Sản phẩm đã đánh giá

        all_product_ids = set(Product.objects.values_list("id", flat=True))
        recommendations = []

        for product_id in all_product_ids:  # Duyệt qua tất cả các sản phẩm
            if product_id not in rated_items:  # Chỉ gợi ý sản phẩm chưa được đánh giá
                if (
                    product_id in self.product_to_index
                ):  # Kiểm tra sản phẩm có trong mapping
                    product_index = self.product_to_index[product_id]
                    sim_users = self.S[user_id]
                    ratings = self.Ybar[product_index, :].toarray().flatten()

                    if np.abs(sim_users).sum() > 0:
                        pred = sim_users.dot(ratings) / np.abs(sim_users).sum()
                    else:
                        pred = 0

                    recommendations.append((product_id, pred))

        # Sắp xếp theo thứ tự dự đoán rating
        recommendations.sort(key=lambda x: x[1], reverse=True)
        recommended_ids = [r[0] for r in recommendations[: self.k]]

        recommended_products = Product.objects.filter(id__in=recommended_ids)
        return recommended_products if recommended_products.exists() else []
