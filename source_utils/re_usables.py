import re
import string
import datetime

from django import forms
from django.utils.timezone import localtime 
from django.utils.translation import ugettext_lazy as _


# alnum_re = re.compile(r"^\w+$")
alnum_re = re.compile(r'^[\w.@+-]+$')#re.compile(r"^\w+$")
only_letters = re.compile(r'^[a-z A-Z \']+$')
company_name_check = re.compile(r'^[a-z A-Z \' 0-9]+$')
check_names = re.compile(r'^[\w]{2,}$')
check_phone = re.compile(r'^[0-9]{10}$')
check_mod_phone = re.compile(r'^\+1([0-9]{10})$')
check_mod_space_phone = re.compile(r'^([0-9]{3})( *)([0-9]{3})( *)([0-9]{4})$')
check_zip = re.compile(r'^[0-9]{5}$')
check_time_input = re.compile(r'^(([0-1]?[0-9])|([2][0-3])):([0-5]?[0-9])(:([0-5]?[0-9]))?$')


def time_format_no_zero(time):
    return datetime.datetime.strptime(time, '%H:%M').strftime("%I:%M %p").lstrip('0')


def add_minutes(time, minutes):
    if type(time) == str:
        time = datetime.datetime.strptime(time, "%Y-%m-%d %I:%M %p")
    return time + datetime.timedelta(minutes=minutes)


def sub_minutes(time, minutes):
    return time - datetime.timedelta(minutes=minutes)


def check_name(name):
    """
    Handles ensuring entry uses only letter and is capitalized.
    """
    if not only_letters.search(name):
        raise forms.ValidationError(_('Enter a valid name. This \
                                      value must contain only letters.'))
    return string.capwords(name)


def check_phone_options(value):

    phone_num = ''.join(i for i in str(value) if i.isdigit())
    if check_phone.search(phone_num):
        return True
    else:
        return False 


def get_actual_hours_and_minutes(hrs, mins):
    duration = (hrs, mins)
    if mins < 0:
        hrs -= 1
        mins = 60 + mins
    return duration


def time_additions(hours, minutes):
    hours += minutes // 60
    minutes = minutes % 60
    return hours, minutes


def minutes_to_decimal_hours(minutes):
    return minutes / 60


def hours_and_minutes_to_decimal_hours(hrs, mins):
    if mins == 0:
        return hrs
    if mins < 0:
    	hrs -= 1
    	mins = 60 + mins
    return hrs + minutes_to_decimal_hours(mins)

def meeting_iter(meeting_number):
    end_number = int(repr(meeting_number)[-1])
    if end_number == 1 and meeting_number != 11:
        return "{}{}".format(meeting_number, "st")
    elif end_number == 2 and meeting_number != 12:
        return "{}{}".format(meeting_number, "nd")
    elif end_number == 3 and meeting_number != 13:
        return "{}{}".format(meeting_number, "rd")
    elif meeting_number < 100:
        return "{}{}".format(meeting_number, "th")
    else:
        return meeting_number

def local_time_conversion(time):
        return localtime(time)

def appt_time_conversion(time):
        return time.strftime("%a %b %d %Y %I:%M %p")

def hour_time_conversion(time):
        return time.strftime("%I:%M")
