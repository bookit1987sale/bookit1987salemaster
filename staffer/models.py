from __future__ import unicode_literals
from django.db import models

import datetime
import operator

from account.models import Account
from service.models import Service
from source_utils.starters import CommonInfo, CommonAccountDetails
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


# def update_serv():
#     services = Service.objects.all()
#     for service in services:
#         service.save()


def upload_location(instance, filename):
    return "%s/%s" %(instance.slug, filename)

class StaffMember(CommonAccountDetails):

    base_account = models.OneToOneField(
        Account,
        verbose_name = 'Staff Member',
        related_name='staff_account',
        on_delete=models.CASCADE
    )

    # skills = models.ForeignKey(
    #     Service,
    #     null=True,
    #     blank=True,
    #     verbose_name = 'skills',
    #     related_name='skill_set',
    #     on_delete=models.CASCADE
    # )

    skill_set = models.ManyToManyField(
        # 'Available Skills',
        Service,
        related_name='staff_skills',
        # null=True,
        blank=True
        )

    def __str__(self):
        return "{} {} ({})".format(
            self.base_account.user.first_name,
            self.base_account.user.last_name,
            self.pk
        )

    def get_absolute_url(self):
        return reverse(
            "staff:staff_update",
            kwargs={'pk': self.pk}
            )

    # def get_avail_url(self):
    #     return reverse(
    #         "staff:staff_avail",
    #         kwargs={'slug': self.slug}
    #         )

    def get_friendly_name(self):
        return "{} {}.".format(
            self.base_account.user.first_name,
            self.base_account.user.last_name[0]
        )

    def get_address(self):
        return "{}\n{}, {} {}".format(
            self.street_address, 
            self.city, 
            self.state, 
            self.zip_code
        )

    def save(self, *args, **kwargs):
        super(StaffMember, self).save(*args, **kwargs)
        self.base_account.user.is_staff = True
        self.base_account.user.save()
        # services = Service.objects.all()
        # for service in services:
        #     service.save()
            # service.save_m2m()

    # def update_serv(self):
    #     services = Service.objects.all()
    #     for service in services:
    #         service.save()

def pre_save_staff(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.__str__())

pre_save.connect(pre_save_staff, sender=StaffMember)

# def post_save_staff(sender, instance, *args, **kwargs):
#     post_save.connect(post_save_staff, sender=StaffMember)

#     update_serv()

# #     print(hjkh)

# post_save.connect(post_save_staff, sender=StaffMember)
