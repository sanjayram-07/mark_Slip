# Student Mark Slip Generator - Deployment Guide

## Overview

This guide covers deployment options for the Student Mark Slip Generator application on various platforms.

---

## 🚀 Deployment Options

### 1. **Heroku** (Recommended for beginners)

**Cost:** Free tier available (limited), paid plans start at $7/month  
**Pros:** Easy deployment, automatic HTTPS, built-in CI/CD  
**Cons:** Requires credit card for free tier

#### Steps:

1. **Install Heroku CLI**

   ```bash
   # Windows
   Download from https://devcenter.heroku.com/articles/heroku-cli

   # macOS
   brew tap heroku/brew && brew install heroku

   # Linux
   curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
   ```

2. **Login to Heroku**

   ```bash
   heroku login
   ```

3. **Create Heroku App**

   ```bash
   heroku create your-app-name
   ```

4. **Set Environment Variables**

   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   heroku config:set DEBUG=False
   ```

5. **Deploy Code**

   ```bash
   git push heroku main
   ```

6. **View Logs**
   ```bash
   heroku logs --tail
   ```

**Files needed:** `Procfile`, `runtime.txt`, `requirements.txt`

---

### 2. **PythonAnywhere** (Easiest for beginners)

**Cost:** Free tier available, paid plans start at $5/month  
**Pros:** Python-focused, no Docker needed, simple setup  
**Cons:** Limited resources on free tier

#### Steps:

1. **Create Account** at https://www.pythonanywhere.com

2. **Upload Files**
   - Go to Files tab
   - Upload your project files

3. **Create Web App**
   - Web tab → Add a new web app
   - Choose Flask
   - Python 3.10
   - Virtual environment path: `/home/username/project_venv`

4. **Edit WSGI Configuration**
   - Edit WSGI configuration file
   - Add this code:

   ```python
   import sys
   path = '/home/username/mark-slip-generator'
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import app as application
   ```

5. **Install Dependencies**

   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 project_venv
   pip install -r requirements.txt
   ```

6. **Reload Web App**
   - Go to Web tab and click "Reload"

**URL:** `https://username.pythonanywhere.com`

---

### 3. **AWS Elastic Beanstalk**

**Cost:** Pay as you go (starts free for first year with t2.micro)  
**Pros:** Scalable, reliable, auto-scaling support  
**Cons:** More complex configuration, steeper learning curve

#### Steps:

1. **Install AWS CLI & EB CLI**

   ```bash
   pip install awsebcli
   aws configure
   ```

2. **Initialize EB Application**

   ```bash
   eb init -p python-3.10 mark-slip-generator --region us-east-1
   ```

3. **Create `.ebextensions/python.config`**

   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: app:app
     aws:elasticbeanstalk:application:environment:
       FLASK_ENV: production
       SECRET_KEY: your-secret-key-here
   ```

4. **Deploy**
   ```bash
   eb create mark-slip-env
   eb deploy
   eb open
   ```

---

### 4. **Digital Ocean App Platform**

**Cost:** $5-90/month depending on resources  
**Pros:** Good performance, developer-friendly, transparent pricing  
**Cons:** Slightly higher cost than alternatives

#### Steps:

1. **Push to GitHub** (required for DO App Platform)

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/username/mark-slip-generator.git
   git push -u origin main
   ```

2. **Create App on Digital Ocean**
   - Go to https://cloud.digitalocean.com/apps
   - Click "Create App"
   - Select GitHub repository
   - Choose "Python" runtime
   - Set environment variables

3. **Deploy**
   - Digital Ocean automatically deploys on push to main

---

### 5. **Docker + Self-Hosted (VPS)**

**Cost:** $3-20/month for VPS  
**Pros:** Maximum control, no vendor lock-in  
**Cons:** Requires server management knowledge

#### Steps:

1. **Create `Dockerfile`**

   ```dockerfile
   FROM python:3.10-slim

   WORKDIR /app

   # Install dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       && rm -rf /var/lib/apt/lists/*

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   ENV FLASK_ENV=production
   ENV PORT=5000

   EXPOSE 5000

   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
   ```

2. **Create `docker-compose.yml`**

   ```yaml
   version: "3.8"

   services:
     web:
       build: .
       ports:
         - "5000:5000"
       environment:
         - FLASK_ENV=production
         - SECRET_KEY=${SECRET_KEY}
       volumes:
         - ./uploads:/app/uploads
   ```

3. **Deploy on VPS**

   ```bash
   # SSH into VPS
   ssh root@your.server.ip

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh

   # Clone repository
   git clone your-repo
   cd your-repo

   # Build and run
   docker-compose up -d
   ```

---

### 6. **Google Cloud Run** (Serverless)

**Cost:** ~$0.20 per million requests  
**Pros:** Auto-scaling, only pay for usage, serverless  
**Cons:** Cold starts, may be expensive for high traffic

#### Steps:

1. **Create `Dockerfile`** (same as Docker option above)

2. **Deploy to Cloud Run**

   ```bash
   # Authenticate
   gcloud auth login

   # Build and push
   gcloud builds submit --tag gcr.io/PROJECT-ID/mark-slip-generator

   # Deploy
   gcloud run deploy mark-slip-generator \
     --image gcr.io/PROJECT-ID/mark-slip-generator \
     --platform managed \
     --region us-central1 \
     --memory 512Mi \
     --set-env-vars FLASK_ENV=production,SECRET_KEY=your-key
   ```

---

## 📋 Pre-Deployment Checklist

- [ ] Set up `.env` file with all required variables
- [ ] Test locally: `python app.py`
- [ ] Run tests if available
- [ ] Set `DEBUG=False` in production
- [ ] Generate strong `SECRET_KEY`: `python -c 'import secrets; print(secrets.token_hex(32))'`
- [ ] Configure CORS for your domain
- [ ] Set up error logging/monitoring
- [ ] Configure backup strategy (if using database)
- [ ] Set up SSL/HTTPS (automatic on most platforms)
- [ ] Test file upload limits
- [ ] Test with sample PDF file

---

## 🔐 Security Best Practices

### 1. **Environment Variables**

Never commit sensitive data. Always use `.env` files:

```bash
# .env (never commit to Git)
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

### 2. **HTTPS/SSL**

- Heroku, PythonAnywhere, Cloud Run provide automatic HTTPS
- For self-hosted, use Let's Encrypt with Nginx

### 3. **Rate Limiting** (Add to app.py)

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/process', methods=['POST'])
@limiter.limit("10 per hour")  # 10 requests per hour
def process_pdf():
    # ... rest of code
```

### 4. **Input Validation**

- Already implemented: filename sanitization
- File type checking for PDFs only
- File size limits

### 5. **Monitoring & Logging**

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

---

## 📊 Recommended Deployment Path

### For Small Projects (< 1000 users/month)

**PythonAnywhere Free Tier**

- No credit card needed
- Easy setup
- Good for testing

### For Growing Projects (1000-50,000 users/month)

**Heroku ($7/month) or Digital Ocean ($5/month)**

- Reliable performance
- Good balance of cost and features
- Easy scaling

### For Enterprise (> 50,000 users/month)

**AWS or Google Cloud**

- Auto-scaling
- Enterprise support
- Pay per usage

---

## 🔄 CI/CD Pipeline Example (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Heroku

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: "your-app-name"
          heroku_email: "your-email@example.com"
```

---

## 🆘 Troubleshooting

### "Module not found"

```bash
# Verify requirements installed
pip install -r requirements.txt

# Check Python version
python --version
```

### "Port already in use"

```bash
# Use environment variable
export PORT=8080
python app.py
```

### "Memory/Timeout issues"

- Optimize PDF processing
- Add request timeout in frontend
- Use background job queue (Celery)

### "File upload not working"

```python
# Check upload folder permissions
import os
os.chmod(app.config['UPLOAD_FOLDER'], 0o755)
```

---

## 📞 Support Resources

- **Heroku:** https://devcenter.heroku.com
- **PythonAnywhere:** https://www.pythonanywhere.com/user_files/help.html
- **AWS:** https://docs.aws.amazon.com/elasticbeanstalk
- **Digital Ocean:** https://docs.digitalocean.com/products/app-platform
- **Google Cloud Run:** https://cloud.google.com/run/docs
- **Flask Deployment:** https://flask.palletsprojects.com/deployment

---

## 📝 Notes

- Always test in production-like environment before going live
- Set up monitoring and alerting
- Plan for backup and disaster recovery
- Document your deployment process
- Keep dependencies updated
- Regular security audits

---

**Last Updated:** April 2026  
**Tested On:** Python 3.10, Flask 3.0.0
