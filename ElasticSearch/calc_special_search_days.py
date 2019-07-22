from dateutil import easter
from dateutil.rrule import *
from dateutil.parser import *
from dateutil import relativedelta
from datetime import *
import jdcal
import json

day_mapping = {SU: 'Sunday', MO: 'Monday', TU: 'Tuesday', WE: 'Wednesday', TH: 'Thursday', FR: 'Friday', SA: 'Saturday'}
weekdays = {x:[] for x in day_mapping.values()}

# Add all dates for all days of the week between 500 and 1000
for day in (day_mapping.items()):
    for dt in rrule(WEEKLY, byweekday=day[0], dtstart=parse('05000101'), until=parse('10001231')):
        x = jdcal.jd2jcal(*jdcal.gcal2jd(dt.year, dt.month, dt.day))
        weekdays[day[1]].append('{:04}-{:02}-{:02}'.format(x[0], x[1], x[2]))

# Add all dates for Easter
weekdays['Easter'] = []
for y in range(500, 1001):
    weekdays['Easter'].append(str(easter.easter(y, method=1)))

# Add the date ranges for Lent
weekdays['Lent'] = []
for e in weekdays['Easter']:
    ash = str(datetime.date(parse(e) + relativedelta.relativedelta(days=-46)))
    lent_end = str(datetime.date(parse(e) + relativedelta.relativedelta(days=-1)))
    if ash in weekdays['Wednesday']:
        weekdays['Lent'].append((ash, lent_end))
    else:
        # This if for the three years that are leap years and where Ash Wednesday occurs in February, i.e., 500, 600, 700, 1000
        weekdays['Lent'].append((str(datetime.date(parse(e) + relativedelta.relativedelta(days=-45))), lent_end))

# Add dates for Pentecost
weekdays['Pentecost'] = []
for e in weekdays['Easter']:
    weekdays['Pentecost'].append(str(datetime.date(parse(e) + relativedelta.relativedelta(days=+49))))

# Save to a JSON file
with open('/home/matt/results/special_search_days.json', mode="w") as f:
    json.dump(weekdays, f)
