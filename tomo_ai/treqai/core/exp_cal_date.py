from datetime import date, timedelta

def get_next_business_day(today: date) -> date:
    next_day = today + timedelta(days=1)

    # 토(5) → 월(+2), 일(6) → 월(+1)
    if next_day.weekday() == 5:
        next_day += timedelta(days=2)
    elif next_day.weekday() == 6:
        next_day += timedelta(days=1)

    return next_day
