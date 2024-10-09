@echo off
start ngrok http 8000
timeout /t 5 /nobreak > NUL
python app/update_ngrok_settings.py
python manage.py runserver 8000