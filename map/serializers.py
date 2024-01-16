import json
from json import JSONEncoder

from .utility import find_core_paths

from rest_framework import serializers

from .models import Marker, POP, Client, Junction, Gpon, Cable, Core, Connection


class MarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ('id', 'type', 'latitude', 'longitude', 'address', 'notes', 'description')


class BasicMarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ('identifier', 'type',)


class POPCreateSerializer(serializers.ModelSerializer):
    marker = MarkerSerializer()

    class Meta:
        model = POP
        fields = ('id', 'identifier', 'name', 'marker')

    def create(self, validated_data):
        marker_data = validated_data.pop('marker')
        marker = Marker.objects.create(**marker_data)
        marker.identifier = validated_data['name']
        marker.save()
        pop = POP.objects.create(marker=marker, **validated_data)
        return pop


class POPListSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source='marker.latitude')
    longitude = serializers.FloatField(source='marker.longitude')
    address = serializers.CharField(source='marker.address')

    class Meta:
        model = POP
        fields = ('id', 'identifier', 'name', 'latitude', 'longitude', 'address')


class ClientCreateSerializer(serializers.ModelSerializer):
    marker = MarkerSerializer()

    class Meta:
        model = Client
        fields = ('id', 'identifier', 'name', 'marker', 'mobile_number')

    def create(self, validated_data):
        marker_data = validated_data.pop('marker')
        marker = Marker.objects.create(**marker_data)
        marker.identifier = validated_data['name']
        marker.save()
        client = Client.objects.create(marker=marker, **validated_data)
        return client


class ClientListSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source='marker.latitude')
    longitude = serializers.FloatField(source='marker.longitude')
    address = serializers.CharField(source='marker.address')

    class Meta:
        model = Client
        fields = ('id', 'identifier', 'name', 'latitude', 'longitude', 'address')


class JunctionCreateSerializer(serializers.ModelSerializer):
    marker = MarkerSerializer()

    class Meta:
        model = Junction
        fields = ('id', 'identifier', 'name', 'marker')

    def create(self, validated_data):
        marker_data = validated_data.pop('marker')
        marker = Marker.objects.create(**marker_data)
        marker.identifier = validated_data['name']
        marker.save()
        junction = Junction.objects.create(marker=marker, **validated_data)
        return junction


class JunctionListSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source='marker.latitude')
    longitude = serializers.FloatField(source='marker.longitude')
    address = serializers.CharField(source='marker.address')

    class Meta:
        model = Junction
        fields = ('id', 'identifier', 'name', 'latitude', 'longitude', 'address')


class GponCreateSerializer(serializers.ModelSerializer):
    marker = MarkerSerializer()

    class Meta:
        model = Gpon
        fields = ('id', 'identifier', 'name', 'marker', 'splitter')

    def create(self, validated_data):
        marker_data = validated_data.pop('marker')
        marker = Marker.objects.create(**marker_data)
        marker.identifier = validated_data['name']
        marker.save()

        splitter = validated_data['splitter']
        input_core = Core.objects.create(marker=marker, core_number=0, assigned=False, color='gpon_color')
        gpon = Gpon.objects.create(marker=marker, input_core=input_core, **validated_data)
        for i in range(1, splitter + 1):
            obj = Core.objects.create(marker=marker, core_number=i, assigned=False, color='gpon_color')
            Connection.objects.create(core_from=obj, core_to=input_core)
        return gpon


class GponListSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(source='marker.latitude')
    longitude = serializers.FloatField(source='marker.longitude')
    address = serializers.CharField(source='marker.address')

    class Meta:
        model = Gpon
        fields = ('id', 'identifier', 'name', 'latitude', 'longitude', 'address')


class CableCreateSerializer(serializers.ModelSerializer):
    polyline = serializers.JSONField()

    class Meta:
        model = Cable
        fields = (
            'id', 'identifier', 'type', 'start_from', 'starting_point', 'end_to', 'ending_point', 'number_of_cores',
            'length', 'notes', 'description', 'polyline',)

    def to_internal_value(self, data):
        choices = {
            'POP': POP,
            'CLIENT': Client,
            'JUNCTION': Junction,
            'GPON': Gpon
        }
        start_form = data['start_from']
        start_form_type = choices[start_form]
        starting_point = start_form_type.objects.get(id=data['starting_point']).marker.id
        data['starting_point'] = starting_point

        end_to = data['end_to']
        end_to_type = choices[end_to]
        ending_point = end_to_type.objects.get(id=data['ending_point']).marker.id
        data['ending_point'] = ending_point

        return super().to_internal_value(data)

    def create(self, validated_data):
        polyline = validated_data['polyline']
        starting_point = validated_data['starting_point']
        ending_point = validated_data['ending_point']

        start_position = {
            "lat": starting_point.latitude,
            "lng": starting_point.longitude
        }

        end_position = {
            "lat": ending_point.latitude,
            "lng": ending_point.longitude
        }

        first_point = polyline.pop(0)
        polyline.insert(0, start_position)
        # Remove and insert the last element
        last_point = polyline.pop()
        polyline.append(end_position)

        num_of_core = validated_data['number_of_cores']
        # Serialize array before creating the model instance
        validated_data['polyline'] = json.dumps(polyline)
        print(validated_data)
        instance = super().create(validated_data)

        for i in range(1, num_of_core + 1):
            start_marker_side = Core.objects.create(
                marker=starting_point,
                cable=instance,
                core_number=i,
                color='red',
                assigned=False
            )
            end_marker_side = Core.objects.create(
                marker=ending_point,
                cable=instance,
                core_number=i,
                color='red',
                assigned=False
            )
            # start_marker_side.connected_cores.add(end_marker_side)
            Connection.objects.create(core_from=start_marker_side, core_to=end_marker_side)
            Connection.objects.create(core_from=end_marker_side, core_to=start_marker_side)

        return instance


class CableListSerializer(serializers.ModelSerializer):
    polyline = serializers.SerializerMethodField()

    class Meta:
        model = Cable
        fields = ('id', 'identifier', 'type', 'number_of_cores', 'length', 'polyline')

    def get_polyline(self, obj):
        return obj.get_polyline()


class ClientCoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Core
        fields = ['id', 'core_number', 'color', 'assigned', ]


class PopCoreSerializer(serializers.ModelSerializer):
    connected_to = serializers.SerializerMethodField()

    class Meta:
        model = Core
        fields = ['id', 'core_number', 'color', 'assigned', 'connected_to', ]

    def get_connected_to(self, obj):
        connection = Connection.objects.filter(core_from=obj)
        for conn in connection:
            if conn.core_from.cable != conn.core_to.cable:
                return {'id': conn.core_to.id}
        return None


class JunctionCoreSerializer(serializers.ModelSerializer):
    last_point = serializers.SerializerMethodField()
    connected_to = serializers.SerializerMethodField()

    class Meta:
        model = Core
        fields = ['id', 'core_number', 'color', 'assigned', 'connected_to', 'last_point']

    def get_last_point(self, obj):
        last_connected_marker = find_core_paths(obj).pop().marker
        data = BasicMarkerSerializer(last_connected_marker).data
        return data

    def get_connected_to(self, obj):
        connection = Connection.objects.filter(core_from=obj)
        for conn in connection:
            if conn.core_from.cable != conn.core_to.cable:
                return {'id': conn.core_to.id}
        return None


class GponInputCableCoreSerializer(serializers.ModelSerializer):
    last_point = serializers.SerializerMethodField()

    class Meta:
        model = Core
        fields = ['id', 'core_number', 'color', 'assigned', 'last_point']

    def get_last_point(self, obj):
        last_connected_marker = find_core_paths(obj).pop().marker
        data = BasicMarkerSerializer(last_connected_marker).data
        return data


class GponOutCoreSerializer(serializers.ModelSerializer):
    connected_to = serializers.SerializerMethodField()

    class Meta:
        model = Core
        fields = ['id', 'core_number', 'connected_to']

    def get_connected_to(self, obj):
        connection = Connection.objects.filter(core_from=obj)
        for conn in connection:
            print(conn)
            if conn.core_to.cable is not None:
                return {'id': conn.core_to.id}
        return None


class GponOutputCableCoreSerializer(serializers.ModelSerializer):
    last_point = serializers.SerializerMethodField()
    connected_to = serializers.SerializerMethodField()

    class Meta:
        model = Core
        fields = ['id', 'core_number', 'color', 'connected_to', 'last_point']

    def get_last_point(self, obj):
        last_connected_marker = find_core_paths(obj).pop().marker
        data = BasicMarkerSerializer(last_connected_marker).data
        return data

    def get_connected_to(self, obj):
        connection = Connection.objects.filter(core_from=obj)
        for conn in connection:
            if conn.core_to.cable is None:
                return {'id': conn.core_to.id}
        return None


class CoreAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Core
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.assigned = validated_data['assigned']
        instance.save()
        return instance


class CableSerializer(serializers.ModelSerializer):
    cores = ClientCoreSerializer(many=True, read_only=True)

    class Meta:
        model = Cable
        fields = ['id', 'identifier', 'number_of_cores', 'length', 'cores']


class ConnectCoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = '__all__'

    def create(self, validated_data):
        core_from = validated_data['core_from']
        core_to = validated_data['core_to']
        Connection.objects.create(core_from=core_to, core_to=core_from)
        return Connection.objects.create(core_from=core_from, core_to=core_to)
