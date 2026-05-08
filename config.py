# Telegram notifications
telegram_enabled = False  # master switch — set to False to disable all Telegram notifications

telegram_bot_token = "12345567:AAAAAAAAAAAAAAA"
telegram_chat_id = "1234567"

telegram_notify_on_capture = True   # notify when a frame is captured successfully
telegram_notify_on_timelapse = True  # notify when a timelapse is created successfully

# List of cameras with their credentials
# Each camera should have: name, ip_address, username, password
cameras = [
    {
        "name": "backyard",
        "ip_address": "192.168.1.108:554",
        "username": "admin",
        "password": "123admin",
        "rtsp_path": "cam/realmonitor?channel=1&subtype=0"  # The path after the IP address
    }
]
