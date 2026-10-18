from datetime import datetime, timezone


def utc_now():
    """Naive UTC timestamp, matching how datetimes are stored in the database."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
