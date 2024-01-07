import json

from django.db import models
from django.utils.translation import gettext_lazy as _


class MarkerType(models.TextChoices):
    POP = 'POP', _('POP')
    CLIENT = 'CLIENT', _('Client')
    JUNCTION = 'JUNCTION', _('Junction')
    GPON = 'GPON', _('Gpon')


class Marker(models.Model):
    identifier = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, choices=MarkerType.choices)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.type


class POP(models.Model):
    identifier = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    marker = models.OneToOneField(Marker, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Junction(models.Model):
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


class Cable(models.Model):
    identifier = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    start_from = models.CharField(max_length=100, choices=MarkerType.choices)
    starting_point = models.ForeignKey(Marker, on_delete=models.DO_NOTHING, related_name='starting_point')
    end_to = models.CharField(max_length=100, choices=MarkerType.choices)
    ending_point = models.ForeignKey(Marker, on_delete=models.DO_NOTHING, related_name='ending_point')
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
        return self.identifier


class Core(models.Model):
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    cable = models.ForeignKey(Cable, on_delete=models.CASCADE, null=True, blank=True)
    core_number = models.IntegerField()
    color = models.CharField(max_length=100)
    assigned = models.BooleanField()
    connected_cores = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return f"{self.marker.type} {self.cable} - {self.core_number}"


class Gpon(models.Model):
    identifier = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    marker = models.OneToOneField(Marker, on_delete=models.CASCADE)
    input_cable = models.ForeignKey(Cable, on_delete=models.CASCADE, null=True, blank=True)
    input_core = models.ForeignKey(Core, on_delete=models.CASCADE, related_name='input_core', null=True, blank=True)
    output_cores = models.ManyToManyField(Core, related_name='output_cores', blank=True)
    splitter = models.IntegerField()

    def __str__(self):
        return self.name


class Connection(models.Model):
    core_from = models.ForeignKey(Core, on_delete=models.CASCADE, related_name='core_from')
    core_to = models.ForeignKey(Core, on_delete=models.CASCADE, related_name='core_to')
