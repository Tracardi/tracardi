from datetime import datetime
import tzlocal


def get_timezone():
    local_timezone = tzlocal.get_localzone()
    return local_timezone.utcoffset(datetime.now()).seconds // 3600
