import string
import re
import datetime

from django.utils.timezone import localtime 
from django import forms
from django.utils.translation import ugettext_lazy as _


def add_minutes(time, minutes):
    # print(time, minutes)
    return time + datetime.timedelta(minutes=minutes)

def sub_minutes(time, minutes):
    return time - datetime.timedelta(minutes=minutes)

from django import template

register = template.Library()


def cap_all_words(sentence):
    return string.capwords(sentence)

def fix_phone(phone):
    phone = re.sub("\D", "", phone)
    return format(int(phone[:-1]), ",").replace(",", "-") + phone[-1]

def add_one_day(day):
    # print(day)
    day = int(day) + 1
    # print(day)
    return day

def sub_one_day(day):
    day = int(day) - 1
    return day

# {% load custom_tags %}
register.filter('cap_all_words', cap_all_words)
register.filter('fix_phone', fix_phone)
register.filter('add_one_day', add_one_day)
register.filter('sub_one_day', sub_one_day)