from __future__ import unicode_literals
from django.db import models

import datetime
import operator

from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from account.models import Account
from source_utils.starters import CommonInfo, CommonAccountDetails

from versatileimagefield.fields import (
    VersatileImageField, 
    PPOIField
)

# from event.models import ClientEvent

def upload_location(instance, filename):
    return "%s/%s" %(instance.slug, filename)


class ClientMember(CommonAccountDetails):
    '''
    Account details
    '''
    base_account = models.OneToOneField(
        Account,
        verbose_name = 'Client',
        related_name='client_account',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return "{} {} ({})".format(
            self.base_account.user.first_name,
            self.base_account.user.last_name[0],
            self.pk
        )

    def get_friendly_name(self):
        return "{} {}.".format(
            self.base_account.user.first_name,
            self.base_account.user.last_name[0]
        )

    def first_name(self):
        return self.base_account.user.first_name

    def get_full_name(self):
        return "{} {}".format(
            self.base_account.user.first_name,
            self.base_account.user.last_name
        )

    def get_address(self):
        return "{}\n{}, {} {}".format(
          self.street_address, 
          self.city, 
          self.state, 
          self.zip_code
        ) 

def pre_save_client(sender, instance, *args, **kwargs):
    slug = "{} {} {}".format(
            instance.base_account.user.first_name,
            instance.base_account.user.last_name[0],
            instance.pk
        )
    instance.slug = slugify(slug)

pre_save.connect(pre_save_client, sender=ClientMember)
