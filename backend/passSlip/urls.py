from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SlipViewSet, AdminViewSet, CodeViewSet, UserLogin, qr, get_data, get_latest_item,   home, login, admin_login, login_view, make_qr, make_request, get_user_by_id

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'slips', SlipViewSet)
router.register(r'admin', AdminViewSet)
router.register(r'code', CodeViewSet)



urlpatterns = [
    path('api/', include(router.urls)),
    path('api/make_qr/', make_qr, name='make_qr'),
    path('api/make_request/', make_request, name='make_request'),
    # path('api/login/', UserLogin.as_view(), name='login_view'),
    path('qr/', views.get_data, name='qr'),

    path('login/', login, name='login'),
    path('login/admin_login', admin_login, name='admin_login'),
    path('home/', home, name='home'),
    path('api/slips/get-user/<int:user_id>/', get_user_by_id, name='get_user_by_id'),
    path('api/slips/latest', get_latest_item, name='get_latest_item'),
]