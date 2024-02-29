import json
from django.db.models import Q
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from . import permissions
from .models import POP, Client, TJBox, Gpon, Cable, Core, Connection, UserProfile, Marker, Reseller
from .serializers import (POPCreateSerializer, ClientCreateSerializer, GponCreateSerializer, TJBoxCreateSerializer,
                          POPListSerializer, ClientListSerializer, GponListSerializer,
                          TJBoxListSerializer, TJBoxUpdateSerializer, CableCreateSerializer, CableListSerializer,
                          CableSerializer,
                          ClientCoreSerializer, CoreAssignSerializer, TJBoxCoreSerializer, ConnectCoresSerializer,
                          PopCoreSerializer, GponOutCoreSerializer, GponCableCoreSerializer, POPUpdateSerializer,
                          ClientUpdateSerializer, GponUpdateSerializer, CableUpdateSerializer, UserSerializer,
                          ResellerCoreSerializer, ResellerUpdateSerializer, ResellerListSerializer,
                          ResellerCreateSerializer)

from .utility import find_core_paths

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone


class UserViewSets(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer

    # permission_classes = (permissions.UpdateOwnProfile,)
    # authentication_classes = (TokenAuthentication,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        message = f"User with name {instance.username} has been deleted."
        return Response({'message': message}, status=status.HTTP_204_NO_CONTENT)


class UserLoginApiView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user = Token.objects.get(key=response.data['token']).user
            user.last_login = timezone.now()
            user.save()

        return response


class LogoutView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        token = Token.objects.get(user=user)
        token.delete()

        return Response({'detail': 'Logged out successfully.'})


class VerifyTokenView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'is_staff': user.is_staff,
        }
        return Response({'user': data}, status=status.HTTP_200_OK)


class DashboardView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        total_clients = Client.objects.count()
        total_gpons = Gpon.objects.count()
        total_pop = POP.objects.count()
        total_cables = Cable.objects.count()
        return Response(data={
            'total_clients': total_clients,
            'total_gpons': total_gpons,
            'total_pop': total_pop,
            'total_cables': total_cables
        }, status=status.HTTP_200_OK)


class PopCreateView(generics.CreateAPIView):
    serializer_class = POPCreateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class PopListView(generics.ListAPIView):
    queryset = POP.objects.all()
    serializer_class = POPListSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class PopUpdateView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    queryset = POP.objects.all()
    serializer_class = POPUpdateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class PopDeleteView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            pop = POP.objects.get(pk=pk)
            pop.marker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except POP.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ResellerCreateView(generics.CreateAPIView):
    serializer_class = ResellerCreateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class ResellerListView(generics.ListAPIView):
    queryset = Reseller.objects.all()
    serializer_class = ResellerListSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class ResellerUpdateView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    queryset = Reseller.objects.all()
    serializer_class = ResellerUpdateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class ResellerDeleteView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            reseller = Reseller.objects.get(pk=pk)
            reseller.marker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Reseller.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ResellerPathsView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, reseller_id):
        try:
            reseller = Reseller.objects.get(id=reseller_id)
        except Reseller.DoesNotExist:
            return Response({'error': 'Reseller not found'}, status=status.HTTP_404_NOT_FOUND)

        cores = Core.objects.filter(marker=reseller.marker, assigned=True)
        serialized_data = []
        for core in cores:
            path = find_core_paths(core)
            data = {
                'total_length': 0,
                'path_direction': [],
            }
            path_direction = data['path_direction']
            print("path", path)
            for c in path:
                path_unit = {}
                marker = c.marker
                cable = c.cable
                data['total_length'] += cable.length
                path_unit['model_type'] = marker.type
                path_unit['model_identifier'] = marker.identifier
                path_unit['cable_id'] = cable.id
                path_unit['cable_line'] = cable.get_polyline()
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


class ResellerCoresDetailsAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, reseller_id):
        try:
            reseller = Reseller.objects.get(id=reseller_id)
        except Reseller.DoesNotExist:
            return Response({'error': 'Reseller not found'}, status=status.HTTP_404_NOT_FOUND)

        cores = Core.objects.filter(marker=reseller.marker)
        cables = set(core.cable for core in cores)

        serialized_data = []
        for cable in cables:
            serialized_cable = CableSerializer(cable).data
            serialized_cable['cores'] = ResellerCoreSerializer(cores.filter(cable=cable), many=True).data
            serialized_data.append(serialized_cable)

        return Response(serialized_data)


class ClientCreateView(generics.CreateAPIView):
    serializer_class = ClientCreateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class ClientListView(generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientListSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class ClientUpdateView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    queryset = Client.objects.all()
    serializer_class = ClientUpdateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class ClientDeleteView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
            client.marker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Client.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ClientPathsView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

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
            print("path", path)
            for c in path:
                path_unit = {}
                marker = c.marker
                cable = c.cable
                data['total_length'] += cable.length
                path_unit['model_type'] = marker.type
                path_unit['model_identifier'] = marker.identifier
                path_unit['cable_id'] = cable.id
                path_unit['cable_line'] = cable.get_polyline()
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
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

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


class TJBoxCreateView(generics.CreateAPIView):
    serializer_class = TJBoxCreateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class TJBoxListView(generics.ListAPIView):
    queryset = TJBox.objects.all()
    serializer_class = TJBoxListSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class TJBoxUpdateView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    queryset = TJBox.objects.all()
    serializer_class = TJBoxUpdateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class TJBoxDeleteView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            tj_box = TJBox.objects.get(pk=pk)
            tj_box.marker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TJBox.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GponCreateView(generics.CreateAPIView):
    serializer_class = GponCreateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class GponListView(generics.ListAPIView):
    queryset = Gpon.objects.all()
    serializer_class = GponListSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class GponUpdateView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    queryset = Gpon.objects.all()
    serializer_class = GponUpdateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class GponDeleteView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            gpon = Gpon.objects.get(pk=pk)
            gpon.marker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Gpon.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CableCreateView(generics.CreateAPIView):
    serializer_class = CableCreateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class CableListView(generics.ListAPIView):
    queryset = Cable.objects.all()
    serializer_class = CableListSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class CableUpdateView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    queryset = Cable.objects.all()
    serializer_class = CableUpdateSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class CableDeleteView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            cable = Cable.objects.get(pk=pk)
            cable.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cable.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CoreAssignView(generics.UpdateAPIView):
    queryset = Core.objects.all()
    serializer_class = CoreAssignSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class TJBoxCoresDetailsAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, tj_box_id):
        try:
            tj_box = TJBox.objects.get(id=tj_box_id)
        except TJBox.DoesNotExist:
            return Response({'error': 'TJ Box not found'}, status=status.HTTP_404_NOT_FOUND)

        cores = Core.objects.filter(marker=tj_box.marker).exclude(cable=None)
        cables = set(core.cable for core in cores)

        serialized_data = []
        for cable in cables:
            serialized_cable = CableSerializer(cable).data
            serialized_cable['cores'] = TJBoxCoreSerializer(cores.filter(cable=cable), many=True).data
            serialized_data.append(serialized_cable)

        splitters = []
        for gpon in Gpon.objects.filter(tj_box=tj_box):
            gpon_out_details = {
                'number_of_splitter': gpon.splitter,
                'input_core_id': gpon.input_core.id,
                'splitter_type': gpon.name,
                'output_cores': []
            }

            cores = Core.objects.filter(marker=gpon.marker, splitter=gpon)
            gpon_out_cores = cores.filter(cable=None).order_by('core_number')
            for core in gpon_out_cores:
                gpon_out_details['output_cores'].append(GponOutCoreSerializer(core).data)
            splitters.append(gpon_out_details)

        data = {
            'splitters': splitters,
            'cables': serialized_data
        }
        return Response(data)


class GponCoresDetailsAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, gpon_id):
        try:
            gpon = Gpon.objects.get(id=gpon_id)
        except Gpon.DoesNotExist:
            return Response({'error': 'Gpon not found'}, status=status.HTTP_404_NOT_FOUND)

        cores = Core.objects.filter(marker=gpon.marker)
        cables = set(core.cable for core in cores if core.cable is not None)

        input_cable = gpon.input_cable
        gpon_input_cable_data = None
        if input_cable is not None:
            cables.remove(input_cable)
            serialized_cable = CableSerializer(input_cable).data
            serialized_cable['cores'] = GponCableCoreSerializer(cores.filter(cable=input_cable), many=True).data
            gpon_input_cable_data = serialized_cable

        gpon_out_details = {
            'number_of_splitter': gpon.splitter,
            'input_core_id': gpon.input_core.id,
            'output_cores': []
        }
        gpon_out_cores = cores.filter(cable=None).exclude(core_number=0)
        for core in gpon_out_cores:
            gpon_out_details['output_cores'].append(GponOutCoreSerializer(core).data)

        gpon_output_cable_data = []

        for cable in cables:
            serialized_cable = CableSerializer(cable).data
            serialized_cable['cores'] = GponCableCoreSerializer(cores.filter(cable=cable), many=True).data
            gpon_output_cable_data.append(serialized_cable)

        data = {
            'type': gpon.name,
            'input_cable': gpon_input_cable_data,
            'out': gpon_out_details,
            'output_cables': gpon_output_cable_data
        }
        return Response(data)


class AddGponInputCable(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request, gpon_id):
        data = request.data
        try:
            gpon = Gpon.objects.get(id=gpon_id)
            cable_id = data['cable_id']

        except Gpon.DoesNotExist:
            return Response({'error': 'Gpon not found'}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response({'error': 'cable_id is required'}, status=status.HTTP_404_NOT_FOUND)

        if gpon.input_cable is not None:
            return Response({'error': 'Gpon already has an input cable'}, status=status.HTTP_400_BAD_REQUEST)

        cables = Cable.objects.filter(Q(starting_point=gpon.marker) | Q(ending_point=gpon.marker))
        cable = cables.filter(id=cable_id).first()

        if cable is None:
            return Response({'error': 'Invalid cable'}, status=status.HTTP_400_BAD_REQUEST)

        cores = Core.objects.filter(marker=gpon.marker, cable=cable)
        for core in cores:
            connected_to = self.get_connected_to(core)
            if connected_to is not None:
                return Response({'error': 'Disconnect connected cores first to add as input cable'},
                                status=status.HTTP_400_BAD_REQUEST)

        gpon.input_cable = cable
        gpon.save()
        return Response({'success': 'Gpon input cable added'}, status=status.HTTP_200_OK)

    def get_connected_to(self, obj):
        connection = Connection.objects.filter(core_from=obj)
        for conn in connection:
            if conn.core_to.cable is None:
                return {'id': conn.core_to.id}
        return None


class RemoveGponInputCable(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, gpon_id):
        try:
            gpon = Gpon.objects.get(id=gpon_id)
        except Gpon.DoesNotExist:
            return Response({'error': 'Gpon not found'}, status=status.HTTP_404_NOT_FOUND)

        if gpon.input_cable is None:
            return Response({'error': 'Gpon does not have an input cable'}, status=status.HTTP_400_BAD_REQUEST)

        input_cores = Core.objects.filter(marker=gpon.marker, cable=gpon.input_cable)
        for cr in input_cores:
            connected_to = self.get_connected_to(cr)
            if connected_to is not None:
                return Response({'error': 'Disconnect assigned core first to remove input cable'},
                                status=status.HTTP_400_BAD_REQUEST)

        gpon.input_cable = None
        gpon.save()
        return Response({'success': 'Gpon input cable removed'}, status=status.HTTP_200_OK)

    def get_connected_to(self, core):
        connection = Connection.objects.filter(core_from=core)
        for conn in connection:
            if conn.core_to.cable is None:
                return {'id': conn.core_to.id}
        return None


class GponInputCoreAssignView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request, gpon_id):
        data = request.data

        try:
            gpon = Gpon.objects.get(id=gpon_id)
            core_id = data['core_id']
        except Gpon.DoesNotExist:
            return Response({'error': 'Gpon not found'}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response({'error': 'core_id is required'}, status=status.HTTP_404_NOT_FOUND)

        if gpon.input_cable is None:
            return Response({'error': 'Gpon does not have an input cable'}, status=status.HTTP_400_BAD_REQUEST)

        input_cores = Core.objects.filter(marker=gpon.marker, cable=gpon.input_cable)
        core = input_cores.filter(id=core_id).first()
        if core is None:
            return Response({'error': 'Invalid Core to assign'}, status=status.HTTP_400_BAD_REQUEST)

        for cr in input_cores:
            connected_to = self.get_connected_to(cr)
            if connected_to is not None:
                return Response({'error': 'Core already connected'}, status=status.HTTP_400_BAD_REQUEST)

        Connection.objects.create(
            core_from=gpon.input_core,
            core_to=core
        )
        Connection.objects.create(
            core_from=core,
            core_to=gpon.input_core
        )
        return Response({'success': 'Core assigned'}, status=status.HTTP_200_OK)

    def get_connected_to(self, core):
        connection = Connection.objects.filter(core_from=core)
        for conn in connection:
            if conn.core_to.cable is None:
                return {'id': conn.core_to.id}
        return None


class GponInputCoreWithdrawView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request, gpon_id):
        try:
            gpon = Gpon.objects.get(id=gpon_id)
        except Gpon.DoesNotExist:
            return Response({'error': 'Gpon not found'}, status=status.HTTP_404_NOT_FOUND)

        if gpon.input_cable is None:
            return Response({'error': 'Gpon does not have an input cable'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data

        try:
            core_id = data['core_id']
            core = Core.objects.get(id=core_id)
        except KeyError:
            return Response({'error': 'core_id is required'}, status=status.HTTP_404_NOT_FOUND)
        except Core.DoesNotExist:
            return Response({'error': 'Core not found'}, status=status.HTTP_404_NOT_FOUND)

        left = Connection.objects.filter(core_from=core, core_to=gpon.input_core).first()
        right = Connection.objects.filter(core_from=gpon.input_core, core_to=core).first()

        if left:
            left.delete()
        if right:
            right.delete()

        return Response({'success': 'Core assigned'}, status=status.HTTP_200_OK)


class PopCoresDetailsAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, pop_id):
        try:
            pop = POP.objects.get(id=pop_id)
        except POP.DoesNotExist:
            return Response({'error': 'POP not found'}, status=status.HTTP_404_NOT_FOUND)

        cores = Core.objects.filter(marker=pop.marker)
        cables = set(core.cable for core in cores)

        serialized_data = []
        for cable in cables:
            serialized_cable = CableSerializer(cable).data
            serialized_cable['cores'] = PopCoreSerializer(cores.filter(cable=cable), many=True).data
            serialized_data.append(serialized_cable)

        return Response(serialized_data)


class PopPathsView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, pop_id):
        try:
            pop = POP.objects.get(id=pop_id)
        except POP.DoesNotExist:
            return Response({'error': 'Pop not found'}, status=status.HTTP_404_NOT_FOUND)

        cores = Core.objects.filter(marker=pop.marker, assigned=True)
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
                path_unit['cable_line'] = cable.get_polyline()

                path_unit['cable_id'] = cable.id
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


class ConnectCoresAPIView(generics.CreateAPIView):
    serializer_class = ConnectCoresSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


class DisConnectCoresAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

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


class CableCutAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request, cable_id):
        data = request.data
        try:
            cable = Cable.objects.get(id=cable_id)
            divider_point = data['divider_point']
            push_index = data['push_index']
            tjbox_id = data['tjbox_id']
            tjbox_name = data['tjbox_name']

        except Cable.DoesNotExist:
            return Response({'error': 'Cable not found'}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response({'error': '{divider_point , push_index, tjbox_id, tjbox_name} is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        marker = Marker.objects.create(identifier=tjbox_id, type="TJ_BOX", latitude=divider_point[0],
                                       longitude=divider_point[1])
        tj_box = TJBox.objects.create(identifier=tjbox_id, name=tjbox_name, marker=marker)

        polyline = cable.get_polyline()
        first_half = polyline[:push_index + 1] + [{'lat': divider_point[0], 'lng': divider_point[1]}]
        second_half = [{'lat': divider_point[0], 'lng': divider_point[1]}] + polyline[push_index + 1:]

        left_cable = Cable.objects.create(
            identifier=cable.identifier,
            type=cable.type,
            start_from=cable.start_from,
            starting_point=cable.starting_point,
            end_to=marker.type,
            ending_point=marker,
            number_of_cores=cable.number_of_cores,
            length=cable.length,
            notes=cable.notes,
            description=cable.description,
            polyline=json.dumps(first_half),

        )
        right_cable = Cable.objects.create(
            identifier=cable.identifier,
            type=cable.type,
            start_from=marker.type,
            starting_point=marker,
            end_to=cable.end_to,
            ending_point=cable.ending_point,
            number_of_cores=cable.number_of_cores,
            length=cable.length,
            notes=cable.notes,
            description=cable.description,
            polyline=json.dumps(second_half),

        )

        starting_point_cores = Core.objects.filter(cable=cable, marker=cable.starting_point).order_by('core_number')
        ending_point_cores = Core.objects.filter(cable=cable, marker=cable.ending_point).order_by('core_number')

        print("starting_point_cores", starting_point_cores.count())
        print("ending_point_cores", ending_point_cores.count())
        print("ending_point_cores", ending_point_cores)

        for core in starting_point_cores:
            core.cable = left_cable
            core.save()
        for core in ending_point_cores:
            core.cable = right_cable
            core.save()

        for i in range(starting_point_cores.count()):
            conn_left_to_right = Connection.objects.filter(core_from=starting_point_cores[i],
                                                           core_to=ending_point_cores[i]).first()

            left_cable_core_for_tj = Core.objects.create(
                marker=marker,
                cable=left_cable,
                core_number=conn_left_to_right.core_from.core_number,
                color=conn_left_to_right.core_from.color,
                assigned=False
            )

            conn_left_to_right.core_to = left_cable_core_for_tj
            conn_left_to_right.save()

            Connection.objects.create(core_from=left_cable_core_for_tj, core_to=conn_left_to_right.core_from)

            conn_right_to_left = Connection.objects.filter(core_from=ending_point_cores[i],
                                                           core_to=starting_point_cores[i]).first()

            right_cable_core_for_tj = Core.objects.create(
                marker=marker,
                cable=right_cable,
                core_number=conn_right_to_left.core_from.core_number,
                color=conn_right_to_left.core_from.color,
                assigned=False
            )

            conn_right_to_left.core_to = right_cable_core_for_tj
            conn_right_to_left.save()

            Connection.objects.create(core_from=right_cable_core_for_tj, core_to=conn_right_to_left.core_from)

        cable.delete()

        return Response({"status": "cable cut success"}, status=status.HTTP_200_OK)
