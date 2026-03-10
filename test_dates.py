from utils.date_helpers import parse_date, days_until_expiry, get_reminder_stage
from datetime import date, timedelta

d = parse_date('2026-03-15')
print('Parsed date:', d)

future = date.today() + timedelta(days=7)
print('Days left:', days_until_expiry(future))

print('Stage for 7 days:', get_reminder_stage(7))
print('Stage for 3 days:', get_reminder_stage(3))
print('Stage for 1 day: ', get_reminder_stage(1))
print('Stage for 0 days:', get_reminder_stage(0))
print('Stage for 10 days:', get_reminder_stage(10))
