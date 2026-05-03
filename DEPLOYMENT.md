# Digital Legacy App — Deployment Guide

## ✅ What Has Been Done

1. **Production Docker Compose File** (`docker-compose.prod.yml`) created with:
   - PostgreSQL database (production-ready)
   - Redis cache/broker
   - Django API with Gunicorn WSGI server
   - Celery worker for background tasks
   - Celery Beat scheduler for DMS checks
   - Nginx server serving the compiled React/Vite Frontend

2. **Production Entrypoint Script** (`entrypoint.sh`) created to:
   - Wait for PostgreSQL to be ready
   - Run migrations automatically
   - Collect static files
   - Start Gunicorn server

3. **Updated Requirements** (`requirements.txt`):
   - Added `gunicorn>=21.0` for production WSGI server
   - Added `psycopg2-binary>=2.9` for PostgreSQL support
   - Added `django-cors-headers>=4.0` for CORS
   - Added `django-filter>=23.0` for filtering support
   - All dependencies now installed and tested

4. **Updated Dockerfile** for production:
   - Multi-stage build optimized for production
   - Non-root user (django) for security
   - Entrypoint script included
   - Minimal base image (Python 3.12-slim)

5. **Environment Configuration**:
   - `.env` file updated with production settings
   - `DEBUG=False` (security-critical)
   - `ALLOWED_HOSTS` configured for your domain
   - Database and Redis environment variables

6. **Local Testing Completed**:
   - ✅ Virtual environment created
   - ✅ All dependencies installed
   - ✅ Database migrations applied
   - ✅ Server starts successfully

---

## 🚀 Quick Deployment Steps (Choose One)

### **Option 1: Local Development (Recommended First)**

```bash
# Activate venv
venv\Scripts\activate

# Run the development server
python manage.py runserver

# Visit: http://localhost:8000/health/
```

### **Option 2: Docker Deployment (Production)**

Requires Docker Desktop to be installed.

```bash
# Build and start all services
docker compose -f docker-compose.prod.yml up --build -d

# Check services are healthy
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs api

# Stop services
docker compose -f docker-compose.prod.yml down
```

---

## 🔧 Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] **Environment Variables** (`.env`):
  - [ ] `DEBUG=False`
  - [ ] `SECRET_KEY` is a strong random string
  - [ ] `ALLOWED_HOSTS` includes your domain
  - [ ] `DATABASE_URL` points to production PostgreSQL
  - [ ] `REDIS_URL` is correct
  - [ ] AWS credentials configured (if using S3)
  - [ ] Email service configured (SendGrid or Gmail)

- [ ] **Security**:
  - [ ] Run `bandit -r apps/ core/` to check for security issues
  - [ ] Run `safety check -r requirements.txt` to verify no CVEs
  - [ ] SSL/TLS certificate configured (use nginx reverse proxy)
  - [ ] `.env` file NOT committed to git

- [ ] **Database**:
  - [ ] PostgreSQL is running and accessible
  - [ ] Migrations have been applied
  - [ ] Backup strategy in place

---

## 📋 API Health Check

After deployment, verify the API is running:

```bash
curl http://localhost:8000/health/
```

Expected response:
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "service": "digital-legacy-api",
    "version": "v1"
  }
}
```

---

## 🐳 Docker Production Services

### PostgreSQL
- **Container**: `dl_postgres_prod`
- **Port**: 5432
- **Data**: Persistent volume `postgres_data`

### Redis
- **Container**: `dl_redis_prod`
- **Port**: 6379
- **Data**: Persistent volume `redis_data`

### Django API
- **Container**: `dl_api_prod`
- **Port**: 8000
- **WSGI Server**: Gunicorn (4 workers)
- **Process**: Runs migrations on startup

### Celery Worker
- **Container**: `dl_celery_prod`
- **Purpose**: Background task processing (notifications, DMS checks)

### Celery Beat
- **Container**: `dl_celery_beat_prod`
- **Purpose**: Scheduled tasks (DMS heartbeat checks)

### React Frontend (Nginx)
- **Container**: `dl_frontend_prod`
- **Port**: 80 / 443
- **Purpose**: Serves the static compiled Vite bundle. Should be configured to proxy `/api/` requests directly to `dl_api_prod` on port 8000 to avoid CORS issues.

---

## 🔐 Security Best Practices

1. **Never commit `.env`** — it contains secrets
2. **Use strong SECRET_KEY** — minimum 50 random characters
3. **Set `DEBUG=False`** — prevents info leakage in errors
4. **Use HTTPS** — configure nginx as reverse proxy
5. **Restrict `ALLOWED_HOSTS`** — only your domain(s)
6. **Database backups** — daily automated backups
7. **Monitor logs** — aggregate logs from all containers
8. **Update dependencies** — run `safety check` regularly

---

## 📊 Performance Tuning

### Gunicorn Workers
Current config: `--workers 4`

Recommended formula: `(2 × CPU cores) + 1`
- For 2-core server: 5 workers
- For 4-core server: 9 workers

Edit in `docker-compose.prod.yml` API service command.

### Database Connections
- Max connections: `DATABASE_POOL_SIZE=20` (in `.env`)
- Recommended: Set based on worker count

### Redis
- Current pool: Default (auto-managed)
- Monitor memory usage in production

---

## 🛠️ Troubleshooting

### **"No migrations to apply"**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **Docker containers not starting**
```bash
docker compose -f docker-compose.prod.yml logs
# Check specific service
docker compose -f docker-compose.prod.yml logs api
```

### **Database connection refused**
- Check PostgreSQL is running: `docker compose -f docker-compose.prod.yml ps`
- Verify DATABASE_URL in `.env`
- Check database credentials

### **Celery tasks not running**
```bash
# Check Celery worker logs
docker compose -f docker-compose.prod.yml logs celery

# Restart worker
docker compose -f docker-compose.prod.yml restart celery
```

---

## 📚 Additional Resources

- [Django Production Deployment](https://docs.djangoproject.com/en/6.0/howto/deployment/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 🎯 Next Steps

1. **Immediate**: Test locally with `python manage.py runserver`
2. **Short-term**: Set up production `.env` with real credentials
3. **Medium-term**: Deploy to cloud provider (AWS, Heroku, DigitalOcean)
4. **Long-term**: Set up CI/CD pipeline and monitoring

---

**Last Updated**: May 1, 2026
**Status**: ✅ Ready for Deployment
