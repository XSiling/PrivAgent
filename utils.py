import datetime

def get_current_time():
    return datetime.datetime.now(tz=datetime.timezone.utc).isoformat()