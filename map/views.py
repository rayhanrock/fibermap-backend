from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import POP, Client, Junction, Gpon, Cable
from .serializers import (POPCreateSerializer, ClientCreateSerializer, GponCreateSerializer, JunctionCreateSerializer,
                          POPListSerializer, ClientListSerializer, GponListSerializer,
                          JunctionListSerializer, CableCreateSerializer, CableListSerializer)


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

# class Network(APIView):
#     def get(self, request, *args, **kwargs):
#         pops = POP.objects.all()
#         clients = Client.objects.all()
#         junctions = Junction.objects.all()
#         gpons = Gpon.objects.all()
#         cables = Cable.objects.all()
#
#         return Response(
#             {
#                 'pops': POPListSerializer(pops, many=True).data,
#                 'clients': ClientListSerializer(clients, many=True).data,
#                 'junctions': JunctionListSerializer(junctions, many=True).data,
#                 'gpons': GponListSerializer(gpons, many=True).data,
#                 'cables': CableListSerializer(cables, many=True).data
#             },
#             status=status.HTTP_200_OK
#         )
