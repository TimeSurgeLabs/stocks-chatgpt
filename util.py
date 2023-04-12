import arrow
from alpaca.data.timeframe import TimeFrame


def resolve_since_time(since: str):
    if since == "day":
        return arrow.now().shift(hours=-24).datetime, TimeFrame.Hour
    elif since == "week":
        return arrow.now().shift(weeks=-1).datetime, TimeFrame.Day
    elif since == "month":
        return arrow.now().shift(months=-1).datetime, TimeFrame.Day
    elif since == "year":
        return arrow.now().shift(years=-1).datetime, TimeFrame.Month
    else:
        raise Exception("Invalid since time")
