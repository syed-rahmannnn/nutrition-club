from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Member
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Load sample member data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of sample members to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        sample_names = [
            'Rajesh Kumar', 'Priya Sharma', 'Amit Singh', 'Sneha Patel', 'Vikram Rao',
            'Anita Gupta', 'Rahul Verma', 'Kavita Jain', 'Suresh Reddy', 'Meera Shah',
            'Arun Kumar', 'Deepika Singh', 'Sanjay Agarwal', 'Pooja Tiwari', 'Manoj Yadav',
            'Ritu Malhotra', 'Kiran Dubey', 'Nikhil Chopra', 'Swati Bansal', 'Rohit Saxena'
        ]
        
        genders = ['Male', 'Female']
        
        created_count = 0
        for i in range(count):
            name = sample_names[i % len(sample_names)]
            if i >= len(sample_names):
                name = f"{name} {i // len(sample_names)}"
            
            member_code = f"M{str(i+1).zfill(3)}"
            phone = f"9{random.randint(100000000, 999999999)}"
            gender = random.choice(genders)
            balance = Decimal(random.randint(0, 1000))
            ums_count = random.randint(0, 50)
            
            # Check if member already exists
            if not Member.objects.filter(member_code=member_code).exists():
                Member.objects.create(
                    member_code=member_code,
                    full_name=name,
                    phone=phone,
                    gender=gender,
                    balance=balance,
                    ums_count=ums_count,
                    invited_by=f"Referral {random.randint(1, 10)}"
                )
                created_count += 1
        
        # Create a superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@localhost.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('Created superuser: admin/admin123')
            )
        
        # Create a regular user for API testing
        if not User.objects.filter(username='operator').exists():
            User.objects.create_user(
                username='operator',
                email='operator@localhost.com',
                password='operator123'
            )
            self.stdout.write(
                self.style.SUCCESS('Created operator user: operator/operator123')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} members')
        )
        
        total_members = Member.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'Total members in database: {total_members}')
        )