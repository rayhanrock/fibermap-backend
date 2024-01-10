from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import POP, Client, Junction, Gpon, Cable, Core, Connection
from .serializers import (POPCreateSerializer, ClientCreateSerializer, GponCreateSerializer, JunctionCreateSerializer,
                          POPListSerializer, ClientListSerializer, GponListSerializer,
                          JunctionListSerializer, CableCreateSerializer, CableListSerializer, CableSerializer,
                          ClientCoreSerializer, CoreAssignSerializer, CoreSerializer, ConnectCoresSerializer)

from .utility import find_core_paths


class PopCreateView(generics.CreateAPIView):
    serializer_class = POPCreateSerializer


class PopListView(generics.ListAPIView):
    queryset = POP.objects.all()
    serializer_class = POPListSerializer


class ClientCreateView(generics.CreateAPIView):
    serializer_class = ClientCreateSerializer


class ClientListView(generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientListSerializer


class JunctionCreateView(generics.CreateAPIView):
    serializer_class = JunctionCreateSerializer


class JunctionListView(generics.ListAPIView):
    queryset = Junction.objects.all()
    serializer_class = JunctionListSerializer


class GponCreateView(generics.CreateAPIView):
    serializer_class = GponCreateSerializer


class GponListView(generics.ListAPIView):
    queryset = Gpon.objects.all()
    serializer_class = GponListSerializer


class CableCreateView(generics.CreateAPIView):
    serializer_class = CableCreateSerializer


class CableListView(generics.ListAPIView):
    queryset = Cable.objects.all()
    serializer_class = CableListSerializer


class CoreAssignView(generics.UpdateAPIView):
    queryset = Core.objects.all()
    serializer_class = CoreAssignSerializer


class ClientPathsView(APIView):
    def get(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

        cores = Core.objects.filter(marker=client.marker, assigned=True)
        serialized_data = []
        for core in cores:
            path = find_core_paths(core)
            data = {
                'total_length': 0,
                'path_direction': [],
            }
            path_direction = data['path_direction']

            for c in path:
                path_unit = {}
                marker = c.marker
                cable = c.cable
                data['total_length'] += cable.length
                path_unit['model_type'] = marker.type
                path_unit['model_identifier'] = marker.identifier
                path_unit['cable_identifier'] = cable.identifier
                path_unit['total_cable_core'] = cable.number_of_cores
                path_unit['cable_length'] = cable.length
                path_unit['color'] = c.color
                path_direction.append(path_unit)
            data['total_length'] -= path_direction[-1]['cable_length']
            path_direction[-1]['cable_length'] = 0
            path_direction[-1]['cable_identifier'] = '/'
            serialized_data.append(data)
        return Response(serialized_data)


class ClientCoresDetailsAPIView(APIView):
    def get(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

        cores = Core.objects.filter(marker=client.marker)
        cables = set(core.cable for core in cores)

        serialized_data = []
        for cable in cables:
            serialized_cable = CableSerializer(cable).data
            serialized_cable['cores'] = ClientCoreSerializer(cores.filter(cable=cable), many=True).data
            serialized_data.append(serialized_cable)

        return Response(serialized_data)


class JunctionCoresDetailsAPIView(APIView):
    def get(self, request, junction_id):
        try:
            junction = Junction.objects.get(id=junction_id)
        except Junction.DoesNotExist:
            return Response({'error': 'Junction not found'}, status=status.HTTP_404_NOT_FOUND)

        cores = Core.objects.filter(marker=junction.marker)
        cables = set(core.cable for core in cores)

        serialized_data = []
        for cable in cables:
            serialized_cable = CableSerializer(cable).data
            serialized_cable['cores'] = CoreSerializer(cores.filter(cable=cable), many=True).data
            serialized_data.append(serialized_cable)

        return Response(serialized_data)


class ConnectCoresAPIView(generics.CreateAPIView):
    serializer_class = ConnectCoresSerializer


class DisConnectCoresAPIView(APIView):
    def post(self, request, format=None):
        data = request.data

        try:
            core_from_id = data['core_from']
            core_to_id = data['core_to']
            core_from = Core.objects.get(id=core_from_id)
            core_to = Core.objects.get(id=core_to_id)
        except KeyError:
            return Response({'error': 'core_from and core_to is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Core.DoesNotExist:
            return Response({'error': 'Core not found'}, status=status.HTTP_404_NOT_FOUND)

        left = Connection.objects.filter(core_from=core_from, core_to=core_to).first()
        right = Connection.objects.filter(core_from=core_to, core_to=core_from).first()

        if left:
            left.delete()
        if right:
            right.delete()

        return Response({"status": "delete success"}, status=status.HTTP_204_NO_CONTENT)
