from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


MEMBERSHIP_CHOICES = (
    ('TRIAL', 'Trial'),
    ('UMS', 'UMS'),
    ('COMPLEMENT', 'Complement'),
    ('OTHERS', 'Others'),
)


class Member(models.Model):
    member_code = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True, null=True)
    gender = models.CharField(max_length=16, blank=True, null=True)
    invited_by = models.CharField(max_length=255, blank=True, null=True)
    registration_date = models.DateField(default=timezone.now)
    membership = models.CharField(max_length=16, choices=MEMBERSHIP_CHOICES, blank=True, null=True)
    membership_total_sessions = models.IntegerField(default=0)
    ums_count = models.IntegerField(default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    latest_weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    latest_height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    next_checkup_date = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    class Meta:
        ordering = ['full_name']


class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    present = models.BooleanField(default=False)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    submitted_at = models.DateTimeField(blank=True, null=True)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('member', 'date')
        ordering = ['-date', 'member__full_name']

    def __str__(self):
        return f"{self.member.full_name} - {self.date} - {'Present' if self.present else 'Absent'}"


class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    method = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.member.full_name} - ₹{self.amount} - {self.date}"


class Checkup(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='checkups')
    checkup_date = models.DateField(default=timezone.now)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    category_data = models.JSONField(blank=True, null=True)  # store measurements as JSON
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-checkup_date']

    def __str__(self):
        return f"{self.member.full_name} - Checkup {self.checkup_date}"


class Registration(models.Model):
    """
    Stores the initial health & lifestyle survey form for a member.
    """
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='registration', null=True, blank=True)
    guest_name = models.CharField(max_length=255)                   # mandatory
    mobile_number = models.CharField(max_length=32)                 # mandatory
    invited_by = models.CharField(max_length=255, default='')       # mandatory
    gender = models.CharField(max_length=16, default='Other')       # mandatory (\"Male\", \"Female\", \"Other\")
    membership = models.CharField(max_length=16, choices=MEMBERSHIP_CHOICES, default='UMS')  # mandatory
    occupation = models.CharField(max_length=255)                   # mandatory
    age = models.IntegerField(default=0)                            # mandatory
    location = models.CharField(max_length=255, blank=True, null=True)  # optional

    # Question set (first form)
    do_you_exercise = models.CharField(max_length=64)               # mandatory (e.g., "Yoga/Gym/Walking/None")
    hours_sleep = models.CharField(max_length=64)                   # mandatory (free text)
    liters_water = models.CharField(max_length=64)                  # mandatory (free text)
    loss_of_energy = models.CharField(max_length=32)                # mandatory ("Yes"/"No"/"Occasionally")
    veg_nonveg = models.CharField(max_length=32, blank=True, null=True)  # optional
    # personal health history can be stored as JSON (optional)
    personal_health_history = models.JSONField(blank=True, null=True)

    # transformation choices
    transformation_targets = models.CharField(max_length=255)       # mandatory (example: "Weight Targets;Fitness")

    tried_diet_programs = models.BooleanField(default=False)        # mandatory (True/False)
    surveyed_by = models.CharField(max_length=255)                  # mandatory
    available_time = models.CharField(max_length=255)               # mandatory
    
    # Number of days field - only required when membership is 'OTHERS'
    number_of_days = models.IntegerField(blank=True, null=True)     # optional, required only for OTHERS membership

    # Payment fields
    plan_total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)       # total payable for the membership
    initial_amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)     # amount paid at registration

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Registration - {self.guest_name}"


class BodyComponentEvaluation(models.Model):
    """
    Stores body components evaluation data (one or many evaluations per member).
    All fields are mandatory for a registration record per your requirement.
    We'll add fat and fluids as requested.
    """

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='body_evaluations')
    date = models.DateField(auto_now_add=True)

    # core measurements (use DECIMAL for numeric precision)
    height_cm = models.DecimalField(max_digits=6, decimal_places=2)  # e.g., 144.00
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    visceral_fat = models.DecimalField(max_digits=5, decimal_places=2)
    trunk_subcutaneous_fat = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    body_fat_men = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    body_fat_women = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    body_age = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    bmr_rm = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    skeletal_muscle_men = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    skeletal_muscle_women = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Extra fields requested - computed automatically in backend
    fat = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fluids = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # Store all calculated analysis data (differences, min/max weight, etc.)
    analysis_data = models.JSONField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.member.full_name} - Body Eval {self.date}"
