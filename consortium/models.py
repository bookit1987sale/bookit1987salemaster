from datetime import datetime

from django.db import models

from source_utils.states import state_choices
from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from source_utils.starters import CommonInfo
from staff_sced.models import AvailabilityForDay
from source_utils.re_usables import time_format_no_zero
from source_utils.time_selector import (
    DAYS_OF_WEEK,
    select_time_options
    )

from versatileimagefield.fields import (
    VersatileImageField, 
    PPOIField
)


class Company(CommonInfo):
    """ 
    This model represents the company that provides product. 
    """
    company = models.CharField(
        max_length=30, 
        unique=True
    )
    company_phone = models.CharField(
        max_length=30
    )
    email = models.EmailField(
        _('contact email address')
    )
    owner = models.CharField(
        _('company owner'),
        max_length=30,
        null=True, 
        blank=True
    )
    street_address = models.CharField(
        verbose_name=_('street'),
        max_length=100
    )
    city = models.CharField(
        verbose_name=_('city'),
        max_length=100
    )
    state = models.CharField(
        verbose_name=_('state'),
        max_length=40,
        choices=state_choices,
        default='PA'
    )
    zip_code = models.IntegerField(
        verbose_name=_('zip code')
    )
    caption = models.CharField(
        _('caption'),
        max_length=500,
        null=True,
        blank=True
    )
    bio = models.TextField(
        _('company bio'),
        max_length=4000,
        null=True,
        blank=True
    )
    alert = models.TextField(
        _('company alert'),
        max_length=4000,
        null=True,
        blank=True
    )
    appt_step = models.PositiveIntegerField(
        'Appointment Select Options Time Step',
        default=30
    )
    work_step = models.PositiveIntegerField(
        'Schedule for Day Time Step',
        default=30
    )
    logo = VersatileImageField(
        'Image',
        upload_to='images/company/',
        null=True, blank=True,
        width_field='width',
        height_field='height',
        ppoi_field='ppoi'
    )
    height = models.PositiveIntegerField(
        'Image Height',
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        'Image Width',
        blank=True,
        null=True
    )
    ppoi = PPOIField(
        'Image PPOI'
    )

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Company')
        ordering = ["company"]

    def __str__(self):
        return "{}".format(
        self.company
    )

    # def get_success_url(self):
    #     return reverse("company:company_list")

    # def get_absolute_url(self):
    #     return reverse("company:company_detail", kwargs={'slug': self.slug})


def pre_save_company(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.__str__())
pre_save.connect(pre_save_company, sender=Company)


class Holidays(models.Model):
    """ 
    This model represents the company that provides product. 
    """
    slug = models.SlugField(max_length=150, blank=True)
    name = models.CharField(
        max_length=40
    )
    day = models.DateField()
    can_work = models.BooleanField(
        _("Overtime Optional"),
        default=False
    )
  
    class Meta:
        verbose_name = _("Company Holiday")
        verbose_name_plural = _("Company Holidays")
        ordering = ["day",]
        # unique_together = ("staff_member", "day")

    # def convert_times(self):
    #     return "{} to {}".format(
    #         time_format_no_zero(self.start),
    #         time_format_no_zero(self.end)
    #         )

    # def calculate_hours(self):
    #     start, end = [datetime.datetime.strptime(x, "%H:%M:%S") for x in [str(self.scheduled_start), str(self.scheduled_end)]]
    #     time = end - start
    #     return time

    # def __str__(self):
    #     return self.day

    # def get_absolute_url(self):
    #     return reverse(
    #         "consortium:get_day",
    #         kwargs={'pk': self.pk}
    #         )

    # def display_schedule(self):
    #     return "{} until {}".format(
    #         self.start,
    #         self.end
    #     )


def pre_save_holiday(sender, instance, *args, **kwargs):
    slug = "{} hours".format(instance.day, instance.day)
    instance.slug = slugify(slug)

pre_save.connect(pre_save_holiday, sender=Holidays)


class Hours(models.Model):
    """ 
    This model represents the company that provides product. 
    """
    slug = models.SlugField(max_length=150, blank=True)
    day = models.CharField(
        _('Day of the week'),
        max_length=15, 
        choices=DAYS_OF_WEEK,
        default=DAYS_OF_WEEK[0][0],
        unique=True
    )
    start = models.CharField(
        _("start time of day"),
        max_length=15
        # choices=select_time_options(
        #     company = {
        #         'start':'12:00 AM',
        #         'end':'11:45 PM',
        #         'step':15}, 
        #         option=1
        #     )
    )
    end = models.CharField(
        _("end time of day"),
        max_length=15
        # choices=select_time_options(
        #     company = {
        #         'start':'12:00 AM',
        #         'end':'11:45 PM',
        #         'step':15}
        #     )
    )
    closed = models.BooleanField(
        _("Closed on this day"),
        default=False
    )
  
    class Meta:
        verbose_name = _("Company Hours For Day Of The Week")
        verbose_name_plural = _("Company Hours For Days Of The Week")
        ordering = ["day",]
        # unique_together = ("staff_member", "day")

    # def convert_times(self):
    #     return "{} to {}".format(
    #         time_format_no_zero(self.start),
    #         time_format_no_zero(self.end)
    #         )

    # def calculate_hours(self):
    #     start, end = [datetime.datetime.strptime(x, "%H:%M:%S") for x in [str(self.scheduled_start), str(self.scheduled_end)]]
    #     time = end - start
    #     return time

    def __str__(self):
        return self.day

    def get_absolute_url(self):
        return reverse(
            "consortium:get_day",
            kwargs={'pk': self.pk}
            )

    def display_schedule(self):
        return "{} until {}".format(
            self.start,
            self.end
        )


def pre_save_hours_for_day(sender, instance, *args, **kwargs):
    slug = "{} hours".format(instance.day, instance.day)
    instance.slug = slugify(slug)
    if instance.closed:
        same_day_events = AvailabilityForDay.objects.filter(day=instance.day).delete()

pre_save.connect(pre_save_hours_for_day, sender=Hours)
