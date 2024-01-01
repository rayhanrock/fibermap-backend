from rest_framework import serializers

from .models import Marker, POP, Client, Junction, Gpon, Cable


class MarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ('id', 'type', 'latitude', 'longitude', 'address', 'notes', 'description')


class POPSerializer(serializers.ModelSerializer):
    marker = MarkerSerializer()

    class Meta:
        model = POP
        fields = ('id', 'identifier', 'name', 'marker')

    def create(self, validated_data):
        marker_data = validated_data.pop('marker')
        marker = Marker.objects.create(**marker_data)
        pop = POP.objects.create(marker=marker, **validated_data)
        return pop


class ClientSerializer(serializers.ModelSerializer):
    marker = MarkerSerializer()

    class Meta:
        model = Client
        fields = ('id', 'identifier', 'name', 'marker', 'mobile_number')

    def create(self, validated_data):
        print(self.get_initial().values())
        marker_data = validated_data.pop('marker')
        marker = Marker.objects.create(**marker_data)
        client = Client.objects.create(marker=marker, **validated_data)
        return client


class JunctionSerializer(serializers.ModelSerializer):
    marker = MarkerSerializer()

    class Meta:
        model = Junction
        fields = ('id', 'identifier', 'name', 'marker')

    def create(self, validated_data):
        marker_data = validated_data.pop('marker')
        marker = Marker.objects.create(**marker_data)
        junction = Junction.objects.create(marker=marker, **validated_data)
        return junction


class GponSerializer(serializers.ModelSerializer):
    marker = MarkerSerializer()

    class Meta:
        model = Gpon
        fields = ('id', 'identifier', 'name', 'marker', 'splitter')

    def create(self, validated_data):
        marker_data = validated_data.pop('marker')
        marker = Marker.objects.create(**marker_data)
        gpon = Gpon.objects.create(marker=marker, **validated_data)
        return gpon


class NetworkPOPSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source='marker.latitude')
    longitude = serializers.FloatField(source='marker.longitude')
    address = serializers.CharField(source='marker.address')

    class Meta:
        model = POP
        fields = ('identifier', 'name', 'latitude', 'longitude', 'address')


class NetworkJunctionSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source='marker.latitude')
    longitude = serializers.FloatField(source='marker.longitude')
    address = serializers.CharField(source='marker.address')

    class Meta:
        model = Junction
        fields = ('identifier', 'name', 'latitude', 'longitude', 'address')


class NetworkClientSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source='marker.latitude')
    longitude = serializers.FloatField(source='marker.longitude')
    address = serializers.CharField(source='marker.address')

    class Meta:
        model = Client
        fields = ('identifier', 'name', 'latitude', 'longitude', 'address')


class NetworkGponSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source='marker.latitude')
    longitude = serializers.FloatField(source='marker.longitude')
    address = serializers.CharField(source='marker.address')

    class Meta:
        model = Gpon
        fields = ('identifier', 'name', 'latitude', 'longitude', 'address')
