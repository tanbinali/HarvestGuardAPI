# HarvestGuard Backend

A Django REST API for managing crop harvests, tracking losses, and helping farmers in Bangladesh make data-driven decisions.

---

## 🎯 Overview

**HarvestGuard Backend** provides a robust REST API with:

- 🔐 JWT-based authentication
- 📊 Crop batch management
- ⚠️ Loss event tracking
- 🎯 Intervention system
- 🏆 Achievement/gamification system
- 📱 Mobile-first API design
- 📖 Auto-generated documentation (Swagger/ReDoc)
- 🔄 Flexible database support (SQLite/PostgreSQL)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- PostgreSQL (optional, SQLite used by default)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser for admin access (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000
```

**Development server**: http://localhost:8000

### Access Points

- **API Base**: http://localhost:8000/api/
- **Swagger UI**: http://localhost:8000/api/swagger/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Admin Panel**: http://localhost:8000/admin/

---

## 📁 Project Structure

```
HarvestGuard/
├── config/                      # Django project settings
│   ├── settings.py             # Main configuration
│   │   ├── DEBUG settings
│   │   ├── Database configuration
│   │   ├── ALLOWED_HOSTS & CORS
│   │   ├── REST Framework config
│   │   ├── JWT settings
│   │   ├── Cloudinary config
│   │   └── Static/Media files
│   ├── urls.py                 # Root URL routing
│   │   ├── /admin/            → Django admin
│   │   ├── /api/auth/         → Authentication endpoints
│   │   ├── /api/crops/        → Crop management
│   │   ├── /api/loss-events/  → Loss tracking
│   │   ├── /api/achievements/ → Achievements
│   │   ├── /api/swagger/      → API documentation
│   │   └── /api/redoc/        → API documentation
│   └── wsgi.py                 # WSGI application entry point
│
├── core/                        # Main Django application
│   ├── models.py               # Database models
│   │   ├── User                → Custom user model
│   │   ├── CropBatch           → Harvest batches
│   │   ├── LossEvent           → Crop losses
│   │   ├── Intervention        → Mitigation actions
│   │   └── Achievement         → User achievements
│   ├── serializers.py          # DRF serializers
│   │   ├── UserSerializer
│   │   ├── CropBatchSerializer
│   │   ├── LossEventSerializer
│   │   ├── InterventionSerializer
│   │   └── AchievementSerializer
│   ├── views.py                # API views
│   │   ├── UserViewSet
│   │   ├── CropBatchViewSet
│   │   ├── LossEventViewSet
│   │   ├── InterventionViewSet
│   │   ├── AchievementViewSet
│   │   └── DashboardView
│   ├── urls.py                 # API routing
│   ├── admin.py                # Django admin configuration
│   ├── apps.py                 # App configuration
│   ├── migrations/             # Database migrations
│   │   ├── 0001_initial.py
│   │   └── ...
│   └── tests.py                # Unit tests
│
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
└── .gitignore                   # Git ignore rules
```

---

## 📚 Database Models

### User Model

```python
class User(AbstractUser):
    email = EmailField(unique=True)  # Login field
    phone_number = CharField(unique=True)
    preferred_language = CharField(choices=[('EN', 'English'), ('BN', 'Bangla')])

    USERNAME_FIELD = 'email'  # Use email for auth
    REQUIRED_FIELDS = ['username']
```

**Fields**: id, email, phone_number, first_name, last_name, password, preferred_language, created_at, updated_at

### CropBatch Model

```python
class CropBatch:
    user = ForeignKey(User)
    crop_type = CharField(choices=[('PADDY', 'Paddy')])
    estimated_weight = FloatField()  # in kg
    harvest_date = DateField()
    storage_location = CharField(choices=[
        ('DHAKA', 'Dhaka'),
        ('CHITTAGONG', 'Chittagong'),
        ('SYLHET', 'Sylhet'),
        ('RAJSHAHI', 'Rajshahi'),
        ('KHULNA', 'Khulna'),
        ('BARISHAL', 'Barishal'),
        ('RANGPUR', 'Rangpur'),
        ('MYMENSINGH', 'Mymensingh'),
    ])
    storage_type = CharField(choices=[
        ('JUTE_BAG', 'Jute Bag'),
        ('SILO', 'Silo'),
        ('OPEN_AREA', 'Open Area'),
    ])
    status = CharField(choices=[('ACTIVE', 'Active'), ('COMPLETED', 'Completed')])
    notes = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### LossEvent Model

```python
class LossEvent:
    crop_batch = ForeignKey(CropBatch)
    loss_type = CharField(choices=[
        ('PEST', 'Pest Damage'),
        ('DISEASE', 'Disease'),
        ('WEATHER', 'Weather'),
        ('STORAGE', 'Storage Issues'),
    ])
    estimated_loss_percentage = FloatField()  # 0-100
    description = TextField()
    reported_date = DateTimeField(auto_now_add=True)
```

### Intervention Model

```python
class Intervention:
    loss_event = ForeignKey(LossEvent)
    intervention_type = CharField(choices=[
        ('PESTICIDE', 'Pesticide'),
        ('FUNGICIDE', 'Fungicide'),
        ('IRRIGATION', 'Irrigation'),
        ('VENTILATION', 'Ventilation'),
    ])
    effectiveness_percentage = FloatField()  # 0-100, effectiveness rating
    applied_date = DateTimeField(auto_now_add=True)
```

### Achievement Model

```python
class Achievement:
    user = ForeignKey(User)
    badge_name = CharField(choices=[
        ('FIRST_HARVEST', 'First Harvest'),
        ('RISK_MITIGATOR', 'Risk Mitigator'),
        ('SCANNER_MASTER', 'Scanner Master'),
        ('WEATHER_ANALYST', 'Weather Analyst'),
        ('DATA_KEEPER', 'Data Keeper'),
    ])
    earned_at = DateTimeField(auto_now_add=True)
```

---

## 🔌 API Endpoints

### Authentication (`/api/auth/`)

```
POST /api/auth/register
- Request: { email, password, phone_number, first_name, last_name, preferred_language }
- Response: { access, refresh, user }

POST /api/auth/login
- Request: { email, password }
- Response: { access, refresh }

POST /api/auth/refresh
- Request: { refresh }
- Response: { access }

GET /api/auth/me
- Headers: Authorization: Bearer {token}
- Response: { user profile data }

PATCH /api/auth/me
- Update current user profile
```

### Crop Management (`/api/crops/`)

```
GET /api/crops/
- List all crop batches (paginated)
- Filters: status, storage_location, crop_type
- Query params: ?page=1&limit=10

POST /api/crops/
- Create new crop batch
- Request: { crop_type, estimated_weight, harvest_date, storage_location, storage_type, notes }

GET /api/crops/{id}/
- Get crop batch details

PATCH /api/crops/{id}/
- Update crop batch

DELETE /api/crops/{id}/
- Delete crop batch

GET /api/crops/active/
- List only active batches

GET /api/crops/completed/
- List only completed batches
```

### Loss Events (`/api/loss-events/`)

```
GET /api/loss-events/
- List all loss events for user's batches

POST /api/loss-events/
- Report new loss event
- Request: { crop_batch, loss_type, estimated_loss_percentage, description }

GET /api/loss-events/{id}/
- Get loss event details

PATCH /api/loss-events/{id}/
- Update loss event

DELETE /api/loss-events/{id}/
- Delete loss event
```

### Interventions (`/api/interventions/`)

```
GET /api/interventions/
- List all interventions

POST /api/interventions/
- Create intervention
- Request: { loss_event, intervention_type, effectiveness_percentage }

PATCH /api/interventions/{id}/
- Update intervention

DELETE /api/interventions/{id}/
- Delete intervention
```

### Achievements (`/api/achievements/`)

```
GET /api/achievements/
- List user's achievements

POST /api/achievements/{badge_name}/
- Manually unlock achievement (if eligible)
```

### Dashboard (`/api/dashboard/`)

```
GET /api/dashboard/
- Response:
  {
    total_batches: int,
    active_batches: int,
    completed_batches: int,
    total_loss_events: int,
    total_interventions: int,
    intervention_success_rate: float,
    average_loss_percentage: float
  }
```

---

## 🔐 Authentication

### JWT Tokens

- **Access Token**: Short-lived (24 hours), included in Authorization header
- **Refresh Token**: Long-lived (7 days), used to get new access token

### Header Format

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Token Refresh

```
POST /api/auth/refresh
{
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
→ Returns new access token
```

---

## 🛢️ Database

### Development

- **Default**: SQLite (`db.sqlite3`)
- **Automatic**: Database file created on migration

### Production

- **Type**: PostgreSQL
- **Setup**: Via `DATABASE_URL` environment variable
- **Format**: `postgresql://user:password@host:port/dbname`

### Migrations

```bash
# Create migration for model changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# See migration status
python manage.py showmigrations

# Rollback migrations
python manage.py migrate app_name 0001
```

---

## ⚙️ Configuration

### Environment Variables (`.env` or Replit Secrets)

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False  # Set to True only in development

# Database (optional, uses SQLite if not set)
DATABASE_URL=postgresql://user:password@localhost:5432/harvestguard

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CSRF_TRUSTED_ORIGINS=http://localhost:5000,https://yourdomain.com

# CORS
CORS_ALLOW_ALL_ORIGINS=False  # Set True only in development
CORS_ALLOWED_ORIGINS=http://localhost:5000,https://frontend.yourdomain.com

# Cloudinary (media storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Django Settings Key Areas

#### REST Framework Config

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

#### JWT Config

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

#### CORS Config

```python
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ['http://localhost:5000', ...]
```

---

## 📦 Dependencies

### Core

- **Django 5.2.5** - Web framework
- **djangorestframework 3.16.1** - REST API toolkit
- **djangorestframework-simplejwt** - JWT authentication
- **djoser** - User authentication endpoints
- **drf-yasg** - Swagger/OpenAPI documentation

### Database

- **psycopg2** - PostgreSQL driver
- **dj-database-url** - Parse DATABASE_URL

### Media & Storage

- **cloudinary** - Cloud image storage
- **django-cloudinary-storage** - Cloudinary backend

### Utilities

- **whitenoise** - Static file serving
- **python-decouple** - Environment variables
- **django-cors-headers** - CORS support

### Production

- **gunicorn** - WSGI HTTP server

---

## 🚀 Running the Server

### Development

```bash
python manage.py runserver 0.0.0.0:8000
```

### Production (Gunicorn)

```bash
gunicorn config.wsgi:application \
  --bind 0.0.0.0:5000 \
  --workers 2 \
  --worker-class sync \
  --timeout 30
```

### With Environment Variables

```bash
python manage.py runserver \
  --settings=config.settings \
  0.0.0.0:8000
```

---

## 🧪 Testing

### Run All Tests

```bash
python manage.py test
```

### Run Specific App Tests

```bash
python manage.py test core
```

### Run Specific Test Class

```bash
python manage.py test core.tests.UserTests
```

### Test with Coverage

```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

---

## 📝 Admin Interface

Access at: http://localhost:8000/admin/

### Login

```
Username: superuser (created via createsuperuser)
Password: password you set
```

### Manage

- Users
- Crop Batches
- Loss Events
- Interventions
- Achievements

### Bulk Actions

- Delete multiple items
- Export data

---

## 🔄 Data Relationships

```
User (1)
  ├── CropBatch (many)
  │   └── LossEvent (many)
  │       └── Intervention (many)
  └── Achievement (many)
```

**Key Relationships**:

- Each user can have multiple crop batches
- Each batch can have multiple loss events
- Each loss event can have multiple interventions
- Each user can earn multiple achievements

---

## ✅ Validation Rules

### User Registration

- Email: Valid email format, unique
- Password: Min 8 characters
- Phone: Valid Bangladesh format (+880 or 01...)
- First/Last Name: Not empty

### Crop Batch

- Crop Type: Must be from predefined choices
- Weight: Positive number
- Harvest Date: Not in future
- Storage Location: Must be valid region
- Storage Type: Must be valid type

### Loss Event

- Loss Type: Must be valid category
- Loss Percentage: 0-100
- Description: Not empty

### Intervention

- Type: Must be valid intervention type
- Effectiveness: 0-100

---

## 🐛 Common Issues & Solutions

### Migration Issues

```bash
# Reset database (development only)
python manage.py migrate zero core
python manage.py migrate

# View migration history
python manage.py showmigrations
```

### Port Already in Use

```bash
# Use different port
python manage.py runserver 0.0.0.0:9000

# Or kill process on port 8000
kill -9 $(lsof -t -i:8000)
```

### Static Files Not Found

```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear static files
python manage.py collectstatic --clear --noinput
```

### Database Connection Error

- Check `DATABASE_URL` format
- Verify PostgreSQL is running
- Confirm credentials are correct

### CORS Errors

- Add frontend origin to `CORS_ALLOWED_ORIGINS`
- Restart Django server
- Clear browser cache

---

## 🚢 Deployment

### Replit

1. Set environment variables in Replit Secrets
2. Configure `deploy_config_tool` with:
   ```
   deployment_target: autoscale
   run: ['gunicorn', 'config.wsgi:application', '--bind=0.0.0.0:5000', '--workers=2']
   ```
3. Click Publish

### Heroku

```bash
# Create Procfile
echo "web: gunicorn config.wsgi" > Procfile

# Deploy
git push heroku main
heroku run python manage.py migrate
```

### PythonAnywhere

1. Upload code
2. Create virtual environment
3. Configure web app
4. Set environment variables
5. Reload web app

---

## 📊 API Response Format

### Success Response (200, 201)

```json
{
  "id": 1,
  "crop_type": "PADDY",
  "estimated_weight": 500,
  "status": "ACTIVE",
  "created_at": "2025-11-28T10:30:00Z",
  ...
}
```

### List Response (with pagination)

```json
{
  "count": 25,
  "next": "http://api.example.com/crops/?page=2",
  "previous": null,
  "results": [
    { "id": 1, ... },
    { "id": 2, ... }
  ]
}
```

### Error Response (4xx, 5xx)

```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "not_authenticated"
}
```

---

## 🔗 Useful Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://github.com/jpadilla/django-rest-framework-simplejwt)
- [drf-yasg (Swagger)](https://drf-yasg.readthedocs.io/)

---

## 📞 Support

- **API Documentation**: Visit `/api/swagger/` or `/api/redoc/`
- **Django Admin**: Access `/admin/` for data management
- **Error Details**: Check Django console output and response messages

---

**Built with ❤️ to help farmers protect their harvests.**
