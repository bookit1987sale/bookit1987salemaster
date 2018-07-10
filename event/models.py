import datetime

import datetime

from django.db import models

from django.utils import timezone

from django.db.models.signals import pre_save, post_save
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from source_utils.starters import CommonInfo
from source_utils.re_usables import (
    get_actual_hours_and_minutes,
    hours_and_minutes_to_decimal_hours,
    meeting_iter,
    appt_time_conversion,
    hour_time_conversion,
    local_time_conversion,
    add_minutes,
    sub_minutes,
    time_format_no_zero
    )
# from source_utils.re_usables import time_format_no_zero
from consumer.models import ClientMember
from source_utils.time_selector import DAYS_OF_WEEK, select_time_options
from service.models import Service
from staffer.models import StaffMember
from consortium.models import Company, Hours


MOOD_OF_CLIENT = [
    ('Not Complete', 'Not Complete'),
    ('Very Pleased', 'Very Pleased'),
    ('Satisfied', 'Satisfied'),
    ('Dissatisfied', 'Dissatisfied'),
    ('Upset', 'Upset'),
    ('NA', 'N/A'),
]

EVENT_STATUS = [
    ('Not Complete', 'Not Complete'),
    ('Attended', 'Attended'),
    ('Cancelled', 'Cancelled'),
    ('No Show', 'No Show'),
]


class SecondPartEvent(models.Model):
    """ 
    This model represents a client's event 
    """
    client_service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='sec_part_client_service',
        blank=True
    )
    user_client = models.CharField(
        "Client",
        max_length=50,
        blank=True
    )
    staff = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='sec_part_staff_for_client_event',
        verbose_name=_("Staff Member"),
        blank=True
    )
    start = models.DateTimeField(
        _("start"),
        db_index=True
    )
    end = models.DateTimeField(
        _("end"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Second Part")
        verbose_name_plural = _("Second Parts")
        ordering = ["start",]

    def __str__(self):
        return "{}/{}-{} with {} 2nd Part".format(
            hour_time_conversion(self.start),
            hour_time_conversion(self.end),
            self.client_service.retail_service,
            self.user_client,
            # appt_time_conversion(self.start),
            # meeting_iter(self.meeting_number)
        )


class ClientEvent(CommonInfo):
    """ 
    This model represents a client's event 
    """
    client_service = models.ForeignKey(
        Service,
        limit_choices_to={'service_no_longer_available': False},
        on_delete=models.CASCADE,
        related_name='client_service'
    )
    user_client = models.ForeignKey(
        ClientMember,
        on_delete=models.CASCADE,
        related_name='user_client',
        verbose_name=_("Client Member"),
        blank=True,
        null=True
    )
    staff_client = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='staff_client',
        verbose_name=_("Staff Client"),
        blank=True,
        null=True
    )
    staff = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='staff_for_client_event',
        verbose_name=_("Staff Member"),
        blank=True
    )
    start = models.DateTimeField(
        _("start"),
        db_index=True
    )
    end = models.DateTimeField(
        _("end"),
        blank=True,
        null=True
    )
    second_event = models.ForeignKey(
        SecondPartEvent,
        on_delete=models.SET_NULL,
        related_name='staff_for_client_second_event',
        verbose_name=_("Second Part Event"),
        blank=True,
        null=True
    )
    client_mood = models.CharField(
        "client's mood",
        max_length=20,
        choices=MOOD_OF_CLIENT,
        default='Not Complete'
    )
    status = models.CharField(
        "appointment status",
        max_length=20,
        choices=EVENT_STATUS,
        default='Not Complete'
    )
    meeting_number = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        verbose_name = _("Client Event")
        verbose_name_plural = _("Client Events")
        ordering = ["start", "client_service"]

    def __str__(self):
        if self.user_client:
            client = self.user_client.__str__()
        else:
            client = self.staff_client.__str__()
        return "{} for {} on {} - {}".format(
            self.client_service.__str__(),
            self.user_client.__str__(),
            appt_time_conversion(self.start),
            meeting_iter(self.meeting_number)
        )

    def get_freindly_start(self):
        return hour_time_conversion(self.start)

    def get_freindly_times(self):
        return "{}/{} {}".format(
            hour_time_conversion(self.start).lstrip('0'),
            hour_time_conversion(self.end).lstrip('0'),
            self.end.strftime("%p, %A")
        )

    def get_staff(self):
        return self.staff.get_friendly_name()

    def get_service(self):
        return self.client_service.retail_service

    def get_client_iter(self):
        if self.user_client:
            return "{}({})".format(
                self.user_client.get_friendly_name(),
                meeting_iter(self.meeting_number)
            )
        else:
            return "{}({})".format(
                self.staff_client.get_friendly_name(),
                meeting_iter(self.meeting_number)
            )

    def get_event_title(self):
        if self.user_client:
            return "{}'s {} on {}".format(
                self.user_client.get_friendly_name(),
                self.get_service(),
                appt_time_conversion(self.start)
            )
        else:
            return "{}'s {} on {}".format(
                self.staff_client.get_friendly_name(),
                self.get_service(),
                appt_time_conversion(self.start)
            )

    def check_for_update(self):
        if self.client_mood == 'Not Complete' or self.status == 'Not Complete':
            if self.end < timezone.now():
                return True

    def get_success_url(self):
        return reverse(
            "event:my_event_list"
            )

    def get_absolute_url(self):
        return reverse(
            "event:event_update",
            kwargs={'pk': self.pk}
            )

    def get_client_absolute_url(self):
        if self.user_client:
            return reverse(
                "consumer:client_detail",
                kwargs={'slug': self.user_client.slug}
                )
        else:
            return reverse(
                "staff:staff_update",
                kwargs={'pk': self.staff_client.pk}
                )


def pre_save_client_event(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.__str__())
    this_client = instance.user_client.__str__()
    if instance.staff_client:
        this_client = instance.staff_client.__str__()
    if instance.client_service.overlap_minutes:
        instance.end = add_minutes(
            instance.start,
            instance.client_service.overlap_from
            )
        if not instance.second_event:
            second_part = SecondPartEvent(
                client_service=instance.client_service,
                user_client=this_client,
                staff=instance.staff,
                start=add_minutes(
                    instance.start,
                    (instance.client_service.overlap_from + instance.client_service.overlap_minutes)
                    ),
                end=add_minutes(
                    instance.start,
                    instance.client_service.minutes
                    )
                )
            second_part.save()
            instance.second_event = second_part
        else:
            instance.second_event.start = add_minutes(
                instance.start,
                (instance.client_service.overlap_from + instance.client_service.overlap_minutes)
            )
            instance.second_event.end = add_minutes(
                instance.start,
                instance.client_service.minutes
            )
            instance.second_event.user_client = this_client
            instance.second_event.client_service = instance.client_service
            instance.second_event.staff = instance.staff
            instance.second_event.save()
    else: 
        instance.end = add_minutes(
            instance.start,
            instance.client_service.minutes
            )
    try:
        latest = ClientEvent.objects.filter(
            user_client=instance.user_client
            ).latest('pk')
        if latest.status == 'Attended' and instance.pk != latest.pk:
            instance.meeting_number = latest.meeting_number + 1
        else:
            instance.meeting_number = latest.meeting_number
    except:
        pass

pre_save.connect(pre_save_client_event, sender=ClientEvent)

def post_save_client_event(sender, instance, *args, **kwargs):
    if instance.status == "Cancelled":
        if instance.second_event:
            instance.second_event.delete()

post_save.connect(post_save_client_event, sender=ClientEvent)


# def post_save_client_event(sender, instance, *args, **kwargs):
#     instance.slug = slugify(instance.__str__())
#     second_event = 'none'

#     try:
#         second_slug = "{}-2nd-part".format(
#             instance.slug
#             )
#         # second_slug = slugify(second_slug)
#         # print(second_slug)
#         second_event = get_object_or_404(ClientEvent, slug=second_slug) #ClientEvent.objects.get(slug=second_slug)
#         print(second_event, " oooo")
#     except:
#         print("doesnt exist")
#         pass
#     if instance.client_service.overlap_minutes and not instance.second_part and second_event == 'none':
#         second_part = ClientEvent(
#             client_service=instance.client_service,
#             user_client=instance.user_client,
#             staff=instance.staff,
#             start=add_minutes(
#                 instance.start,
#                 (instance.client_service.overlap_from + instance.client_service.overlap_minutes)
#                 ),
#             end=add_minutes(
#                 instance.start,
#                 instance.client_service.minutes
#                 ),
#             second_part=True,
#             meeting_number=instance.meeting_number
#             )
#         second_part.save()

# post_save.connect(post_save_client_event, sender=ClientEvent)

# overlap_from overlap_minutes


class StaffActivityType(CommonInfo):
    """ 
    This model represents a staff member's type of activity 
    """
    activity = models.CharField(
        _('Staff Activity'),
        max_length=20
    )
    work_related = models.BooleanField(
        default=False
    )
    no_longer_available = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.activity

def pre_save_staff_activity(sender, instance, *args, **kwargs):

    instance.slug = slugify(instance.activity)

pre_save.connect(pre_save_staff_activity, sender=StaffActivityType)


class StaffEvent(models.Model):
    """ 
    This model represents a staff member's activity event 
    """
    staff_activity = models.ForeignKey(
        StaffActivityType,
        on_delete=models.CASCADE,
        related_name='staff_activity',
        verbose_name=_("Staff Activity Options")
    )
    staff = models.ForeignKey(
        StaffMember, 
        on_delete=models.CASCADE,
        related_name='staff_for_staff_event',
        verbose_name=_("Staff Member")
    )
    start = models.DateTimeField(
        _("start"),
        db_index=True
    )
    end = models.DateTimeField(
        _("end"),
        blank=True,
        null=True
    )
    confirmed = models.BooleanField(
        default=False
    )
    cancelled = models.BooleanField(
        "I'm cancelling this request",
        default=False
    )
    all_day = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = _("Staff Event")
        verbose_name_plural = _("Staff Events")
        ordering = ["start", "staff_activity"]

    def __str__(self):
        return "{} for {} {} until {}".format(
            self.staff_activity,
            self.staff.__str__(),
            appt_time_conversion(self.start),
            appt_time_conversion(self.end)
        )

    def get_my_request(self):
        return "{} until {}".format(
            appt_time_conversion(self.start),
            appt_time_conversion(self.end)
        )

    def get_absolute_url(self):
        return reverse('event:staff_event_update', kwargs = {'pk' : self.pk})

def pre_save_staff_event(sender, instance, *args, **kwargs):
    slug = "{}".format(instance.__str__())
    instance.slug = slugify(slug)

pre_save.connect(pre_save_staff_event, sender=StaffEvent)


# def company_details():
#     company = Company.objects.get(pk=1)
#     time_step = company.work_step
#     hours = Hours.objects.all()
#     return {'time_step':time_step, 'hours':hours}


# class AvailabilityForDay(CommonInfo):
#     """ 
#     This model represents a staff member's availability for the day 
#     """
#     staff_member = models.ForeignKey(
#         StaffMember,
#         on_delete=models.CASCADE,
#         related_name='member_availabilityiii',
#         verbose_name=_("Staff Member")
#     )
#     day = models.CharField(
#         _('Day of the week'),
#         max_length=15
#     )
#     scheduled_start = models.CharField(
#         _("start time of day"),
#         max_length=15
#     )
#     scheduled_end = models.CharField(
#         _("end time of day"),
#         max_length=15
#     )
  
#     class Meta:
#         verbose_name = _("Staff's Scheduled Hours For Day Of The Week")
#         verbose_name_plural = _("Staff's Scheduled Hours For Days Of The Week")
#         ordering = ["day", "staff_member"]
#         unique_together = ("staff_member", "day")

#     def convert_time(self, time):
#         return time

#     # def calculate_hours(self):
#     #     start, end = [datetime.datetime.strptime(x, "%H:%M:%S") for x in [str(self.scheduled_start), str(self.scheduled_end)]]
#     #     time = end - start
#     #     return time

#     def __str__(self):
#         return "{} - {}: {} to {}".format(
#             self.day,
#             self.staff_member,
#             self.scheduled_start, 
#             self.scheduled_end
#         )

#     def get_absolute_url(self):
#         return reverse(
#             "event:my_avail_update",
#             kwargs={'pk': self.pk}
#             )

#     def convert_times(self):
#         return "{} to {}".format(
#             time_format_no_zero(self.start),
#             time_format_no_zero(self.end)
#             )

#     def display_schedule(self):
#         return "{} - {} until {}".format(
#             self.day,
#             self.scheduled_start,
#             self.scheduled_end
#         )

#     # def company_details(self):
#     #     return Company.object(pk=1)

#     # def get_absolute_url(self):
#     #     return reverse('time_log:staff_avail_update', kwargs = {'pk' : self.pk})


# def pre_save_staff_avail_for_day(sender, instance, *args, **kwargs):
#     # slug = "{} {}".format(instance.staff.username, instance.day)
#     instance.slug = slugify(instance.__str__())

# pre_save.connect(pre_save_staff_avail_for_day, sender=AvailabilityForDay)

