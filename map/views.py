from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import POP, Client, Junction, Gpon, Cable, Core, Connection
from .serializers import (POPCreateSerializer, ClientCreateSerializer, GponCreateSerializer, JunctionCreateSerializer,
                          POPListSerializer, ClientListSerializer, GponListSerializer,
                          JunctionListSerializer, CableCreateSerializer, CableListSerializer, CableSerializer,
                          ClientCoreSerializer, CoreAssignSerializer, JunctionCoreSerializer, ConnectCoresSerializer,
                          PopCoreSerializer, GponOutCoreSerializer, GponCableCoreSerializer, POPUpdateSerializer,
                          ClientUpdateSerializer, GponUpdateSerializer)

from .utility import find_core_paths


class DashboardView(APIView):

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


class PopListView(generics.ListAPIView):
    queryset = POP.objects.all()
    serializer_class = POPListSerializer


class PopUpdateView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    queryset = POP.objects.all()
    serializer_class = POPUpdateSerializer


class PopDeleteView(APIView):

    def delete(self, request, pk):
        try:
            pop = POP.objects.get(pk=pk)
            pop.marker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except POP.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ClientCreateView(generics.CreateAPIView):
    serializer_class = ClientCreateSerializer


class ClientListView(generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientListSerializer


class ClientUpdateView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    queryset = Client.objects.all()
    serializer_class = ClientUpdateSerializer


class ClientDeleteView(APIView):

    def delete(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
            client.marker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Client.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


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


class GponUpdateView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    queryset = Gpon.objects.all()
    serializer_class = GponUpdateSerializer


class GponDeleteView(APIView):

    def delete(self, request, pk):
        try:
            gpon = Gpon.objects.get(pk=pk)
            gpon.marker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Gpon.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


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
            serialized_cable['cores'] = JunctionCoreSerializer(cores.filter(cable=cable), many=True).data
            serialized_data.append(serialized_cable)

        return Response(serialized_data)


class GponCoresDetailsAPIView(APIView):

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
