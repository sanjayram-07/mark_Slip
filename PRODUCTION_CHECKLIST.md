# Production Deployment Checklist

Use this checklist to ensure your deployment is secure and production-ready.

---

## 🔒 Security

- [ ] **SECRET_KEY Configuration**

  ```bash
  # Generate strong secret key
  python -c 'import secrets; print(secrets.token_hex(32))'
  # Store in .env file, never commit to Git
  ```

- [ ] **DEBUG Mode Disabled**

  ```bash
  FLASK_ENV=production
  DEBUG=False
  ```

- [ ] **HTTPS/SSL Enabled**
  - [ ] Heroku: Automatic
  - [ ] PythonAnywhere: Automatic
  - [ ] Self-hosted: Use Let's Encrypt/nginx

- [ ] **CORS Configuration**
      Edit `app.py` if needed:

  ```python
  CORS(app, origins=[
      "https://yourdomain.com",
      "https://www.yourdomain.com"
  ])
  ```

- [ ] **File Upload Validation**
  - [ ] Only PDF files allowed
  - [ ] File size limit: 50MB
  - [ ] Filename sanitization enabled

- [ ] **Environment Variables Secured**
  - [ ] No secrets in code
  - [ ] All sensitive data in `.env`
  - [ ] `.env` in `.gitignore`

- [ ] **Rate Limiting Enabled**
      Consider adding `flask-limiter` for API protection

- [ ] **Error Logging Configured**
  - [ ] Sentry, DataDog, or similar
  - [ ] No sensitive data in logs

---

## 🏗️ Infrastructure

- [ ] **Database Setup** (if applicable)
  - [ ] Backups configured
  - [ ] Connection pooling enabled
  - [ ] Migrations applied

- [ ] **Storage Setup**
  - [ ] Temporary file cleanup scheduled
  - [ ] Upload directory permissions set (775)
  - [ ] Disk space monitoring

- [ ] **Memory/CPU**
  - [ ] Process monitoring enabled
  - [ ] Auto-restart on crash configured
  - [ ] Resource limits set

- [ ] **Backup Strategy**
  - [ ] Daily backups scheduled
  - [ ] Backup tested for restoration
  - [ ] Off-site storage configured

- [ ] **Monitoring**
  - [ ] Server uptime monitoring (UptimeRobot, etc.)
  - [ ] Error tracking (Sentry)
  - [ ] Performance monitoring (New Relic, DataDog)
  - [ ] Alert thresholds set

---

## 🚀 Deployment Preparation

- [ ] **Code Review**
  - [ ] All changes reviewed
  - [ ] No debug code left
  - [ ] No hardcoded credentials

- [ ] **Testing**
  - [ ] Local tests pass
  - [ ] Test with production PDF samples
  - [ ] Test on staging environment
  - [ ] Load testing completed

- [ ] **Dependencies**
  - [ ] `requirements.txt` updated
  - [ ] `Procfile` correct
  - [ ] `runtime.txt` specifies Python 3.10

- [ ] **Database Migrations** (if applicable)
  - [ ] Migrations created
  - [ ] Rollback plan documented
  - [ ] Tested on staging

- [ ] **Static Files**
  - [ ] CSS/JS minified
  - [ ] Images optimized
  - [ ] CDN configured (if applicable)

---

## 📋 Pre-Deployment

Choose your platform and follow its checklist:

### Heroku Pre-Deployment

- [ ] Heroku account created
- [ ] Heroku CLI installed
- [ ] App created on Heroku
- [ ] Git remote added
- [ ] Config vars set:
  ```bash
  heroku config:set FLASK_ENV=production
  heroku config:set SECRET_KEY=<your-secret>
  heroku config:set DEBUG=False
  ```

### PythonAnywhere Pre-Deployment

- [ ] PythonAnywhere account created
- [ ] Files uploaded
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] WSGI configuration updated
- [ ] Environment variables set

### AWS Pre-Deployment

- [ ] AWS account created with billing alert
- [ ] IAM user created for deployment
- [ ] EB CLI installed and configured
- [ ] `.ebextensions/` directory created
- [ ] Security groups configured

### Docker Pre-Deployment

- [ ] Docker installed
- [ ] Dockerfile tested locally
- [ ] Docker image builds successfully
- [ ] Container runs and serves requests
- [ ] docker-compose.yml configured

---

## 🔄 Deployment Day

1. **Backup Current (if upgrading)**

   ```bash
   # Take backup of current state
   heroku pg:backups:capture
   # or similar for your platform
   ```

2. **Deploy Code**
   - [ ] Push to main/master branch
   - [ ] CI/CD pipeline passes
   - [ ] Deployment completes without errors

3. **Post-Deployment Tests**
   - [ ] Health endpoint responds: `GET /api/health`
   - [ ] Home page loads: `GET /`
   - [ ] API accepts requests: `POST /api/process`
   - [ ] File upload works with test PDF
   - [ ] PDF generation completes successfully

4. **Monitor**
   - [ ] Check error logs
   - [ ] Monitor resource usage
   - [ ] Watch for exceptions

---

## 📊 Performance Checklist

- [ ] **Response Times**
  - [ ] Homepage loads < 2s
  - [ ] API health check < 100ms
  - [ ] PDF processing < 30s for typical file

- [ ] **Database Performance** (if applicable)
  - [ ] Query times monitored
  - [ ] Indexes created
  - [ ] Slow query log reviewed

- [ ] **Caching**
  - [ ] Static files cached (30+ days)
  - [ ] API responses cached where appropriate

- [ ] **Compression**
  - [ ] GZIP enabled on static content
  - [ ] JavaScript/CSS minified

---

## 🔐 Security Hardening

Additional security measures:

- [ ] **OWASP Top 10 Review**
  - [ ] SQL Injection: Not applicable (no DB used)
  - [ ] Broken Authentication: Uses Flask sessions
  - [ ] Sensitive Data Exposure: HTTPS enabled
  - [ ] XML External Entities: Not used
  - [ ] Broken Access Control: Input validation enabled
  - [ ] Security Misconfiguration: Debug off, headers set
  - [ ] Cross-Site Scripting (XSS): Template escaping enabled
  - [ ] Insecure Deserialization: Not used
  - [ ] Using Components with Known Vulnerabilities: Dependencies updated
  - [ ] Insufficient Logging & Monitoring: Implemented

- [ ] **HTTP Security Headers**
      Add to `app.py`:

  ```python
  @app.after_request
  def set_security_headers(response):
      response.headers['X-Content-Type-Options'] = 'nosniff'
      response.headers['X-Frame-Options'] = 'SAMEORIGIN'
      response.headers['X-XSS-Protection'] = '1; mode=block'
      response.headers['Strict-Transport-Security'] = 'max-age=31536000'
      return response
  ```

- [ ] **Input Validation**
  - [ ] All user inputs validated
  - [ ] File uploads checked
  - [ ] Filename sanitized

- [ ] **Regular Updates**
  - [ ] Dependencies updated monthly
  - [ ] Security patches applied immediately
  - [ ] OS/framework security updates applied

---

## 📞 Escalation & Support

- [ ] **Support Channel Setup**
  - [ ] Email configured
  - [ ] Error alerts configured
  - [ ] On-call rotation established

- [ ] **Documentation**
  - [ ] Runbook created
  - [ ] Troubleshooting guide prepared
  - [ ] Architecture diagram documented

- [ ] **Rollback Plan**
  - [ ] Previous version tagged
  - [ ] Rollback procedure tested
  - [ ] Rollback time < 5 minutes

---

## ✅ Final Approval

- [ ] **Project Manager**
  - [ ] Approves release
  - [ ] Stakeholders notified

- [ ] **Tech Lead**
  - [ ] Code review complete
  - [ ] Architecture approved
  - [ ] Performance acceptable

- [ ] **DevOps**
  - [ ] Infrastructure ready
  - [ ] Monitoring configured
  - [ ] Backup verified

- [ ] **Security**
  - [ ] Security review passed
  - [ ] No critical vulnerabilities
  - [ ] GDPR/compliance requirements met (if applicable)

---

## 📝 Post-Deployment

### Day 1

- [ ] Monitor error logs continuously
- [ ] Check performance metrics
- [ ] Verify all features working
- [ ] Gather user feedback

### Week 1

- [ ] Review error patterns
- [ ] Optimize slow functions
- [ ] Plan follow-up improvements
- [ ] Document any issues

### Month 1

- [ ] Analyze usage patterns
- [ ] Plan capacity upgrades if needed
- [ ] Update documentation
- [ ] Schedule security audit

---

## 🚨 Emergency Procedures

### If Issues Arise

1. **Check Logs**

   ```bash
   # Heroku
   heroku logs --tail

   # Docker
   docker logs <container-id>
   ```

2. **Quick Rollback**

   ```bash
   # Heroku
   heroku releases
   heroku rollback v<number>

   # Docker
   docker pull <previous-image-version>
   docker-compose up -d
   ```

3. **Notify Team**
   - Send incident alert
   - Document in incident log
   - Start investigation

---

## 📞 Deployment Support

- **Heroku Support:** https://help.heroku.com
- **PythonAnywhere Help:** https://www.pythonanywhere.com/user_files/help.html
- **AWS Support:** https://console.aws.amazon.com/support
- **Docker Docs:** https://docs.docker.com

---

**Checklist Version:** 1.0  
**Last Updated:** April 2026  
**Environment:** Production

---

Use this checklist for every production deployment. Customize for your specific needs.
