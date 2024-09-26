import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
from .models import Rating, Product, User


class CFRecommender:
    def __init__(self, k=5, dist_func=cosine_similarity, CF=1):
        self.k = k
        self.dist_func = dist_func
        self.CF = CF  # 1 cho lọc cộng tác người dùng, 0 cho sản phẩm
        self.Ybar_data = None
        self.mean = None
        self.Ybar = None
        self.S = None

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
        Y_data = Y_data.astype(int)  # Chuyển đổi tất cả các giá trị thành số nguyên

        users = Y_data[:, 0]  # Cột user_id
        self.mean = np.zeros(np.max(users) + 1)  # Mảng trung bình cho mỗi user
        self.Ybar_data = Y_data.copy()  # Tạo bản sao dữ liệu đánh giá

        for n in range(len(self.mean)):
            ids = np.where(users == n)[0]  # Tìm tất cả các đánh giá của user n
            ratings = Y_data[ids, 2]  # Lấy tất cả các đánh giá của user n
            m = np.mean(ratings) if len(ratings) > 0 else 0  # Trung bình các đánh giá
            self.mean[n] = m  # Gán giá trị trung bình
            self.Ybar_data[ids, 2] = ratings - self.mean[n]  # Chuẩn hóa các đánh giá

        # Tạo ma trận sparse từ dữ liệu đánh giá đã chuẩn hóa
        self.Ybar = sparse.coo_matrix(
            (self.Ybar_data[:, 2], (self.Ybar_data[:, 1], self.Ybar_data[:, 0]))
        )
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
        if Y_data is None:
            raise ValueError("Không có dữ liệu đánh giá.")
        self.normalize_Y(Y_data)  # Chuẩn hóa dữ liệu đánh giá
        self.similarity()  # Tính toán ma trận tương đồng

    def predict(self, user_id, product_id):
        """
        Dự đoán đánh giá cho một người dùng và một sản phẩm nhất định.
        """
        user_id = int(user_id)  # Chuyển đổi thành số nguyên
        product_id = int(product_id)  # Chuyển đổi thành số nguyên

        # Giả sử self.Ybar là ma trận thưa đã được khởi tạo
        user_ratings = self.Ybar[:, user_id].toarray().flatten()
        sim_users = self.S[user_id]  # Lấy độ tương đồng của người dùng

        # Lấy đánh giá cho sản phẩm i
        ratings = self.Ybar[product_id, :].toarray().flatten()

        # Đảm bảo không chia cho 0 nếu không có user tương đồng
        if np.abs(sim_users).sum() > 0:
            pred = sim_users.dot(ratings) / np.abs(sim_users).sum()
        else:
            pred = 0  # Đặt giá trị dự đoán là 0 nếu không có user tương đồng

        return pred

    def recommend(self, user_id):
        """
        Gợi ý sản phẩm cho người dùng
        """
        if self.S is None:
            raise ValueError("Mô hình chưa được huấn luyện")

        # Lấy đánh giá của user_id trong ma trận đánh giá
        user_ratings = self.Ybar[:, user_id].toarray().flatten()
        rated_items = np.where(user_ratings > 0)[0]  # Sản phẩm đã đánh giá
        recommendations = []

        # Duyệt qua các sản phẩm chưa được đánh giá
        for i in range(self.Ybar.shape[0]):
            if i not in rated_items:
                # Lấy độ tương đồng giữa user và những user khác
                sim_users = self.S[user_id]
                ratings = self.Ybar[i, :].toarray().flatten()  # Đánh giá cho sản phẩm i

                # Đảm bảo không chia cho 0 nếu không có user tương đồng
                if np.abs(sim_users).sum() > 0:
                    pred = sim_users.dot(ratings) / np.abs(sim_users).sum()
                else:
                    pred = 0  # Đặt giá trị dự đoán là 0 nếu không có user tương đồng

                recommendations.append((i, pred))
        # Sắp xếp theo thứ tự dự đoán rating
        recommendations.sort(key=lambda x: x[1], reverse=True)

        # Lấy danh sách product_id
        recommended_ids = [r[0] for r in recommendations[: self.k]]

        # Truy vấn cơ sở dữ liệu
        recommended_products = Product.objects.filter(id__in=recommended_ids)

        return recommended_products if recommended_products.exists() else []
