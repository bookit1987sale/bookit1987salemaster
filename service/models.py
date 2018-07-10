from __future__ import unicode_literals

from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_save, post_save
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from source_utils.starters import CommonInfo, GenericCategory
# from staffer.models import StaffMember

UNIT_TYPE = (
        ('minute', 'Minute'),
        # ('hour', 'Hour'),
        ('occurence', 'Occurence'),
)

class ServiceBasics(models.Model):
    """ 
    This model represents the general type of service category offered. 
    """
    slug = models.SlugField(max_length=100, blank=True)
    # unit_type = models.CharField(
    #     max_length=40, 
    #     choices=UNIT_TYPE,
    #     default=UNIT_TYPE[0][0]
    # )
    minutes = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    cost = models.DecimalField(
        'Cost per Unit',
        validators=[MinValueValidator(0)],
        max_digits=5,
        decimal_places=2
    )
    service_no_longer_available = models.BooleanField(
        default=False
    )

    class Meta:
        abstract = True


class Branch(ServiceBasics):
    """ 
    This model represents the specific type of general service category offered. 
    """
    service_branch_description = models.CharField(
        'service branch description',
        max_length=130, 
        unique=True
    )

    class Meta:
        verbose_name = _('Service Branch Description')
        verbose_name_plural = _('Service Branch Description')
        ordering = ["service_branch_description"]

    def get_cat_cost(self):
        return self.minutes * self.cost

    def __str__(self):
        return "{}".format(
            self.service_branch_description
    )


def pre_save_branch(sender, instance, *args, **kwargs):

    instance.slug = slugify(instance.service_branch_description)

pre_save.connect(pre_save_branch, sender=Branch)


class Service(ServiceBasics):
    """ This model describes a specific service. """

    service_branch = models.ForeignKey(
        Branch,
        verbose_name = 'Service Type',
        related_name='service_branch',
        on_delete=models.CASCADE
    )
    retail_service = models.CharField(
        'service description',
        max_length=130, 
        unique=True
    )
    overlap_from = models.PositiveIntegerField(
        'minutes from start for the start of overlap',
        default=0,
        blank=True
    )
    overlap_minutes = models.PositiveIntegerField(
        'overlap duration in minutes',
        default=0,
        blank=True
    )
    popular = models.BooleanField(
        default=False
    )
    staff_trained_for = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = _('Retail Service')
        verbose_name_plural = _('Retail Services')
        ordering= ['service_branch', 'retail_service']

    def __str__(self):
        return self.retail_service

    def get_short_description(self):
        return self.retail_service

    def get_long_description(self):
        return "{} - ({})".format(
            self.retail_service,
            self.service_branch.service_branch_description,
        )

    def get_service_and_cost(self):
        return "{} ${}".format(
            self.retail_service,
            self.get_tot_service_cost(),
        )

    # def get_staff_list(self):
    #     return StaffMember.objects.filter(base_account__user__is_active=true)

    def get_tot_service_cost(self):
        accum_costs = self.service_branch.get_cat_cost() + (self.minutes * self.cost)
        return f'{accum_costs:.2f}'
     
def pre_save_service(sender, instance, *args, **kwargs):
    if not instance.overlap_from:
        instance.overlap = 0
    slug = "{}-{}".format(
        instance.retail_service,
        instance.service_branch.service_branch_description
        )
    instance.slug = slugify(slug)
    avail_staff = instance.staff_skills.filter(base_account__user__is_active=True)
    if not avail_staff:
        instance.staff_trained_for = False
    else:
        instance.staff_trained_for = True
pre_save.connect(pre_save_service, sender=Service)

