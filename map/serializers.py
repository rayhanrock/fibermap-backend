import json
from json import JSONEncoder

from .utility import find_core_paths

from rest_framework import serializers

from .models import Marker, POP, Client, Junction, Gpon, Cable, Core, Connection


class MarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ('id', 'type', 'latitude', 'longitude', 'address', 'notes', 'description')

    def validate_address(self, value):
        if not value:
            raise serializers.ValidationError('Address is required')
        return value

    def validate_latitude(self, value):
        if not value:
            raise serializers.ValidationError('Latitude is required')
        return value

    def validate_longitude(self, value):
        if not value:
            raise serializers.ValidationError('Longitude is required')
        return value


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

    def validate_identifier(self, value):
        if not value:
            raise serializers.ValidationError('Identifier is required')
        value = value.strip()
        if POP.objects.filter(identifier=value).exists():
            raise serializers.ValidationError('Identifier already exists')
        return value


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

    def validate_identifier(self, value):
        if not value:
            raise serializers.ValidationError('Identifier is required')
        value = value.strip()
        if Client.objects.filter(identifier=value).exists():
            raise serializers.ValidationError('Identifier already exists')
        return value


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

    def validate_identifier(self, value):
        if not value:
            raise serializers.ValidationError('Identifier is required')
        value = value.strip()
        if Junction.objects.filter(identifier=value).exists():
            raise serializers.ValidationError('Identifier already exists')
        return value


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

    def validate_identifier(self, value):
        if not value:
            raise serializers.ValidationError('Identifier is required')
        value = value.strip()
        if Gpon.objects.filter(identifier=value).exists():
            raise serializers.ValidationError('Identifier already exists')
        return value

    def validate_splitter(self, value):
        if value not in [2, 4, 8, 12, 16, 32]:
            raise serializers.ValidationError('Splitter must be 2, 4, 8, 12, 16 or 32')
        return value


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
        if start_form in choices:
            starting_point = choices[start_form].objects.filter(id=data['starting_point']).first()
            if starting_point:
                data['starting_point'] = starting_point.marker.id

        end_to = data['end_to']
        if end_to in choices:
            ending_point = choices[end_to].objects.filter(id=data['ending_point']).first()
            if ending_point:
                data['ending_point'] = ending_point.marker.id

        return super().to_internal_value(data)

    # def create(self, validated_data):
    #     starting_point = validated_data['starting_point']
    #     ending_point = validated_data['ending_point']
    #
    #     num_of_core = validated_data['number_of_cores']
    #     instance = super().create(validated_data)
    #
    #     colors = ['red', 'orange', 'yellow', 'olive', 'green', 'teal', 'blue', 'violet', 'purple', 'pink', 'brown',
    #               'black']
    #     len_color = len(colors)
    #     for i in range(1, num_of_core + 1):
    #         color_index = i % len_color
    #         start_marker_side = Core.objects.create(
    #             marker=starting_point,
    #             cable=instance,
    #             core_number=i,
    #             color=colors[color_index],
    #             assigned=False
    #         )
    #         end_marker_side = Core.objects.create(
    #             marker=ending_point,
    #             cable=instance,
    #             core_number=i,
    #             color=colors[color_index],
    #             assigned=False
    #         )
    #
    #         Connection.objects.create(core_from=start_marker_side, core_to=end_marker_side)
    #         Connection.objects.create(core_from=end_marker_side, core_to=start_marker_side)
    #
    #     return instance

    def create(self, validated_data):
        starting_point = validated_data['starting_point']
        ending_point = validated_data['ending_point']

        num_of_core = validated_data['number_of_cores']
        instance = super().create(validated_data)

        colors = ['red', 'orange', 'yellow', 'olive', 'green', 'teal', 'blue', 'violet', 'purple', 'pink', 'brown',
                  'black']
        len_color = len(colors)
        start_list = []
        end_list = []
        for i in range(1, num_of_core + 1):
            color_index = i % len_color
            start_marker_side = Core(
                marker=starting_point,
                cable=instance,
                core_number=i,
                color=colors[color_index],
                assigned=False
            )
            end_marker_side = Core(
                marker=ending_point,
                cable=instance,
                core_number=i,
                color=colors[color_index],
                assigned=False
            )
            start_list.append(start_marker_side)
            end_list.append(end_marker_side)

        Core.objects.bulk_create(
            start_list + end_list
        )
        st = Core.objects.filter(cable=instance, marker=starting_point).order_by('core_number')
        en = Core.objects.filter(cable=instance, marker=ending_point).order_by('core_number')

        connections = [
                          Connection(core_from=start, core_to=end)
                          for start, end in zip(st, en)
                      ] + [
                          Connection(core_from=end, core_to=start)
                          for start, end in zip(st, en)
                      ]
        Connection.objects.bulk_create(connections)

        return instance

    def validate_number_of_cores(self, value):
        if value not in [2, 4, 8, 12, 24, 36, 48]:
            raise serializers.ValidationError('Number of cores must be 2, 4, 8, 12, 24, 36 or 48')
        return value

    def validate(self, data):
        polyline = data['polyline']
        starting_point = data['starting_point']
        ending_point = data['ending_point']

        start_position = {
            "lat": starting_point.latitude,
            "lng": starting_point.longitude
        }

        end_position = {
            "lat": ending_point.latitude,
            "lng": ending_point.longitude
        }

        first_point = polyline.pop(0)
        lat_error = first_point['lat'] - start_position['lat']
        lng_error = first_point['lng'] - start_position['lng']
        if abs(lat_error) > 0.001 or abs(lng_error) > 0.001:
            raise serializers.ValidationError("try draw polyline from starting point as close as possible")

        polyline.insert(0, start_position)

        last_point = polyline.pop()
        lat_error = last_point['lat'] - end_position['lat']
        lng_error = last_point['lng'] - end_position['lng']
        if abs(lat_error) > 0.001 or abs(lng_error) > 0.001:
            raise serializers.ValidationError("try draw polyline from ending point as close as possible")

        polyline.append(end_position)
        data['polyline'] = json.dumps(polyline)

        return data


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


class GponCableCoreSerializer(serializers.ModelSerializer):
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
