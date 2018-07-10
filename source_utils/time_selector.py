import datetime
import time

from source_utils.re_usables import add_minutes

# from consortium.models import Company

DAYS_OF_WEEK = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
]


def to_am_pm_date(date_time):
    return datetime.datetime.strptime(date_time, "%Y-%m-%d %I:%M %p")

# def format_to_am_pm()

def day_plus_12_time_to_datetime(st_date, st_time, end_date, end_time):
    st_date_time = "{} {}".format(st_date, st_time)
    end_date_time = "{} {}".format(end_date, end_time)
    if to_am_pm_date(end_date_time) < datetime.datetime.now():
        return 1, 1
    if to_am_pm_date(st_date_time) < datetime.datetime.now():
        start_time = datetime.datetime.strftime(
            add_minutes(datetime.datetime.now(), 15),
                "%Y-%m-%d %I:%M %p"
            )
        start_time = list(start_time)
        start_time[-4] = '0'
        start_time = "".join(start_time)
        return start_time, to_am_pm_date(end_date_time)
    else:
        return to_am_pm_date(st_date_time), to_am_pm_date(end_date_time)


def order_weekdays(days):
    unordered_days = {}
    ordered_days = []
    for day in days:
        unordered_days[time.strptime(day.day, "%A").tm_wday] = day
    for key in sorted(unordered_days.keys()):
        ordered_days.append(unordered_days[key])
    return ordered_days


def str_time(time):
    str_time = str(time)
    if len(str_time) == 1:
        str_time = "0" + str_time
    return str_time


def time_to_int(time):
    time = ''.join(i for i in str(time) if i.isdigit())


def select_time_options(company, option=0):
    # print(company)
    all_times = []
    step_start = datetime.datetime.strptime(company['start'], "%I:%M %p")
    step_end = datetime.datetime.strptime(company['end'], "%I:%M %p")
    step = company['step']
    while step_start <= step_end:
        all_times.append((step_start.strftime(
            "%I:%M %p").lstrip('0'),
                step_start.strftime("%I:%M %p").lstrip('0')
            )
        )
        step_start = add_minutes(step_start, step)
    if all_times:
        if option == 1:
           del all_times[-1]
        else:
           del all_times[0]
    else:
        all_times.append("No avail")
    # print(all_times) 
    return all_times


# def company_details():
#     company = Company.objects.get(pk=1)
#     time_step = company.work_step
#     hours = Hours.objects.all()
#     return {'time_step':time_step, 'hours':hours}

