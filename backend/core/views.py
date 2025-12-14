from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from weasyprint import HTML
from decimal import Decimal
from .models import Member, Attendance, Payment, Checkup, Registration, BodyComponentEvaluation
from .serializers import (
    MemberSerializer, MemberListSerializer, AttendanceSerializer, 
    PaymentSerializer, CheckupSerializer, RegistrationSerializer, BodyComponentEvaluationSerializer
)


def calculate_body_analysis(body_eval, registration):
    """
    Calculate all body component analysis values based on the entered data.
    Updates body_eval object with fat, fluids, and analysis_data.
    
    Args:
        body_eval: BodyComponentEvaluation instance
        registration: Registration instance (for gender and age)
    """
    # Convert to floats for calculations
    height_cm = float(body_eval.height_cm)
    weight_kg = float(body_eval.weight_kg)
    h_m = height_cm / 100.0
    
    gender = registration.gender
    age = registration.age
    
    # Get gender-specific values
    if gender == "Male":
        body_fat = float(body_eval.body_fat_men) if body_eval.body_fat_men else 0
        skeletal_muscle = float(body_eval.skeletal_muscle_men) if body_eval.skeletal_muscle_men else 0
        bf_target = 20
        trunk_target = 15
        if age < 30:
            sm_target = 36
        else:
            sm_target = 36
    elif gender == "Female":
        body_fat = float(body_eval.body_fat_women) if body_eval.body_fat_women else 0
        skeletal_muscle = float(body_eval.skeletal_muscle_women) if body_eval.skeletal_muscle_women else 0
        bf_target = 30
        trunk_target = 30
        if age < 30:
            sm_target = 27
        else:
            sm_target = 25
    else:
        # "Other" - use men values as default
        body_fat = float(body_eval.body_fat_men or body_eval.body_fat_women or 0)
        skeletal_muscle = float(body_eval.skeletal_muscle_men or body_eval.skeletal_muscle_women or 0)
        bf_target = 25
        trunk_target = 15
        sm_target = 30
    
    # 2.1 Min & Max weight
    min_weight = round(21 * h_m * h_m, 1)
    max_weight = round(23 * h_m * h_m, 1)
    
    # 2.2 Excess weight
    excess_weight_raw = round(max_weight - weight_kg, 1)
    excess_weight_abs = abs(excess_weight_raw)
    
    # 2.3 Visceral fat difference
    visc_entered = float(body_eval.visceral_fat)
    visc_diff = round(9 - visc_entered, 1)
    
    # 2.4 Trunk subcutaneous fat difference
    trunk_fat = float(body_eval.trunk_subcutaneous_fat) if body_eval.trunk_subcutaneous_fat else 0
    trunk_diff = round(trunk_target - trunk_fat, 1)
    
    # 2.5 Body fat difference
    bf_diff = round(bf_target - body_fat, 1)
    
    # 2.6 Body age difference
    real_age = age
    body_age_val = float(body_eval.body_age) if body_eval.body_age else real_age
    body_age_diff = round(real_age - body_age_val, 1)
    
    # 2.7 BMI difference
    bmi_val = float(body_eval.bmi) if body_eval.bmi else 0
    bmi_diff = round(23 - bmi_val, 1)
    
    # 2.8 Skeletal muscle difference
    sm_diff = round(sm_target - skeletal_muscle, 1)
    
    # 2.9 Fat calculation
    actual_fat_mass = round(weight_kg * body_fat / 100.0, 1)
    ideal_fat_mass = round(weight_kg * bf_target / 100.0, 1)
    fat_excess = round(actual_fat_mass - ideal_fat_mass, 1)
    
    # 2.10 Fluids calculation
    if excess_weight_raw > 0:
        # Person is below or at ideal weight
        fat_result = 1
        fluids_result = 0
    else:
        # Person is overweight
        fluids_candidate = round(excess_weight_abs - fat_excess, 1)
        if fluids_candidate < 0:
            fluids_candidate = 0
        fat_result = fat_excess
        fluids_result = fluids_candidate
    
    # Update body_eval
    body_eval.fat = Decimal(str(fat_result))
    body_eval.fluids = Decimal(str(fluids_result))
    
    # Store all analysis data
    body_eval.analysis_data = {
        "min_weight": min_weight,
        "max_weight": max_weight,
        "excess_weight": excess_weight_raw,
        "visceral_diff": visc_diff,
        "trunk_diff": trunk_diff,
        "body_fat_diff": bf_diff,
        "body_age_diff": body_age_diff,
        "bmi_diff": bmi_diff,
        "skeletal_diff": sm_diff,
        "targets": {
            "body_fat": bf_target,
            "trunk_fat": trunk_target,
            "skeletal_muscle": sm_target,
            "visceral_fat": 9,
            "bmi": 23
        }
    }
    
    return body_eval


class MemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint for members
    GET /api/members/ - list all members (with optional search)
    GET /api/members/<id>/ - retrieve member detail
    POST /api/members/ - create new member
    PUT/PATCH /api/members/<id>/ - update member
    DELETE /api/members/<id>/ - delete member
    """
    queryset = Member.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MemberListSerializer
        return MemberSerializer
    
    def get_queryset(self):
        queryset = Member.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) | 
                Q(phone__icontains=search) |
                Q(member_code__icontains=search)
            )
        return queryset

    @action(detail=False, methods=['get'], url_path='search', permission_classes=[AllowAny])
    def search(self, request):
        """
        Search members by name or phone.
        GET /api/members/search/?q=<term>
        Returns minimal fields for frontend selection.
        """
        search_term = request.query_params.get('q', '').strip()
        if not search_term:
            return Response({'detail': 'Search term required'}, status=400)

        members = Member.objects.filter(
            Q(full_name__icontains=search_term) | Q(phone__icontains=search_term)
        ).values('id', 'full_name', 'phone', 'registration_date', 'invited_by', 'gender')[:10]

        return Response(list(members))


class AttendanceViewSet(viewsets.ModelViewSet):
    """API endpoint for attendance records"""
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Attendance.objects.all()
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(date=date)
        return queryset


class PaymentViewSet(viewsets.ModelViewSet):
    """API endpoint for payments"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


class CheckupViewSet(viewsets.ModelViewSet):
    """API endpoint for checkups"""
    queryset = Checkup.objects.all()
    serializer_class = CheckupSerializer
    permission_classes = [IsAuthenticated]


class RegistrationViewSet(viewsets.ViewSet):
    """API endpoint for registrations - custom implementation for atomic create"""
    permission_classes = []  # Allow unauthenticated access for new registrations

    @transaction.atomic
    def create(self, request):
        """
        Accepts full registration payload that includes:
        - registration: {guest_name,..., plan_total_amount, initial_amount_paid}
        - body_evaluation: {height_cm, weight_kg, visceral_fat, fat, fluids, ...}
        If member exists by phone, attach registration to that member; otherwise create a Member.
        """
        payload = request.data
        reg_data = payload.get('registration')
        body_data = payload.get('body_evaluation')

        if not reg_data or not body_data:
            return Response({"detail": "registration and body_evaluation required"}, status=400)

        # Validate and save registration (without member)
        reg_serializer = RegistrationSerializer(data=reg_data)
        reg_serializer.is_valid(raise_exception=True)
        
        # Look up or create Member by mobile_number
        phone = reg_serializer.validated_data.get('mobile_number')
        gender = reg_serializer.validated_data.get('gender')
        invited_by = reg_serializer.validated_data.get('invited_by')
        membership_type = reg_serializer.validated_data.get('membership')
        
        # Determine membership total sessions and plan amounts
        membership_totals = {
            'TRIAL': 3,
            'UMS': 26,
            'COMPLEMENT': 1,
        }
        membership_amounts = {
            'TRIAL': Decimal('700'),
            'UMS': Decimal('5400'),
            'COMPLEMENT': Decimal('0'),
        }
        
        # For OTHERS membership, use number_of_days and custom amounts
        if membership_type == 'OTHERS':
            number_of_days = reg_serializer.validated_data.get('number_of_days', 0)
            total_sessions = number_of_days
            # For OTHERS, accept custom plan_total_amount from frontend
            plan_total_raw = reg_serializer.validated_data.get('plan_total_amount') or reg_data.get('plan_total_amount') or 0
            plan_total = Decimal(str(plan_total_raw))
        else:
            total_sessions = membership_totals.get(membership_type, 0)
            plan_total = membership_amounts.get(membership_type, Decimal('0'))
        
        # Get initial amount paid from request (default 0)
        initial_paid_raw = reg_serializer.validated_data.get('initial_amount_paid') or reg_data.get('initial_amount_paid') or 0
        initial_paid = Decimal(str(initial_paid_raw))
        
        # Set plan_total_amount and initial_amount_paid
        reg_serializer.validated_data['plan_total_amount'] = plan_total
        reg_serializer.validated_data['initial_amount_paid'] = initial_paid
        
        member = Member.objects.filter(phone=phone).first()
        if not member:
            # create a new Member minimal record
            member = Member.objects.create(
                member_code=f"M{int(timezone.now().timestamp())}",
                full_name=reg_serializer.validated_data.get('guest_name'),
                phone=phone,
                gender=gender,
                invited_by=invited_by,
                registration_date=timezone.now().date(),
                membership=membership_type,
                membership_total_sessions=total_sessions,
                ums_count=1,  # Registration counts as first session
            )
            # Create new registration for new member
            registration = reg_serializer.save(member=member)
        else:
            # Update existing member with gender, invited_by, and membership info
            member.gender = gender
            member.invited_by = invited_by
            member.membership = membership_type
            member.membership_total_sessions = total_sessions
            # Only set ums_count to 1 if it's currently 0
            if member.ums_count == 0:
                member.ums_count = 1
            member.save(update_fields=['gender', 'invited_by', 'membership', 'membership_total_sessions', 'ums_count', 'updated_at'])
            
            # Check if member already has a registration (OneToOne relationship)
            try:
                registration = member.registration
                # Update existing registration with new data
                for key, value in reg_serializer.validated_data.items():
                    if key != 'member':  # Don't update the member field
                        setattr(registration, key, value)
                registration.save()
            except Registration.DoesNotExist:
                # Create new registration if member doesn't have one
                registration = reg_serializer.save(member=member)

        # Update member financials
        member.total_paid = Decimal(member.total_paid or 0) + initial_paid
        member.balance = plan_total - Decimal(member.total_paid)

        # Validate & save body component
        body_data['member'] = member.id
        body_serializer = BodyComponentEvaluationSerializer(data=body_data)
        body_serializer.is_valid(raise_exception=True)
        body_obj = body_serializer.save(member=member)
        
        # Calculate and update fat, fluids, and analysis_data
        body_obj = calculate_body_analysis(body_obj, registration)
        body_obj.save()

        # Update member latest metrics
        member.latest_weight = body_obj.weight_kg
        member.latest_height = body_obj.height_cm
        member.save(update_fields=['latest_weight', 'latest_height', 'total_paid', 'balance', 'updated_at'])

        # Create initial Payment record if paid > 0
        if initial_paid > 0:
            Payment.objects.create(
                member=member,
                amount=initial_paid,
                date=registration.created_at.date() if registration.created_at else timezone.now().date(),
                method='registration',
                notes='Initial amount paid at registration'
            )

        # Return combined response
        response = {
            "member": MemberSerializer(member).data,
            "registration": RegistrationSerializer(registration).data,
            "body_evaluation": BodyComponentEvaluationSerializer(body_obj).data
        }
        return Response(response, status=201)

    def retrieve(self, request, pk=None):
        registration = get_object_or_404(Registration, pk=pk)
        return Response(RegistrationSerializer(registration).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def attendance_submit(request):
    """
    Atomic submission of attendance entries with payments.
    
    Expected JSON:
    {
      "date": "2025-11-26",
      "entries": [
         {"member_id": 12, "present": true, "paid_amount": 0},
         {"member_id": 28, "present": true, "paid_amount": 500, "method": "cash", "notes": ""}
      ]
    }
    
    Returns:
    {
      "status": "ok",
      "submitted_count": 2,
      "total_received": 500.00
    }
    """
    data = request.data
    date_str = data.get('date')
    entries = data.get('entries', [])
    submitted_by = request.user

    if not date_str:
        date_str = timezone.now().date()

    created = []
    total_received = Decimal('0.00')

    try:
        with transaction.atomic():
            for e in entries:
                member = get_object_or_404(Member, pk=e['member_id'])
                present = bool(e.get('present', False))
                paid_amount = Decimal(str(e.get('paid_amount', 0) or 0))
                
                # Check if attendance already exists and what the previous state was
                existing_attendance = Attendance.objects.filter(member=member, date=date_str).first()
                was_present_before = existing_attendance.present if existing_attendance else False
                
                # Create or update attendance record
                obj, created_flag = Attendance.objects.update_or_create(
                    member=member, 
                    date=date_str,
                    defaults={
                        'present': present,
                        'paid_amount': paid_amount,
                        'submitted_at': timezone.now(),
                        'submitted_by': submitted_by,
                        'notes': e.get('notes', '')
                    }
                )
                created.append(obj)
                
                # Increment UMS count only if:
                # 1. Present is True AND
                # 2. Either newly created OR changed from not present to present
                if present and (created_flag or (not created_flag and not was_present_before)):
                    member.ums_count += 1
                
                # Create payment record and update balances if payment made
                if paid_amount > 0:
                    Payment.objects.create(
                        member=member,
                        amount=paid_amount,
                        date=date_str,
                        method=e.get('method', 'cash'),
                        notes=e.get('notes', '')
                    )
                    # Update member balances
                    member.balance = Decimal(member.balance) - paid_amount
                    member.total_paid = Decimal(member.total_paid) + paid_amount
                    total_received += paid_amount
                
                member.save(update_fields=['balance', 'total_paid', 'ums_count', 'updated_at'])

        return Response({
            "status": "ok",
            "submitted_count": len(created),
            "total_received": float(total_received)
        })
    
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_daily_report(request):
    """
    Generate PDF report for daily attendance.
    GET /api/report/daily?date=YYYY-MM-DD
    """
    date_str = request.GET.get('date')
    if date_str:
        report_date = date_str
    else:
        report_date = timezone.now().date().isoformat()

    attendances = Attendance.objects.filter(
        date=report_date, 
        present=True
    ).select_related('member').order_by('member__full_name')
    
    total_present = attendances.count()
    total_received = sum([Decimal(a.paid_amount) for a in attendances])

    context = {
        'date': report_date,
        'attendances': attendances,
        'total_present': total_present,
        'total_received': total_received,
        'org_name': 'Membership Management System',
    }

    html_string = render_to_string('report_daily.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="daily_report_{report_date}.pdf"'
    return response


@api_view(['GET'])
def dashboard_stats(request):
    """Get dashboard statistics"""
    total_members = Member.objects.count()
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(date=today, present=True).count()
    total_balance = sum([m.balance for m in Member.objects.all()])
    
    return Response({
        'total_members': total_members,
        'today_attendance': today_attendance,
        'total_outstanding_balance': float(total_balance),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_registration_analysis(request, registration_id):
    """
    Generate comprehensive analysis PDF report for a registration.
    Includes Health & Lifestyle Survey + Body Components Evaluation with all calculations.
    GET /api/reports/registration/<registration_id>/analysis/
    """
    try:
        registration = get_object_or_404(Registration, pk=registration_id)
        member = registration.member
        
        # Get the latest body evaluation for this member
        body_eval = member.body_evaluations.first()
        
        if not body_eval:
            return Response({
                "detail": "No body evaluation found for this registration"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Prepare analysis data from the stored JSON
        analysis = body_eval.analysis_data or {}
        
        context = {
            'registration': registration,
            'member': member,
            'body_eval': body_eval,
            'analysis': analysis,
            'org_name': 'Y.Lakshmi Health & Lifestyle',
        }
        
        # Render HTML template
        html_string = render_to_string('analysis_report.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()
        
        # Return PDF response with attachment disposition to force download
        response = HttpResponse(pdf, content_type='application/pdf')
        # Sanitize filename by replacing spaces and special characters
        safe_name = registration.guest_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        response['Content-Disposition'] = f'attachment; filename="analysis_{safe_name}_{registration_id}.pdf"'
        return response
        
    except Exception as e:
        return Response({
            "detail": f"Error generating PDF: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def health_check(request):
    """Health check endpoint for load balancers"""
    return Response({'status': 'healthy', 'timestamp': timezone.now()})


# Note: search endpoint provided via MemberViewSet.search action


@api_view(['GET'])
@permission_classes([AllowAny])
def body_checkup_data(request, member_id):
    """
    Get body checkup data for a specific member organized by weeks.
    GET /api/body-checkup/<member_id>/
    
    Returns member info and checkup data organized by weeks (1-16).
    """
    member = get_object_or_404(Member, pk=member_id)
    
    # Get all checkups for this member ordered by date
    checkups = Checkup.objects.filter(member=member).order_by('checkup_date')
    
    # Organize checkups by week (assuming weekly checkups starting from registration date)
    registration_date = member.registration_date
    weeks = {}
    
    for checkup in checkups:
        # Calculate week number based on days since registration
        days_diff = (checkup.checkup_date - registration_date).days
        week_num = (days_diff // 7) + 1  # Week 1, 2, 3, etc.
        
        if 1 <= week_num <= 16:
            # Extract data from category_data JSON field
            category_data = checkup.category_data or {}
            
            weeks[week_num] = {
                'date': checkup.checkup_date.strftime('%Y-%m-%d'),
                'data': {
                    'age': category_data.get('age', ''),
                    'height': str(checkup.height) if checkup.height else '',
                    'weight': str(checkup.weight) if checkup.weight else '',
                    'body_fat': category_data.get('body_fat', ''),
                    'bma': category_data.get('bma', ''),
                    'bmi': category_data.get('bmi', ''),
                    'bmr': category_data.get('bmr', ''),
                    'visceral_fat': category_data.get('visceral_fat', ''),
                    'subcutaneous_fat': category_data.get('subcutaneous_fat', ''),
                    'muscle_mass': category_data.get('muscle_mass', ''),
                }
            }

    # Ensure Week 1 is prefilled from registration/body evaluation if not present
    if 1 not in weeks:
        # Registration date as Week 1 date
        week1_date = registration_date.strftime('%Y-%m-%d') if registration_date else ''
        # Latest body evaluation (at registration)
        body_eval = member.body_evaluations.first()
        weeks[1] = {
            'date': week1_date,
            'data': {
                'age': str(member.registration.age) if hasattr(member, 'registration') and member.registration and member.registration.age is not None else '',
                'height': str(body_eval.height_cm) if body_eval and body_eval.height_cm is not None else '',
                'weight': str(body_eval.weight_kg) if body_eval and body_eval.weight_kg is not None else '',
                'body_fat': str(body_eval.body_fat_men or body_eval.body_fat_women) if body_eval else '',
                'bma': str(body_eval.body_age) if body_eval and body_eval.body_age is not None else '',
                'bmi': str(body_eval.bmi) if body_eval and body_eval.bmi is not None else '',
                'bmr': str(body_eval.bmr_rm) if body_eval and body_eval.bmr_rm is not None else '',
                'visceral_fat': str(body_eval.visceral_fat) if body_eval and body_eval.visceral_fat is not None else '',
                'subcutaneous_fat': str(body_eval.trunk_subcutaneous_fat) if body_eval and body_eval.trunk_subcutaneous_fat is not None else '',
                'muscle_mass': str(body_eval.skeletal_muscle_men or body_eval.skeletal_muscle_women) if body_eval else '',
            }
        }
    
    # Build response
    # Determine locked weeks: Week 1 always locked; any week with a Checkup record is locked
    locked_weeks = {1: True}
    for w in weeks.keys():
        if w != 1:
            # compute date for week
            # locked if a checkup exists matching that week
            # already gathered above by checkups loop; if week data exists from DB, treat as locked
            # heuristic: if week came from DB (has possible values), lock it
            # we mark weeks that were loaded from checkups as locked
            pass
    # Build response
    response_data = {
        'member': {
            'id': member.id,
            'full_name': member.full_name,
            'phone': member.phone,
            'registration_date': member.registration_date.strftime('%Y-%m-%d') if member.registration_date else '',
            'invited_by': member.invited_by or '',
            'gender': member.gender or '',
        },
        'weeks': weeks,
        'locked_weeks': sorted(list({1}.union(set([( ( ( (checkup.checkup_date - registration_date).days // 7) + 1) ) for checkup in checkups if 1 <= ( (checkup.checkup_date - registration_date).days // 7) + 1 <= 16 ]))))
    }
    
    return Response(response_data)


@api_view(['POST'])
@permission_classes([AllowAny])
def body_checkup_save(request, member_id):
    """
    Save body checkup data for a member.
    POST /api/body-checkup/<member_id>/save/
    
    Expected JSON:
    {
      "checkup_data": [
        {
          "week": 1,
          "data": {
            "age": "25",
            "height": "170",
            "weight": "70",
            "body_fat": "20",
            ...
          }
        },
        ...
      ]
    }
    """
    member = get_object_or_404(Member, pk=member_id)
    checkup_data = request.data.get('checkup_data', [])
    
    if not checkup_data:
        return Response({'detail': 'No checkup data provided'}, status=400)
    
    registration_date = member.registration_date
    
    try:
        with transaction.atomic():
            for week_entry in checkup_data:
                week_num = week_entry.get('week')
                data = week_entry.get('data', {})
                
                if not week_num or not data:
                    continue
                
                # Calculate checkup date based on week number; allow override from payload
                provided_date = week_entry.get('date')
                if provided_date:
                    checkup_date = timezone.datetime.fromisoformat(provided_date).date()
                else:
                    checkup_date = registration_date + timezone.timedelta(days=(week_num - 1) * 7)
                
                # Extract height and weight
                height = data.get('height', '')
                weight = data.get('weight', '')
                
                # Prepare category_data (all other fields)
                category_data = {
                    'age': data.get('age', ''),
                    'body_fat': data.get('body_fat', ''),
                    'bma': data.get('bma', ''),
                    'bmi': data.get('bmi', ''),
                    'bmr': data.get('bmr', ''),
                    'visceral_fat': data.get('visceral_fat', ''),
                    'subcutaneous_fat': data.get('subcutaneous_fat', ''),
                    'muscle_mass': data.get('muscle_mass', ''),
                }
                
                # Create or update checkup
                checkup, created = Checkup.objects.update_or_create(
                    member=member,
                    checkup_date=checkup_date,
                    defaults={
                        'weight': Decimal(weight) if weight else None,
                        'height': Decimal(height) if height else None,
                        'category_data': category_data,
                    }
                )
                
                # Update member's latest metrics if this is the most recent checkup
                if weight:
                    member.latest_weight = Decimal(weight)
                if height:
                    member.latest_height = Decimal(height)
            
            member.save(update_fields=['latest_weight', 'latest_height', 'updated_at'])
        
        return Response({'status': 'success', 'message': 'Checkup data saved successfully'})
    
    except Exception as e:
        return Response({'detail': f'Error saving data: {str(e)}'}, status=400)
