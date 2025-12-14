from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import date
import json
from .models import Member, Attendance, Payment, Registration, BodyComponentEvaluation


class AttendanceSubmitTest(TestCase):
    """Test cases for attendance submission endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='operator', password='testpass123')
        self.client = APIClient()
        self.client.login(username='operator', password='testpass123')
        
        # Create test members
        self.member1 = Member.objects.create(
            member_code='M001',
            full_name='John Doe',
            phone='1234567890',
            balance=Decimal('100.00'),
            ums_count=5
        )
        
        self.member2 = Member.objects.create(
            member_code='M002',
            full_name='Jane Smith',
            phone='0987654321',
            balance=Decimal('0.00'),
            ums_count=3
        )
    
    def test_submit_attendance_with_payment(self):
        """Test submitting attendance with payment"""
        payload = {
            "date": "2025-11-26",
            "entries": [
                {
                    "member_id": self.member1.id,
                    "present": True,
                    "paid_amount": 50
                }
            ]
        }
        
        response = self.client.post('/api/attendance/submit/', payload, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['submitted_count'], 1)
        self.assertEqual(response.data['total_received'], 50.0)
        
        # Verify member balance updated
        self.member1.refresh_from_db()
        self.assertEqual(float(self.member1.balance), 50.0)
        self.assertEqual(float(self.member1.total_paid), 50.0)
        self.assertEqual(self.member1.ums_count, 6)
        
        # Verify attendance created
        attendance = Attendance.objects.get(member=self.member1, date="2025-11-26")
        self.assertTrue(attendance.present)
        self.assertEqual(float(attendance.paid_amount), 50.0)
        
        # Verify payment created
        payment = Payment.objects.get(member=self.member1, date="2025-11-26")
        self.assertEqual(float(payment.amount), 50.0)
    
    def test_submit_attendance_without_payment(self):
        """Test submitting attendance without payment"""
        payload = {
            "date": "2025-11-26",
            "entries": [
                {
                    "member_id": self.member2.id,
                    "present": True,
                    "paid_amount": 0
                }
            ]
        }
        
        response = self.client.post('/api/attendance/submit/', payload, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_received'], 0.0)
        
        # Verify no payment created
        self.assertEqual(Payment.objects.filter(member=self.member2).count(), 0)
        
        # Verify UMS count increased
        self.member2.refresh_from_db()
        self.assertEqual(self.member2.ums_count, 4)
    
    def test_submit_multiple_attendances(self):
        """Test submitting multiple attendance entries at once"""
        payload = {
            "date": "2025-11-26",
            "entries": [
                {
                    "member_id": self.member1.id,
                    "present": True,
                    "paid_amount": 50
                },
                {
                    "member_id": self.member2.id,
                    "present": True,
                    "paid_amount": 30
                }
            ]
        }
        
        response = self.client.post('/api/attendance/submit/', payload, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['submitted_count'], 2)
        self.assertEqual(response.data['total_received'], 80.0)
        
        # Verify both attendances created
        self.assertEqual(Attendance.objects.filter(date="2025-11-26").count(), 2)
        self.assertEqual(Payment.objects.count(), 2)
    
    def test_update_existing_attendance(self):
        """Test updating an existing attendance record"""
        # Create initial attendance
        Attendance.objects.create(
            member=self.member1,
            date="2025-11-26",
            present=True,
            paid_amount=Decimal('0.00')
        )
        
        # Update with payment
        payload = {
            "date": "2025-11-26",
            "entries": [
                {
                    "member_id": self.member1.id,
                    "present": True,
                    "paid_amount": 50
                }
            ]
        }
        
        response = self.client.post('/api/attendance/submit/', payload, format='json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify only one attendance record exists
        self.assertEqual(Attendance.objects.filter(member=self.member1, date="2025-11-26").count(), 1)
        
        # Verify payment was updated
        attendance = Attendance.objects.get(member=self.member1, date="2025-11-26")
        self.assertEqual(float(attendance.paid_amount), 50.0)
    
    def test_authentication_required(self):
        """Test that authentication is required"""
        self.client.logout()
        
        payload = {
            "date": "2025-11-26",
            "entries": []
        }
        
        response = self.client.post('/api/attendance/submit/', payload, format='json')
        self.assertEqual(response.status_code, 403)


class MemberAPITest(TestCase):
    """Test cases for Member API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='operator', password='testpass123')
        self.client = APIClient()
        self.client.login(username='operator', password='testpass123')
        
        Member.objects.create(
            member_code='M001',
            full_name='John Doe',
            phone='1234567890'
        )
        
        Member.objects.create(
            member_code='M002',
            full_name='Jane Smith',
            phone='0987654321'
        )
    
    def test_list_members(self):
        """Test listing all members"""
        response = self.client.get('/api/members/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_search_members(self):
        """Test searching members by name or phone"""
        response = self.client.get('/api/members/?search=John')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'John Doe')
        
        response = self.client.get('/api/members/?search=0987')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['phone'], '0987654321')
    
    def test_retrieve_member(self):
        """Test retrieving a single member"""
        member = Member.objects.first()
        response = self.client.get(f'/api/members/{member.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['full_name'], member.full_name)
    
    def test_create_member(self):
        """Test creating a new member"""
        payload = {
            'member_code': 'M003',
            'full_name': 'Bob Johnson',
            'phone': '5555555555',
            'gender': 'Male',
            'registration_date': '2025-12-07'
        }
        
        response = self.client.post('/api/members/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Member.objects.count(), 3)
        
        member = Member.objects.get(member_code='M003')
        self.assertEqual(member.full_name, 'Bob Johnson')


class RegistrationAPITest(TestCase):
    """Test cases for Registration API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
    
    def test_create_registration_and_body_eval(self):
        """Test creating a complete registration with body evaluation"""
        payload = {
            "registration": {
                "guest_name": "Test User",
                "mobile_number": "9000000000",
                "invited_by": "John Doe",
                "gender": "Male",
                "membership": "UMS",
                "occupation": "Test Occupation",
                "age": 30,
                "location": "",
                "do_you_exercise": "Walking",
                "hours_sleep": "7",
                "liters_water": "2L",
                "loss_of_energy": "No",
                "transformation_targets": "Weight Targets",
                "tried_diet_programs": False,
                "surveyed_by": "Operator A",
                "available_time": "8-11 AM"
            },
            "body_evaluation": {
                "height_cm": 160,
                "weight_kg": 70,
                "visceral_fat": 12,
                "fat": 20,
                "fluids": 55
            }
        }
        
        resp = self.client.post('/api/registrations/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        
        data = resp.json()
        self.assertIn('member', data)
        self.assertIn('registration', data)
        self.assertIn('body_evaluation', data)
        
        # Verify member was created
        self.assertTrue(Member.objects.filter(phone='9000000000').exists())
        member = Member.objects.get(phone='9000000000')
        self.assertEqual(member.full_name, 'Test User')
        self.assertEqual(float(member.latest_weight), 70.0)
        self.assertEqual(float(member.latest_height), 160.0)
        
        # Verify registration was created
        self.assertTrue(Registration.objects.filter(member=member).exists())
        registration = Registration.objects.get(member=member)
        self.assertEqual(registration.guest_name, 'Test User')
        self.assertEqual(registration.occupation, 'Test Occupation')
        self.assertEqual(registration.do_you_exercise, 'Walking')
        
        # Verify body evaluation was created
        self.assertTrue(BodyComponentEvaluation.objects.filter(member=member).exists())
        body_eval = BodyComponentEvaluation.objects.get(member=member)
        self.assertEqual(float(body_eval.height_cm), 160.0)
        self.assertEqual(float(body_eval.weight_kg), 70.0)
        self.assertEqual(float(body_eval.fat), 20.0)
        self.assertEqual(float(body_eval.fluids), 55.0)
    
    def test_create_registration_with_full_data(self):
        """Test creating registration with complete survey data"""
        payload = {
            "registration": {
                "guest_name": "Shaik Naseemunn",
                "mobile_number": "9000781488",
                "invited_by": "Referral",
                "gender": "Female",
                "membership": "UMS",
                "occupation": "Sweet Business",
                "age": 45,
                "location": "Aagari",
                "do_you_exercise": "Walking",
                "hours_sleep": "12pm to 9am",
                "liters_water": "2L",
                "loss_of_energy": "Occasionally",
                "veg_nonveg": "Non-Veg",
                "personal_health_history": {"bp": "high", "diabetes": "no"},
                "transformation_targets": "Fitness;Good energy level",
                "tried_diet_programs": False,
                "surveyed_by": "Y. Lakshmi",
                "available_time": "8-11 AM"
            },
            "body_evaluation": {
                "height_cm": 144,
                "weight_kg": 76.3,
                "visceral_fat": 22,
                "trunk_subcutaneous_fat": 41.4,
                "body_fat_women": 42.4,
                "body_age": 65,
                "bmi": 36.8,
                "bmr_rm": 1449,
                "skeletal_muscle_women": 20,
                "fat": 9,
                "fluids": 19.3
            }
        }
        
        resp = self.client.post('/api/registrations/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        
        data = resp.json()
        member = Member.objects.get(phone='9000781488')
        
        # Verify all registration fields
        registration = Registration.objects.get(member=member)
        self.assertEqual(registration.location, 'Aagari')
        self.assertEqual(registration.veg_nonveg, 'Non-Veg')
        self.assertEqual(registration.personal_health_history['bp'], 'high')
        
        # Verify all body evaluation fields
        body_eval = BodyComponentEvaluation.objects.get(member=member)
        self.assertEqual(float(body_eval.trunk_subcutaneous_fat), 41.4)
        self.assertEqual(float(body_eval.body_fat_women), 42.4)
        self.assertEqual(float(body_eval.bmi), 36.8)
    
    def test_registration_missing_required_fields(self):
        """Test that missing required fields cause validation error"""
        payload = {
            "registration": {
                "guest_name": "Test User",
                "invited_by": "Someone",
                "gender": "Male",
                "membership": "TRIAL",
                # missing mobile_number
                "occupation": "Test",
                "age": 25
            },
            "body_evaluation": {
                "height_cm": 160,
                "weight_kg": 70,
                "visceral_fat": 12,
                "fat": 20,
                "fluids": 55
            }
        }
        
        resp = self.client.post('/api/registrations/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        # Verify that required fields are in the error response
        error_data = resp.json()
        self.assertTrue('mobile_number' in error_data or 'missing_fields' in error_data)
    
    def test_body_eval_missing_required_fields(self):
        """Test that missing body evaluation required fields cause validation error"""
        payload = {
            "registration": {
                "guest_name": "Test User",
                "mobile_number": "9000000001",
                "invited_by": "Friend",
                "gender": "Female",
                "membership": "UMS",
                "occupation": "Test",
                "age": 28,
                "do_you_exercise": "Walking",
                "hours_sleep": "7",
                "liters_water": "2L",
                "loss_of_energy": "No",
                "transformation_targets": "Weight Targets",
                "tried_diet_programs": False,
                "surveyed_by": "Operator",
                "available_time": "8-11 AM"
            },
            "body_evaluation": {
                "height_cm": 160,
                # missing weight_kg, visceral_fat, fat, fluids
            }
        }
        
        resp = self.client.post('/api/registrations/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
    
    def test_existing_member_registration(self):
        """Test that registration links to existing member if phone matches"""
        # Create existing member
        existing_member = Member.objects.create(
            member_code='M999',
            full_name='Existing Member',
            phone='9999999999'
        )
        
        payload = {
            "registration": {
                "guest_name": "Updated Name",
                "mobile_number": "9999999999",  # Same phone as existing member
                "invited_by": "Friend",
                "gender": "Male",
                "membership": "TRIAL",
                "occupation": "Test",
                "age": 35,
                "do_you_exercise": "Yoga",
                "hours_sleep": "8",
                "liters_water": "3L",
                "loss_of_energy": "No",
                "transformation_targets": "Fitness",
                "tried_diet_programs": True,
                "surveyed_by": "Operator",
                "available_time": "Morning"
            },
            "body_evaluation": {
                "height_cm": 170,
                "weight_kg": 75,
                "visceral_fat": 10,
                "fat": 18,
                "fluids": 60
            }
        }
        
        resp = self.client.post('/api/registrations/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        
        # Verify only one member exists with this phone
        self.assertEqual(Member.objects.filter(phone='9999999999').count(), 1)
        
        # Verify registration is linked to existing member
        registration = Registration.objects.get(mobile_number='9999999999')
        self.assertEqual(registration.member.id, existing_member.id)
    
    def test_retrieve_registration(self):
        """Test retrieving a registration by ID"""
        # Create a registration first
        payload = {
            "registration": {
                "guest_name": "Test User",
                "mobile_number": "9000000002",
                "invited_by": "Direct",
                "gender": "Other",
                "membership": "TRIAL",
                "occupation": "Test",
                "age": 32,
                "do_you_exercise": "Walking",
                "hours_sleep": "7",
                "liters_water": "2L",
                "loss_of_energy": "No",
                "transformation_targets": "Weight Targets",
                "tried_diet_programs": False,
                "surveyed_by": "Operator",
                "available_time": "8-11 AM"
            },
            "body_evaluation": {
                "height_cm": 160,
                "weight_kg": 70,
                "visceral_fat": 12,
                "fat": 20,
                "fluids": 55
            }
        }
        
        create_resp = self.client.post('/api/registrations/', data=json.dumps(payload), content_type='application/json')
        registration_id = create_resp.json()['registration']['id']
        
        # Retrieve the registration
        get_resp = self.client.get(f'/api/registrations/{registration_id}/')
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()['guest_name'], 'Test User')
