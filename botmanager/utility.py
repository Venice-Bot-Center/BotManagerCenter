import datetime


def letter_cmp(a, b):
    if a[2] > b[2]:
        return -1
    if a[2] == b[2]:
        if a[0] > b[0]:
            return 1
        return -1
    else:
        return 1


def get_monday() -> datetime.date:
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday() + 8)
