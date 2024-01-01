from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import POP, Client, Junction, Gpon
from .serializers import (POPSerializer, ClientSerializer, GponSerializer, JunctionSerializer,
                          NetworkPOPSerializer, NetworkClientSerializer, NetworkGponSerializer,
                          NetworkJunctionSerializer, )


class PopListCreateView(generics.ListCreateAPIView):
    queryset = POP.objects.all()
    serializer_class = POPSerializer


class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class JunctionListCreateView(generics.ListCreateAPIView):
    queryset = Junction.objects.all()
    serializer_class = JunctionSerializer


class GponListCreateView(generics.ListCreateAPIView):
    queryset = Gpon.objects.all()
    serializer_class = GponSerializer


class Network(APIView):
    def get(self, request, *args, **kwargs):
        pops = POP.objects.all()
        clients = Client.objects.all()
        junctions = Junction.objects.all()
        gpons = Gpon.objects.all()

        return Response(
            {
                'pops': NetworkPOPSerializer(pops, many=True).data,
                'clients': NetworkClientSerializer(clients, many=True).data,
                'junctions': NetworkJunctionSerializer(junctions, many=True).data,
                'gpons': NetworkGponSerializer(gpons, many=True).data
            },
            status=status.HTTP_200_OK
        )
