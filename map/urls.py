from django.urls import path
from map import views
from map import oldview

urlpatterns = [
    path('pop/', views.PopListView.as_view(), name='pop-list'),
    path('pop/create/', views.PopCreateView.as_view(), name='pop-create'),

    path('client/', views.ClientListView.as_view(), name='client-create'),
    path('client/create/', views.ClientCreateView.as_view(), name='client-list'),

    path('junction/', views.JunctionListView.as_view(), name='junction-create'),
    path('junction/create/', views.JunctionCreateView.as_view(), name='junction-list'),

    path('gpon/', views.GponListView.as_view(), name='gpon-create'),
    path('gpon/create/', views.GponCreateView.as_view(), name='gpon-list'),

    path('cable/', views.CableListView.as_view(), name='cable-list'),
    path('cable/create/', views.CableCreateView.as_view(), name='cable-create'),
    # path('network/', views.Network.as_view(), name='network'),

    # path('network/', oldview.network_view, name='network_view'),
]
