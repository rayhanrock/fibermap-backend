from django.db.models import Q, Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import POP, Client, Junction, Gpon, Cable, Core
from .serializers import (POPCreateSerializer, ClientCreateSerializer, GponCreateSerializer, JunctionCreateSerializer,
                          POPListSerializer, ClientListSerializer, GponListSerializer,
                          JunctionListSerializer, CableCreateSerializer, CableListSerializer, CableSerializer,
                          CoreSerializer)


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
            serialized_cable['cores'] = CoreSerializer(cores.filter(cable=cable), many=True).data
            serialized_data.append(serialized_cable)

        return Response(serialized_data)
