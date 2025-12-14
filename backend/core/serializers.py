from rest_framework import serializers
from .models import Member, Attendance, Payment, Checkup, Registration, BodyComponentEvaluation


class BodyComponentEvaluationSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format='%Y-%m-%d', required=False)
    
    class Meta:
        model = BodyComponentEvaluation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'fat', 'fluids', 'analysis_data')

    def validate(self, data):
        # enforce mandatory numeric fields for registration (fat and fluids are now auto-calculated)
        mandatory = ['height_cm', 'weight_kg', 'visceral_fat']
        missing = [f for f in mandatory if data.get(f) in (None, '')]
        if missing:
            raise serializers.ValidationError({"missing_fields": missing})
        
        # Gender-based validation for body fat and skeletal muscle fields
        member = data.get('member')
        if member and hasattr(member, 'gender'):
            gender = member.gender
            
            if gender == "Male":
                # For males, only men columns can have values
                if data.get('body_fat_women') or data.get('skeletal_muscle_women'):
                    raise serializers.ValidationError(
                        "For male gender, only men columns (body_fat_men, skeletal_muscle_men) can have values."
                    )
            elif gender == "Female":
                # For females, only women columns can have values
                if data.get('body_fat_men') or data.get('skeletal_muscle_men'):
                    raise serializers.ValidationError(
                        "For female gender, only women columns (body_fat_women, skeletal_muscle_women) can have values."
                    )
            # For "Other" gender, all fields are allowed (no restriction)
        
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'member')

    def validate(self, data):
        # mandatory fields checks
        required_fields = ['guest_name', 'mobile_number', 'invited_by', 'gender', 'membership',
                           'occupation', 'age', 'do_you_exercise', 'hours_sleep', 'liters_water',
                           'loss_of_energy', 'transformation_targets',
                           'surveyed_by', 'available_time']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            raise serializers.ValidationError({"missing_fields": missing})
        
        # If membership is OTHERS, number_of_days is required
        membership = data.get('membership')
        if membership == 'OTHERS':
            if not data.get('number_of_days'):
                raise serializers.ValidationError({
                    "number_of_days": "Number of days is required when membership is 'Others'"
                })
            if data.get('number_of_days') <= 0:
                raise serializers.ValidationError({
                    "number_of_days": "Number of days must be greater than 0"
                })
        
        return data


class MemberSerializer(serializers.ModelSerializer):
    registration = RegistrationSerializer(read_only=True)
    body_evaluations = BodyComponentEvaluationSerializer(many=True, read_only=True)
    membership_label = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = '__all__'
    
    def get_membership_label(self, obj):
        if obj.membership_total_sessions and obj.membership_total_sessions > 0:
            return f"{obj.ums_count} / {obj.membership_total_sessions}"
        return ""


class MemberListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    membership_label = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = ['id', 'member_code', 'full_name', 'phone', 'ums_count', 'balance', 
                  'latest_weight', 'latest_height', 'next_checkup_date', 
                  'membership', 'membership_total_sessions', 'membership_label']
    
    def get_membership_label(self, obj):
        if obj.membership_total_sessions and obj.membership_total_sessions > 0:
            return f"{obj.ums_count} / {obj.membership_total_sessions}"
        return ""


class AttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'


class CheckupSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = Checkup
        fields = '__all__'



