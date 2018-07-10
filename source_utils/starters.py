from django.db import models

from source_utils.states import state_choices
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from versatileimagefield.fields import (
    VersatileImageField, 
    PPOIField
)


class CommonInfo(models.Model):
    slug = models.SlugField(max_length=150, blank=True)
    origin = models.DateTimeField(auto_now_add=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class Conflict(CommonInfo):
    conflict_description = models.CharField(
        "Conflict description", 
        max_length=300
    )
    conflict_resolution = models.CharField(
        "Conflict resolution",
        null=True, 
        blank=True, 
        max_length=300
    )

    class Meta:
        abstract = True


class CommonAccountDetails(CommonInfo):

    class Meta:
        abstract = True

    STATE_CHOICES = state_choices

    # first_name = models.CharField(_('first name'), max_length=30, null=True, 
    #     blank=True)
    # last_name = models.CharField(_('last name'), max_length=30, null=True, 
    #     blank=True)
    initial_password = models.CharField(max_length=40, null=True, blank=True)
    spouse_name = models.CharField(_('significant other'), max_length=30, null=True, 
        blank=True)
    street_address = models.CharField(verbose_name=_('address'), max_length=100,
        null=True, blank=True)
    city = models.CharField(verbose_name=_('city'), max_length=100,
        null=True, blank=True)
    state = models.CharField(verbose_name=_('state'), max_length=40,
        choices=STATE_CHOICES, null=True, blank=True)
    zip_code = models.IntegerField(verbose_name=_('zip code'), null=True, blank=True)
    # main_phone = PhoneNumberField(verbose_name=_('main phone'), max_length=15, 
    #     blank=True)
    # alt_phone = PhoneNumberField(verbose_name=_('alternate phone (not required)'), 
    #     max_length=15, null=True, blank=True)
    image = VersatileImageField(
        'Image',
        upload_to='images/staff/',
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


class GenericCategory(models.Model):
    """ 
    This model represents a general type of base category offered. 
    """
    slug = models.SlugField(max_length=100, blank=True)
    category = models.CharField(
        max_length=30, 
        unique=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.category
