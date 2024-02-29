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

    path('reseller/', views.ResellerListView.as_view(), name='reseller-create'),
    path('reseller/create/', views.ResellerCreateView.as_view(), name='reseller-list'),
    path('reseller-details/<int:reseller_id>/cores/', views.ResellerCoresDetailsAPIView.as_view(),
         name='reseller-core-details'),
    path('reseller/<int:reseller_id>/paths/', views.ResellerPathsView.as_view(), name='reseller-path'),
    path('reseller/<int:id>/update/', views.ResellerUpdateView.as_view(), name='reseller-update'),
    path('reseller/<int:pk>/delete/', views.ResellerDeleteView.as_view(), name='reseller-delete'),

    path('tjbox/', views.TJBoxListView.as_view(), name='tjbox-list'),
    path('tjbox/create/', views.TJBoxCreateView.as_view(), name='tjbox-create'),
    path('tjbox-details/<int:tj_box_id>/cores/', views.TJBoxCoresDetailsAPIView.as_view(),
         name='tjbox-core-details'),
    path('tjbox/<int:id>/update/', views.TJBoxUpdateView.as_view(), name='tjbox-update'),
    path('tjbox/<int:pk>/delete/', views.TJBoxDeleteView.as_view(), name='tjbox-delete'),


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
    path('cable/<int:id>/update/', views.CableUpdateView.as_view(), name='cable-update'),
    path('cable/<int:pk>/delete/', views.CableDeleteView.as_view(), name='cable-delete'),
    path('cable/<int:cable_id>/cut/', views.CableCutAPIView.as_view(), name='cable-cut'),

    path('connect-cores/', views.ConnectCoresAPIView.as_view(), name='connect-cores'),
    path('disconnect-cores/', views.DisConnectCoresAPIView.as_view(), name='disconnect-cores'),
    # path('network/', views.Network.as_view(), name='network'),

    path('network/', oldview.network_view, name='network_view'),
]
