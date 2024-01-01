from django.urls import path
from map import views
from map import oldview

urlpatterns = [
    path('pop/', views.PopListCreateView.as_view(), name='pop-list-create'),
    path('gpon/', views.GponListCreateView.as_view(), name='gpon-list-create'),
    path('junction/', views.JunctionListCreateView.as_view(), name='junction-list-create'),
    path('client/', views.ClientListCreateView.as_view(), name='client-list-create'),
    path('network/', views.Network.as_view(), name='network'),



    # path('network/', oldview.network_view, name='network_view'),
]
