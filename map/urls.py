from django.urls import path
from map import views
from map import oldview

urlpatterns = [
    path('pop/', views.PopListView.as_view(), name='pop-list'),
    path('pop/create/', views.PopCreateView.as_view(), name='pop-create'),

    path('client/', views.ClientListView.as_view(), name='client-create'),
    path('client/create/', views.ClientCreateView.as_view(), name='client-list'),
    path('client-details/<int:client_id>/cores/', views.ClientCoresDetailsAPIView.as_view(),
         name='client-core-details'),
    path('client/<int:client_id>/paths/', views.ClientPathsView.as_view(), name='client-path'),

    path('junction/', views.JunctionListView.as_view(), name='junction-create'),
    path('junction/create/', views.JunctionCreateView.as_view(), name='junction-list'),
    path('junction-details/<int:junction_id>/cores/', views.JunctionCoresDetailsAPIView.as_view(),
         name='junction-core-details'),

    path('gpon/', views.GponListView.as_view(), name='gpon-create'),
    path('gpon/create/', views.GponCreateView.as_view(), name='gpon-list'),

    path('cable/', views.CableListView.as_view(), name='cable-list'),
    path('cable/create/', views.CableCreateView.as_view(), name='cable-create'),

    path('core/<int:pk>/update-assign-status/', views.CoreAssignView.as_view(), name='core-assign-withdraw'),

    path('connect-cores/', views.ConnectCoresAPIView.as_view(), name='connect-cores'),
    path('disconnect-cores/', views.DisConnectCoresAPIView.as_view(), name='disconnect-cores'),
    # path('network/', views.Network.as_view(), name='network'),

    path('network/', oldview.network_view, name='network_view'),
]
