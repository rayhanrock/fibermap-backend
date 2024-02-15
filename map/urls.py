from django.urls import path, include
from map import views
from map import oldview
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', views.UserViewSets)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.UserLoginApiView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('verify-token/', views.VerifyTokenView.as_view(), name='verify-token'),

    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('pop/', views.PopListView.as_view(), name='pop-list'),
    path('pop/create/', views.PopCreateView.as_view(), name='pop-create'),
    path('pop-details/<int:pop_id>/cores/', views.PopCoresDetailsAPIView.as_view(),
         name='pop-core-details'),
    path('pop/<int:pop_id>/paths/', views.PopPathsView.as_view(), name='pop-path'),
    path('pop/<int:id>/update/', views.PopUpdateView.as_view(), name='pop-update'),
    path('pop/<int:pk>/delete/', views.PopDeleteView.as_view(), name='pop-delete'),

    path('client/', views.ClientListView.as_view(), name='client-create'),
    path('client/create/', views.ClientCreateView.as_view(), name='client-list'),
    path('client-details/<int:client_id>/cores/', views.ClientCoresDetailsAPIView.as_view(),
         name='client-core-details'),
    path('client/<int:client_id>/paths/', views.ClientPathsView.as_view(), name='client-path'),
    path('client/<int:id>/update/', views.ClientUpdateView.as_view(), name='client-update'),
    path('client/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client-delete'),

    path('junction/', views.JunctionListView.as_view(), name='junction-create'),
    path('junction/create/', views.JunctionCreateView.as_view(), name='junction-list'),
    path('junction-details/<int:junction_id>/cores/', views.JunctionCoresDetailsAPIView.as_view(),
         name='junction-core-details'),

    path('gpon/', views.GponListView.as_view(), name='gpon-create'),
    path('gpon/create/', views.GponCreateView.as_view(), name='gpon-list'),
    path('gpon-details/<int:gpon_id>/cores/', views.GponCoresDetailsAPIView.as_view(),
         name='gpon-core-details'),
    path('gpon/<int:gpon_id>/add-input-cable/', views.AddGponInputCable.as_view(), name='gpon-add-input-cable'),
    path('gpon/<int:gpon_id>/remove-input-cable/', views.RemoveGponInputCable.as_view(),
         name='gpon-remove-input-cable'),
    path('gpon/<int:gpon_id>/assign-core/', views.GponInputCoreAssignView.as_view(), name='gpon-input-assign-core'),
    path('gpon/<int:gpon_id>/withdraw-core/', views.GponInputCoreWithdrawView.as_view(), name='gpon-input-withdraw-core'),
    path('gpon/<int:id>/update/', views.GponUpdateView.as_view(), name='gpon-update'),
    path('gpon/<int:pk>/delete/', views.GponDeleteView.as_view(), name='gpon-delete'),

    path('cable/', views.CableListView.as_view(), name='cable-list'),
    path('cable/create/', views.CableCreateView.as_view(), name='cable-create'),

    path('core/<int:pk>/update-assign-status/', views.CoreAssignView.as_view(), name='core-assign-withdraw'),

    path('connect-cores/', views.ConnectCoresAPIView.as_view(), name='connect-cores'),
    path('disconnect-cores/', views.DisConnectCoresAPIView.as_view(), name='disconnect-cores'),
    # path('network/', views.Network.as_view(), name='network'),

    path('network/', oldview.network_view, name='network_view'),
]
