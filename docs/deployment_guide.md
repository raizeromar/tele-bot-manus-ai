# Telegram AI Agent - Deployment Guide

## Prerequisites

Before deploying the Telegram AI Agent, ensure you have the following:

1. **Server Requirements**
   - A VPS or dedicated server running Linux (Ubuntu 22.04 LTS recommended)
   - Minimum 2 CPU cores, 4GB RAM, and 20GB storage
   - Root or sudo access to the server
   - A domain name pointed to your server (optional but recommended)

2. **Software Requirements**
   - Docker (version 20.10 or higher)
   - Docker Compose (version 2.0 or higher)
   - Git

3. **API Credentials**
   - Telegram API credentials (API ID and API Hash) from https://my.telegram.org/apps
   - Google API key with access to Gemini 2.0 Flash

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/telegram-ai-agent.git
cd telegram-ai-agent
```

### 2. Configure Environment Variables

```bash
cd deployment
cp .env.example .env
```

Edit the `.env` file with your specific configuration:

```
# Generate a secure random string for SECRET_KEY
SECRET_KEY=your_secure_random_string

# Set to False in production
DEBUG=False

# Add your domain name
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database credentials (change these to secure values)
DB_NAME=telegram_ai_agent
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=5432

# CORS settings
CORS_ALLOWED_ORIGINS=https://your-domain.com

# Celery settings
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Telegram API credentials
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash

# Google API key
GOOGLE_API_KEY=your_google_api_key

# Frontend settings
NEXT_PUBLIC_API_URL=https://your-domain.com/api

# Docker Compose settings (must match DB settings above)
POSTGRES_PASSWORD=your_secure_password
POSTGRES_USER=postgres
POSTGRES_DB=telegram_ai_agent
```

### 3. Build and Start the Containers

```bash
docker-compose build
docker-compose up -d
```

This will start all the necessary services:
- PostgreSQL database
- Redis for Celery
- Django backend
- Celery worker
- Celery beat scheduler
- Next.js frontend
- Nginx for routing

### 4. Create a Superuser

```bash
docker-compose exec backend python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### 5. Configure SSL (Recommended)

For production deployments, it's strongly recommended to configure SSL. You can use Let's Encrypt with Certbot:

```bash
# Install Certbot
apt-get update
apt-get install certbot python3-certbot-nginx

# Obtain and configure SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 6. Verify Deployment

1. Visit `https://your-domain.com` (or `http://your-server-ip` if not using a domain)
2. Log in with the superuser credentials you created
3. Navigate to the admin panel at `/admin` to configure initial settings

## Maintenance

### Updating the Application

To update the application to a new version:

```bash
# Pull the latest code
git pull

# Rebuild and restart containers
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup and Restore

#### Database Backup

```bash
docker-compose exec db pg_dump -U postgres telegram_ai_agent > backup_$(date +%Y%m%d).sql
```

#### Database Restore

```bash
cat backup_file.sql | docker-compose exec -T db psql -U postgres telegram_ai_agent
```

### Monitoring Logs

```bash
# View logs for all services
docker-compose logs

# View logs for a specific service
docker-compose logs backend
docker-compose logs celery
docker-compose logs frontend
```

### Scaling

To scale the application for higher load:

1. Increase resources allocated to Docker
2. Scale specific services:
   ```bash
   docker-compose up -d --scale backend=3 --scale celery=2
   ```
3. Consider using a managed database service for production

## Troubleshooting

### Container Issues

If containers fail to start:

```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs --tail=100 service_name
```

### Database Connection Issues

If the backend can't connect to the database:

1. Verify database container is running: `docker-compose ps db`
2. Check database logs: `docker-compose logs db`
3. Ensure environment variables are correctly set in `.env`

### Telegram Authentication Issues

If Telegram authentication fails:

1. Verify API credentials in `.env`
2. Check backend logs for specific error messages
3. Ensure the server has internet access to connect to Telegram servers

## Security Recommendations

1. **Firewall Configuration**
   - Configure a firewall to only allow necessary ports (80, 443)
   - Use `ufw` on Ubuntu:
     ```bash
     ufw allow 80/tcp
     ufw allow 443/tcp
     ufw enable
     ```

2. **Regular Updates**
   - Keep the server OS updated
   - Regularly update Docker and Docker Compose
   - Pull the latest application code

3. **Secure Environment Variables**
   - Restrict access to the `.env` file
   - Use a secrets management solution for production

4. **Regular Backups**
   - Schedule regular database backups
   - Store backups in a secure, off-site location

## Additional Configuration

### Custom Domain Setup

If using a custom domain:

1. Update DNS settings to point to your server IP
2. Update the `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` in `.env`
3. Configure Nginx for your domain
4. Set up SSL certificates as described above

### Email Configuration

To enable email notifications:

1. Add SMTP settings to `.env`:
   ```
   EMAIL_HOST=smtp.example.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email@example.com
   EMAIL_HOST_PASSWORD=your_email_password
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=your_email@example.com
   ```

2. Update Django settings to use these variables

## Support

If you encounter issues not covered in this guide, please:

1. Check the logs for specific error messages
2. Consult the technical documentation
3. Contact support at support@example.com
