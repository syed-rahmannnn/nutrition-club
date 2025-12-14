from django.contrib import admin
from .models import Member, Attendance, Payment, Checkup, Registration, BodyComponentEvaluation


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['member_code', 'full_name', 'phone', 'ums_count', 'balance', 'registration_date']
    search_fields = ['member_code', 'full_name', 'phone']
    list_filter = ['registration_date', 'gender']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['member', 'date', 'present', 'paid_amount', 'submitted_at']
    list_filter = ['date', 'present']
    search_fields = ['member__full_name', 'member__phone']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'date', 'method']
    list_filter = ['date', 'method']
    search_fields = ['member__full_name', 'member__phone']


@admin.register(Checkup)
class CheckupAdmin(admin.ModelAdmin):
    list_display = ['member', 'checkup_date', 'weight', 'height']
    list_filter = ['checkup_date']
    search_fields = ['member__full_name']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'mobile_number', 'occupation', 'surveyed_by', 'created_at']
    list_filter = ['created_at', 'do_you_exercise', 'tried_diet_programs']
    search_fields = ['guest_name', 'mobile_number', 'member__full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BodyComponentEvaluation)
class BodyComponentEvaluationAdmin(admin.ModelAdmin):
    list_display = ['member', 'date', 'weight_kg', 'height_cm', 'bmi', 'fat', 'fluids']
    list_filter = ['date']
    search_fields = ['member__full_name', 'member__phone']
    readonly_fields = ['created_at', 'updated_at']
