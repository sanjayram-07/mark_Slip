# Quick Start Guide - Local Development

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (for version control)

---

## 🚀 Installation & Setup

### 1. Clone or Download the Project

```bash
# Clone from GitHub (if on Git)
git clone https://github.com/yourusername/mark-slip-generator.git
cd mark-slip-generator

# OR download and extract ZIP file
cd mark-slip-generator
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your settings (optional for local dev)
# For production, change SECRET_KEY and FLASK_ENV
```

### 5. Run the Application

```bash
python app.py
```

You should see:

```
============================================================
Student Mark Slip Generator - Backend
============================================================
Starting Flask server...
Open http://localhost:5000 in your browser
============================================================
```

### 6. Open in Browser

Navigate to: **http://localhost:5000**

---

## 📝 Usage

### Upload PDF

1. Click "Choose PDF file" or drag a PDF onto the upload area
2. The PDF should contain student mark information in table format

### Customize (Optional)

- **College Name**: Default is "Madras Institute of Technology"
- **Department Name**: Default is "Department of Computer Technology"

### Generate Slip

1. Click "Process & Download"
2. Wait for processing to complete
3. PDF with formatted mark slips will download automatically

---

## 📊 Supported PDF Formats

### Format 1: Individual Pages

- One student per page
- Clearly labeled: "Register Number: XXXX"
- Table with: Course Code, Course Name, Grade, Result

### Format 2: Summary Sheet (Recommended)

- All students in columns
- All subjects in rows
- Student roll numbers in header row

### Example Structure:

```
┌──────────────┬──────────┬──────────┬──────────┐
│ S.No | Code │  2020001 │  2020002 │  2020003 │
├──────────────┼──────────┼──────────┼──────────┤
│   1  │ CS101│    A     │    B     │    A     │
│   2  │ CS102│    B+    │    A     │    B+    │
│   3  │ CS103│    A     │    A     │    A     │
└──────────────┴──────────┴──────────┴──────────┘
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"

**Solution:**

```bash
# Make sure virtual environment is activated
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port already in use"

**Solution:**

```bash
# Use different port
export PORT=8080
python app.py

# Or kill the process using port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

### Issue: "No student data found"

**Solution:**

- Ensure PDF contains tables with data
- Check that text is extractable (not scanned image)
- Verify the format follows expected structure

### Issue: "Connection refused"

**Solution:**

```bash
# Make sure Flask app is running
python app.py

# Check if running on different port
# App logs will show: Running on http://127.0.0.1:XXXX
```

---

## 📁 Project Structure

```
mark-slip-generator/
├── app.py                 # Flask application (main entry point)
├── a1.py                  # PDF processing logic
├── requirements.txt       # Python dependencies
├── Procfile              # For Heroku deployment
├── Dockerfile            # For Docker deployment
├── docker-compose.yml    # Docker compose configuration
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore patterns
├── templates/
│   └── index.html        # Web interface
├── DEPLOYMENT.md         # Deployment guide
├── QUICKSTART.md         # This file
└── README.md             # Main documentation
```

---

## 🔧 Configuration Files Explained

### `app.py`

- Main Flask application
- Handles file uploads and PDF processing
- Routes for API endpoints

### `a1.py`

- PDF extraction and processing
- Mark slip generation
- Multi-format PDF support

### `requirements.txt`

- Python package dependencies
- Version pinned for consistency

### `.env`

- Environment-specific configuration
- API keys and secrets
- Database URLs (if applicable)

### `Procfile`

- Process file for Heroku deployment
- Specifies command to run application

### `Dockerfile`

- Container configuration for Docker
- Defines application environment

---

## 🚀 Next Steps

### Development

1. Modify files in the project directory
2. Changes take effect immediately (auto-reload enabled)
3. Check terminal for debug output

### Testing

```bash
# Test API health check
curl http://localhost:5000/api/health

# Test with sample PDF
# Use the web interface at http://localhost:5000
```

### Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step deployment guides for:

- Heroku (easiest)
- PythonAnywhere
- AWS Elastic Beanstalk
- Digital Ocean
- Docker + VPS
- Google Cloud Run

---

## 📞 Support & Help

- Check the [README.md](README.md) for general information
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
- Review logs in terminal/console for error messages

---

## 📝 Common Tasks

### Change Default College Name

Edit the form in `templates/index.html` or pass via API:

```bash
curl -X POST http://localhost:5000/api/process \
  -F "file=@marks.pdf" \
  -F "college=Your College Name" \
  -F "dept=Your Department Name"
```

### Access Logs

Logs are printed to console/terminal. For persistent logging, edit `app.py` to set log file path.

### Change Port

```bash
# Set environment variable before running
export PORT=8000
python app.py
```

---

## 🔐 Production Considerations

Before deploying to production:

1. Set `DEBUG=False` in `.env`
2. Generate secure `SECRET_KEY`
3. Enable HTTPS/SSL
4. Set up proper logging
5. Configure backups
6. Set up monitoring/alerting

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed security guidelines.

---

**Version:** 1.0.0  
**Last Updated:** April 2026
