from __future__ import unicode_literals
import datetime
import uuid

from django.db import models
from django.dispatch import receiver

# these will determine the default formality of correspondence
ALLOWED_TYPES = [
    ('ecuador', 'ecuador'),
    ('scotland', 'scotland'),
    ('both', 'both'),
]


def _random_uuid():
    return uuid.uuid4().hex


class Party(models.Model):
    """
    A party consists of one or more guests.
    """
    name = models.TextField()
    type = models.CharField(max_length=10, choices=ALLOWED_TYPES)
    category = models.CharField(max_length=20, null=True, blank=True)
    save_the_date_sent = models.DateTimeField(null=True, blank=True, default=None)
    save_the_date_opened = models.DateTimeField(null=True, blank=True, default=None)
    invitation_id = models.CharField(max_length=32, db_index=True, default=_random_uuid, unique=True)
    invitation_sent = models.DateTimeField(null=True, blank=True, default=None)
    invitation_opened = models.DateTimeField(null=True, blank=True, default=None)
    is_invited = models.BooleanField(default=True)
    rehearsal_dinner = models.BooleanField(default=False)
    allow_plus_one = models.BooleanField(default=False)
    is_attending = models.NullBooleanField(default=None)
    comments = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return 'Party: {}'.format(self.name)

    def __str__(self):
        return 'Party: {}'.format(self.name)

    @classmethod
    def in_default_order(cls):
        return cls.objects.order_by('category', '-is_invited', 'name')

    @property
    def ordered_guests(self):
        return self.guest_set.order_by('is_child', 'pk')

    @property
    def any_guests_attending(self):
        return any(self.guest_set.values_list('is_attending', flat=True))

    @property
    def guest_emails(self):
        return self.guest_set.exclude(email='').values_list('email', flat=True)


MEALS = [
    ('any', 'any/cualquiera'),
    ('dairy_free', 'dairy free/sin lactosa'),
    ('vegetarian', 'vegetarian'),
    ('vegan', 'vegan'),
]


class Guest(models.Model):
    """
    A single guest
    """
    party = models.ForeignKey(Party, on_delete=models.PROTECT)
    first_name = models.TextField()
    last_name = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    is_attending = models.NullBooleanField(default=None)
    meal = models.CharField(max_length=20, choices=MEALS, null=True, blank=True)
    is_child = models.BooleanField(default=False)

    @property
    def name(self):
        return u'{} {}'.format(self.first_name, self.last_name)

    @property
    def unique_id(self):
        # convert to string so it can be used in the "add" templatetag
        return str(self.pk)

    def __unicode__(self):
        return 'Guest: {} {}'.format(self.first_name, self.last_name)

    def __str__(self):
        return 'Guest: {} {}'.format(self.first_name, self.last_name)


class Event(models.Model):
    """
    There are two events
    """

    name = models.TextField()
    date = models.DateTimeField(null=True, blank=True, default=None)
    type = models.CharField(max_length=10, choices=ALLOWED_TYPES, default='scotland')

    def __unicode__(self):
        return 'Event: {}'.format(self.name)

    def __str__(self):
        return 'Event: {}'.format(self.name)

class Invitation(models.Model):
    """
    An invitation per party per event
    """

    party = models.ForeignKey(Party, on_delete=models.PROTECT)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    save_the_date_sent = models.DateTimeField(null=True, blank=True, default=None)
    save_the_date_opened = models.DateTimeField(null=True, blank=True, default=None)
    invitation_id = models.CharField(max_length=32, db_index=True, default=_random_uuid, unique=True)
    invitation_sent = models.DateTimeField(null=True, blank=True, default=None)
    invitation_opened = models.DateTimeField(null=True, blank=True, default=None)

    @property
    def name(self):
        return u'{} {}'.format(self.party.name, self.event.name)

    def __unicode__(self):
        return 'Invitation: {} {}'.format(self.party.name, self.event.name)

    def __str__(self):
        return 'Invitation: {} {}'.format(self.party.name, self.event.name)


class RSVP(models.Model):
    """
    The reply for each event for each guest
    """

    guest = models.ForeignKey(Guest, on_delete=models.PROTECT)
    invitation = models.ForeignKey(Invitation, on_delete=models.PROTECT)
    event = models.ForeignKey(Event, on_delete=models.PROTECT, default=None)
    date_of_reply  = models.DateTimeField(null=True, blank=True, default=None)
    is_attending = models.NullBooleanField(default=None)
    meal = models.CharField(max_length=20, choices=MEALS, null=True, blank=True)

    def __unicode__(self):
        return 'RSVP: {} {}'.format(self.guest.name, self.invitation.name, self.event.name)

    def __str__(self):
        return 'RSVP: {} {}'.format(self.guest.name, self.invitation.name, self.event.name)