import json

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class UserProfile(AbstractUser):
    GENDER_TYPE_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_TYPE_CHOICES, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)


class MarkerType(models.TextChoices):
    POP = 'POP', _('POP')
    CLIENT = 'CLIENT', _('Client')
    TJ_BOX = 'TJ_BOX', _('TJ BOX')
    RESELLER = 'RESELLER', _('Reseller')


class Marker(models.Model):
    identifier = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, choices=MarkerType.choices)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.type


class PopType(models.TextChoices):
    OLT = 'OLT', _('Olt')
    SWITCH = 'Switch', _('Switch')


class POP(models.Model):
    identifier = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    marker = models.OneToOneField(Marker, on_delete=models.CASCADE)
    pop_type = models.CharField(max_length=100, choices=PopType.choices)

    def __str__(self):
        return self.name


class TJBox(models.Model):
    identifier = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    marker = models.OneToOneField(Marker, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Client(models.Model):
    identifier = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    marker = models.OneToOneField(Marker, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Reseller(models.Model):
    identifier = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    marker = models.OneToOneField(Marker, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Cable(models.Model):
    identifier = models.CharField(max_length=100)
    type = models.CharField(max_length=100, null=True, blank=True)
    start_from = models.CharField(max_length=100, choices=MarkerType.choices)
    starting_point = models.ForeignKey(Marker, on_delete=models.CASCADE, related_name='starting_point')
    end_to = models.CharField(max_length=100, choices=MarkerType.choices)
    ending_point = models.ForeignKey(Marker, on_delete=models.CASCADE, related_name='ending_point')
    number_of_cores = models.IntegerField()
    length = models.FloatField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    polyline = models.TextField(null=True, blank=True)

    def set_polyline(self, data):
        self.polyline = json.dumps(data)

    def get_polyline(self):
        return json.loads(self.polyline)

    def __str__(self):
        return f'{self.identifier}'


class Core(models.Model):
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    cable = models.ForeignKey(Cable, on_delete=models.CASCADE, null=True, blank=True)
    core_number = models.IntegerField()
    color = models.CharField(max_length=100)
    assigned = models.BooleanField()
    splitter = models.ForeignKey("Gpon", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.marker.type} {self.cable} - {self.core_number}"


class Gpon(models.Model):
    tj_box = models.ForeignKey(TJBox, on_delete=models.CASCADE, null=True, blank=True)
    identifier = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    input_cable = models.ForeignKey(Cable, on_delete=models.CASCADE, null=True, blank=True)
    input_core = models.ForeignKey(Core, on_delete=models.CASCADE, related_name='input_core', null=True, blank=True)
    splitter = models.IntegerField()

    def __str__(self):
        return self.name


class Connection(models.Model):
    core_from = models.ForeignKey(Core, on_delete=models.CASCADE, related_name='core_from')
    core_to = models.ForeignKey(Core, on_delete=models.CASCADE, related_name='core_to')

    def __str__(self):
        return f"{self.core_from} - {self.core_to}"
