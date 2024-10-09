import os
import json
import requests


# Lấy thông tin ngrok từ API
def get_ngrok_info():
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        data = response.json()
        return data["tunnels"][0]["public_url"]  # Lấy URL công khai đầu tiên
    except (requests.RequestException, IndexError) as e:
        print(f"Error fetching ngrok info: {e}")
        return None


# Cập nhật ALLOWED_HOSTS và CSRF_TRUSTED_ORIGINS
def update_django_settings():
    ngrok_url = get_ngrok_info()
    if ngrok_url:
        ngrok_domain = ngrok_url.split("//")[1]  # Lấy phần domain từ URL

        # Đường dẫn đến file settings.py của bạn
        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )  # Lấy đường dẫn đến thư mục cha
        settings_path = os.path.join(
            base_dir, "EcommerceWebsite", "settings.py"
        )  # Tạo đường dẫn chính xác

        try:
            with open(settings_path, "r", encoding="utf-8") as file:
                settings = file.readlines()

            # Tìm và thay thế ALLOWED_HOSTS và CSRF_TRUSTED_ORIGINS
            for i, line in enumerate(settings):
                if line.startswith("ALLOWED_HOSTS"):
                    settings[i] = (
                        f'ALLOWED_HOSTS = ["{ngrok_domain}", "localhost", "127.0.0.1"]\n'
                    )
                elif line.startswith("CSRF_TRUSTED_ORIGINS"):
                    settings[i] = f'CSRF_TRUSTED_ORIGINS = ["{ngrok_url}"]\n'

            with open(settings_path, "w", encoding="utf-8") as file:
                file.writelines(settings)

            print(f"Updated settings with ngrok URL: {ngrok_url}")
        except FileNotFoundError:
            print(f"File not found: {settings_path}")
        except Exception as e:
            print(f"Error updating settings: {e}")
    else:
        print("Could not retrieve ngrok URL.")


if __name__ == "__main__":
    update_django_settings()
