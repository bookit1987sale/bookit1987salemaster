import re
import string

from django import forms
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


def check_name(name):
    """
    Handles ensuring entry uses only letter and is capitalized.
    """
    if not only_letters.search(name):
        raise forms.ValidationError(_('Enter a valid name. This \
                                      value must contain only letters.'))
    return string.capwords(name)


def check_phone_options(value):
    if check_phone.search(value):
        value = "+1" + value
        return value
    elif check_mod_space_phone.search(value):
        value = "+1" + value
        return value
    elif check_mod_phone.search(value):               
        return value
    else:
        raise forms.ValidationError(_('Enter a valid phone number\
                                      - ex. 2223334444.')) 

