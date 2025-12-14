from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'members', views.MemberViewSet)
router.register(r'attendances', views.AttendanceViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'checkups', views.CheckupViewSet)
router.register(r'registrations', views.RegistrationViewSet, basename='registration')

urlpatterns = [
    # Router includes member search action at /members/search/
    path('', include(router.urls)),
    path('attendance/submit/', views.attendance_submit, name='attendance_submit'),
    path('report/daily/', views.generate_daily_report, name='daily_report'),
    path('reports/registration/<int:registration_id>/analysis/', views.generate_registration_analysis, name='registration_analysis'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    # Removed standalone members/search path to avoid collision with router detail route
    path('body-checkup/<int:member_id>/', views.body_checkup_data, name='body_checkup_data'),
    path('body-checkup/<int:member_id>/save/', views.body_checkup_save, name='body_checkup_save'),
    path('health/', views.health_check, name='health_check'),
]
