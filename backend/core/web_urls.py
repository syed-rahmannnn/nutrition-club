from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='homepage.html'), name='homepage'),
    path('ums/', TemplateView.as_view(template_name='ums_attendance.html'), name='ums_attendance'),
    path('body-checkup/', TemplateView.as_view(template_name='body_checkup.html'), name='body_checkup'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('member-details/', TemplateView.as_view(template_name='member_details.html'), name='member_details'),
]
