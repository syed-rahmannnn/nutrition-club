# Membership Management System

A comprehensive Django-based membership management system with attendance tracking, payment management, body checkup records, and PDF report generation.

## Features

- **Member Management**: Create, update, and search member records
- **UMS Attendance**: Daily attendance tracking with pending/tick UX
- **Payment Tracking**: Record payments and update member balances automatically
- **Body Checkup**: Track member health checkups with measurements
- **PDF Reports**: Generate daily attendance reports with WeasyPrint
- **RESTful API**: Full REST API with Django REST Framework
- **Modern UI**: Responsive Tailwind CSS interface

## Project Structure

```
membership-management/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/                # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── core/                  # Main application
│       ├── models.py          # Database models
│       ├── serializers.py     # DRF serializers
│       ├── views.py           # API views
│       ├── urls.py            # API routes
│       ├── admin.py           # Django admin
│       ├── tests.py           # Unit tests
│       ├── templates/         # HTML templates
│       │   ├── homepage.html
│       │   ├── ums_attendance.html
│       │   └── report_daily.html
│       └── static/
│           └── js/
│               └── ums.js     # UMS attendance client logic
└── README.md
```

## Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL 15
- **PDF Generation**: WeasyPrint
- **Frontend**: Tailwind CSS (CDN)
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- **Docker Desktop**: Download and install from https://www.docker.com/products/docker-desktop
- **Git** (optional): For cloning the repository

### Docker Installation Guide

1. **Windows**: 
   - Download Docker Desktop for Windows
   - Run the installer and follow setup wizard
   - Restart your computer if prompted
   - Verify installation: `docker --version`

2. **macOS**:
   - Download Docker Desktop for Mac
   - Drag Docker.app to Applications folder
   - Launch Docker Desktop and wait for it to start
   - Verify installation: `docker --version`

3. **Linux**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   # Logout and login again
   ```

### Installation

#### Option 1: Automated Setup (Recommended)

**Windows:**
```cmd
cd c:\Users\syedr\Desktop\test_website
setup.bat
```

**Linux/macOS:**
```bash
cd /path/to/test_website
chmod +x setup.sh
./setup.sh
```

#### Option 2: Manual Setup

1. **Navigate to project directory**
   ```cmd
   cd c:\Users\syedr\Desktop\test_website
   ```

2. **Build and start services**
   ```cmd
   docker-compose up --build
   ```

3. **Run migrations (in new terminal)**
   ```cmd
   docker-compose exec web python manage.py migrate
   ```

4. **Create sample data**
   ```cmd
   docker-compose exec web python manage.py seed_data --count 20
   ```

5. **Create superuser**
   ```cmd
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access the application**
   - **Homepage**: http://localhost:8000/
   - **Admin Panel**: http://localhost:8000/admin/
   - **API Root**: http://localhost:8000/api/

#### Default Credentials (if using seed_data)
- **Admin**: admin / admin123
- **Operator**: operator / operator123

## Database Models

### Member
- `member_code`: Unique identifier
- `full_name`: Member's full name
- `phone`: Contact number
- `gender`: Gender
- `invited_by`: Referral information
- `registration_date`: Date of registration
- `ums_count`: UMS attendance count
- `balance`: Outstanding balance
- `total_paid`: Total amount paid
- `latest_weight`, `latest_height`: Health metrics
- `next_checkup_date`: Scheduled checkup
- `profile_image`: Profile photo

### Attendance
- `member`: Foreign key to Member
- `date`: Attendance date
- `present`: Boolean flag
- `paid_amount`: Payment made on this date
- `submitted_at`: Submission timestamp
- `submitted_by`: User who submitted
- `notes`: Additional notes

### Payment
- `member`: Foreign key to Member
- `amount`: Payment amount
- `date`: Payment date
- `method`: Payment method (cash, online, etc.)
- `notes`: Additional notes

### Checkup
- `member`: Foreign key to Member
- `checkup_date`: Date of checkup
- `weight`, `height`: Body measurements
- `category_data`: JSON field for custom measurements
- `notes`: Additional notes

### Registration
- `member`: One-to-one with Member
- `reg_date`: Registration date
- `answers`: JSON field for registration questionnaire

## API Endpoints

### Members
- `GET /api/members/` - List all members (supports `?search=` query)
- `POST /api/members/` - Create new member
- `GET /api/members/<id>/` - Retrieve member details
- `PUT/PATCH /api/members/<id>/` - Update member
- `DELETE /api/members/<id>/` - Delete member

### Attendance
- `GET /api/attendances/` - List attendance records
- `POST /api/attendance/submit/` - Submit attendance (atomic transaction)
  ```json
  {
    "date": "2025-11-26",
    "entries": [
      {
        "member_id": 12,
        "present": true,
        "paid_amount": 500,
        "method": "cash",
        "notes": ""
      }
    ]
  }
  ```

### Reports
- `GET /api/report/daily/?date=YYYY-MM-DD` - Generate PDF report

### Payments
- `GET /api/payments/` - List payments
- `POST /api/payments/` - Create payment

### Checkups
- `GET /api/checkups/` - List checkups
- `POST /api/checkups/` - Create checkup

### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics

## UMS Attendance Workflow

The UMS attendance page implements a "pending tick" UX:

1. **Search**: Find members by name or phone
2. **Select**: Check the "Present" checkbox for attending members
3. **Payment**: Enter payment amount (if any) - input is enabled only when checked
4. **Pending List**: Selected entries appear in the right sidebar
5. **Submit**: Click "Submit Attendance" to save all entries atomically
6. **PDF Report**: Click "Generate PDF" to download the daily report

### Features:
- Atomic transaction ensures all-or-nothing submission
- Automatic balance calculation (balance -= paid_amount)
- UMS count increment for present members
- Payment record creation for non-zero amounts
- Real-time pending list updates

## Running Tests

```powershell
# Run all tests
docker-compose exec web python manage.py test

# Run specific test class
docker-compose exec web python manage.py test core.tests.AttendanceSubmitTest

# Run with coverage (install coverage first)
docker-compose exec web pip install coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## Development Commands

```powershell
# Make migrations
docker-compose exec web python manage.py makemigrations

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access Django shell
docker-compose exec web python manage.py shell

# Collect static files (for production)
docker-compose exec web python manage.py collectstatic

# View logs
docker-compose logs -f web
```

## Production Deployment

### Environment Variables

Create a `.env` file in the backend directory:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=0
DATABASE_URL=postgres://user:pass@host:5432/dbname
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Deployment Platforms

**Render / Railway / DigitalOcean App Platform**:
1. Connect your repository
2. Set environment variables
3. Use the Dockerfile for deployment
4. Add managed PostgreSQL database
5. Configure static/media file storage (S3/Spaces)

### Static Files

For production, use django-storages with S3:

```python
# settings.py
STATIC_URL = 'https://your-bucket.s3.amazonaws.com/static/'
MEDIA_URL = 'https://your-bucket.s3.amazonaws.com/media/'
```

### WeasyPrint on Production

WeasyPrint requires system libraries. Most platforms (Render, Railway) support them. If issues occur:
- Ensure `libcairo2`, `libpango-1.0-0`, `libgdk-pixbuf2.0-0` are installed
- Or use alternative PDF generation (Puppeteer/headless Chrome)

## Security Considerations

- Change `DJANGO_SECRET_KEY` in production
- Set `DEBUG=0` in production
- Use strong passwords for database and admin
- Configure `ALLOWED_HOSTS` properly
- Enable HTTPS/SSL
- Use environment variables for sensitive data
- Implement rate limiting for API endpoints
- Add proper CORS configuration

## Authentication

- Uses Django's built-in authentication
- Session authentication for web interface
- Token/Session authentication for API
- All API endpoints require authentication by default
- Admin panel access at `/admin/`

## Customization

### Adding New Fields to Member Model

1. Update `core/models.py`
2. Run `makemigrations` and `migrate`
3. Update serializers and forms as needed

### Custom PDF Template

Edit `core/templates/report_daily.html` to customize the PDF report layout.

### Adding New API Endpoints

1. Add view function or viewset in `core/views.py`
2. Register URL in `core/urls.py`
3. Add tests in `core/tests.py`

## Troubleshooting

**Database connection issues**:
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check DATABASE_URL environment variable

**WeasyPrint errors**:
- Verify system dependencies are installed in Dockerfile
- Check logs: `docker-compose logs web`

**Static files not loading**:
- Run `python manage.py collectstatic`
- Verify STATIC_URL and STATIC_ROOT settings

**CSRF token errors**:
- Ensure you're logged in for API requests
- Include CSRF token in POST requests from frontend

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

This project is open source. Adjust license as needed.

## Support

For issues and questions:
- Check the documentation above
- Review the code comments
- Open an issue on GitHub

## Roadmap

- [ ] Member photo upload and display
- [ ] Advanced reporting (monthly, custom date ranges)
- [ ] SMS/Email notifications
- [ ] Payment receipt generation
- [ ] Mobile app (React Native)
- [ ] Bulk operations (import/export CSV)
- [ ] Advanced search and filtering
- [ ] Dashboard analytics and charts

---

**Built with Django + DRF + PostgreSQL + Tailwind CSS**
