from datetime import datetime, timedelta


def format_time(timestamp):
    now = datetime.now()
    time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    if now - time <= timedelta(minutes=5):
        return "刚刚"
    elif now.date() == time.date():
        return time.strftime("%H %M %S")
    else:
        return timestamp
