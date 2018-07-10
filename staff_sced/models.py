from django.db import models

from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from source_utils.starters import CommonInfo
from source_utils.re_usables import (
    time_format_no_zero
    )
from staffer.models import StaffMember


class AvailabilityForDay(CommonInfo):
    """ 
    This model represents a staff member's availability for the day 
    """
    staff_member = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='member_availability',
        verbose_name=_("Staff Member")
    )
    day = models.CharField(
        _('Day of the week'),
        max_length=15
    )
    scheduled_start = models.CharField(
        _("start time of day"),
        max_length=15,
        null=True, 
        blank=True
    )
    scheduled_end = models.CharField(
        _("end time of day"),
        max_length=15,
        null=True, 
        blank=True
    )
    not_avail = models.BooleanField(
        _("Not available on this day"),
        default=False
    )
  
    class Meta:
        verbose_name = _("Staff's Scheduled Hours For Day Of The Week")
        verbose_name_plural = _("Staff's Scheduled Hours For Days Of The Week")
        ordering = ["day", "staff_member"]
        unique_together = ("staff_member", "day")

    def convert_time(self, time):
        return time

    # def calculate_hours(self):
    #     start, end = [datetime.datetime.strptime(x, "%H:%M:%S") for x in [str(self.scheduled_start), str(self.scheduled_end)]]
    #     time = end - start
    #     return time

    def __str__(self):
        return "{} - {}: {} to {}".format(
            self.day,
            self.staff_member,
            self.scheduled_start, 
            self.scheduled_end
        )

    def get_absolute_url(self):
        # print(self.pk, " self.pk")
        return reverse(
            "staff_sced:my_avail_update",
            kwargs={'pk': self.pk}
            )

    def convert_times(self):
        return "{} to {}".format(
            time_format_no_zero(self.start),
            time_format_no_zero(self.end)
            )

    def display_schedule(self):
        return "{} - {} until {}".format(
            self.day,
            self.scheduled_start,
            self.scheduled_end
        )

    # def company_details(self):
    #     return Company.object(pk=1)

    # def get_absolute_url(self):
    #     return reverse('time_log:staff_avail_update', kwargs = {'pk' : self.pk})


def pre_save_staff_avail_for_day(sender, instance, *args, **kwargs):
    # slug = "{} {}".format(instance.staff.username, instance.day)
    instance.slug = slugify(instance.__str__())

pre_save.connect(pre_save_staff_avail_for_day, sender=AvailabilityForDay)
