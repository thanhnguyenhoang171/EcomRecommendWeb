import numpy as np
from .models import Rating  # Điều chỉnh theo mô hình của bạn
from .recommendation import CFRecommender


class Evaluator:
    def __init__(self, recommender):
        self.recommender = recommender

    def load_test_data(self):
        """
        Lấy dữ liệu đánh giá từ cơ sở dữ liệu.
        """
        # Lấy dữ liệu đánh giá từ cơ sở dữ liệu
        ratings = Rating.objects.all().values_list(
            "customer_id", "product_id", "rating"
        )
        return np.array(list(ratings))

    def evaluate(self):
        """
        Đánh giá mô hình bằng cách tính RMSE.
        """
        rate_test = self.load_test_data()  # Lấy dữ liệu kiểm tra
        if rate_test.size == 0:
            print("Không có dữ liệu kiểm tra để đánh giá.")
            return None, None  # Trả về None nếu không có dữ liệu

        # Kiểm tra hình dạng của rate_test
        if rate_test.ndim == 1:
            rate_test = rate_test.reshape(-1, 3)  # Chuyển đổi thành 2 chiều nếu cần

        n_tests = rate_test.shape[0]
        SE = 0  # squared error

        for n in range(n_tests):
            user_id = int(rate_test[n, 0])    # customer_id, đảm bảo là số nguyên
            product_id = int(rate_test[n, 1])  # product_id, đảm bảo là số nguyên
            actual_rating = rate_test[n, 2]  # rating thực tế

            # Dự đoán đánh giá
            pred = self.recommender.predict(user_id, product_id)

            # Tính lỗi bình phương
            SE += (pred - actual_rating) ** 2

        # Tính RMSE
        RMSE = np.sqrt(SE / n_tests) if n_tests > 0 else float('inf')
        print("User-user CF, RMSE =", RMSE)

        return SE, RMSE  # Đảm bảo trả về SE và RMSE




# Sử dụng lớp Evaluator trong một view hoặc script
def run_evaluation():
    # Tạo một instance của mô hình của bạn
    recommender = CFRecommender(k=30, CF=1)  # Ví dụ, thay đổi theo nhu cầu của bạn
    recommender.fit()  # Huấn luyện mô hình
    evaluator = Evaluator(recommender)
    evaluator.evaluate()


# Nếu bạn muốn chạy đánh giá này khi khởi động ứng dụng
# Bạn có thể gọi hàm run_evaluation() trong views.py hoặc nơi thích hợp
