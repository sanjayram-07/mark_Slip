# Student Mark Slip Generator - Production Ready

A complete web application to process student mark PDFs and generate formatted mark slips.  
**Production-ready with deployment guides for multiple platforms.**

## 🌟 Features

- 📤 Upload multi-page mark PDFs
- 📄 Automatically extract student information and marks
- 🎨 Generate beautifully formatted A5 mark slips **with logo**
- 📥 Download combined PDF with all slips
- 🎯 **2 slips per A4 page for efficient printing**
- 🌐 Simple, responsive web interface
- 🚀 **Production-ready code**
- ⚙️ **Environment-based configuration**
- 📊 **Comprehensive logging**

## 📋 Technology Stack

| Component          | Technology                                               |
| ------------------ | -------------------------------------------------------- |
| **Backend**        | Flask 3.0.0                                              |
| **Frontend**       | HTML5, CSS3, JavaScript                                  |
| **PDF Processing** | pdfplumber, reportlab, pypdf                             |
| **Server**         | Gunicorn                                                 |
| **Docker**         | Docker, Docker Compose                                   |
| **Deployment**     | Heroku, PythonAnywhere, AWS, Digital Ocean, Google Cloud |

## 📁 Project Structure

```
mark-slip-generator/
├── app.py                      # Flask application (main)
├── a1.py                       # PDF processing logic
├── requirements.txt            # Dependencies
├── Procfile                   # Heroku deployment
├── runtime.txt                # Python version
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose config
├── .env.example               # Environment variables
├── templates/index.html       # Web interface
├── README.md                  # Overview
├── QUICKSTART.md              # Quick start guide
├── DEPLOYMENT.md              # Deployment guides
└── PRODUCTION_CHECKLIST.md    # Checklist
```

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# 1. Clone or download project
cd mark-slip-generator

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run application
python app.py
```

Open your browser to: **http://localhost:5000**

See [QUICKSTART.md](QUICKSTART.md) for detailed setup.

---

## 🌐 Deployment (Choose Your Platform)

| Platform           | Time   | Cost    | Difficulty |
| ------------------ | ------ | ------- | ---------- |
| **Heroku**         | 5 min  | Free/$  | ⭐ Easy    |
| **PythonAnywhere** | 10 min | Free/$  | ⭐ Easy    |
| **AWS**            | 20 min | $$$     | ⭐⭐⭐     |
| **Digital Ocean**  | 15 min | $$      | ⭐⭐       |
| **Docker**         | 15 min | $$      | ⭐⭐⭐     |
| **Google Cloud**   | 10 min | Pay/use | ⭐⭐       |

### Fastest: Heroku (5 minutes)

```bash
# 1. Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli
# 2. Login
heroku login

# 3. Create app
heroku create your-app-name

# 4. Deploy
git push heroku main
```

Live at: `https://your-app-name.herokuapp.com`

### Easiest: PythonAnywhere (10 minutes)

1. Create account at https://pythonanywhere.com (no credit card needed!)
2. Upload files
3. Create Web App → Flask → Python 3.10
4. Done!

### With Docker

```bash
docker-compose up -d
# Live at http://localhost:5000
```

**→ See [DEPLOYMENT.md](DEPLOYMENT.md) for all platforms with detailed steps**

---

## 🔐 Production Setup

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

### 4. Open in Browser

- Open your web browser and go to: **http://localhost:5000**

## How to Use

1. **Upload PDF**: Click on the file input or drag a PDF file onto the upload area
2. **Customize Headers** (optional):
   - Edit the College Name field
   - Edit the Department Name field
3. **Process**: Click "Process & Download" button
4. **Download**: The generated PDF will automatically download
5. **Print**: Each page contains 2 student mark slips (optimized for A4 printing)

## What's New

✨ **Recent Updates:**

- ✅ MIT logo added to the left corner of every student slip
- ✅ **2 student slips per A4 page** (efficient for printing)
- ✅ Compact layout optimized for readability
- ✅ Improved header design with logo integration

## Expected PDF Format

The input PDF should have:

- One page per student
- Register Number (e.g., "Register Number: AB123")
- Student Name (e.g., "Student Name: John Doe")
- A table with columns: S.No, Course Code, Course Name, Grade, Result

Example:

```

Register Number: AB-2020-001
Student Name: John Doe
First Semester Result - Nov / Dec 2025

S.No Course Code Course Name Grade Result
1 CSE101 Programming in C A PASS
2 CSE102 Data Structures B+ PASS

````

## Output

- **Combined PDF**: `student_mark_slips.pdf` - All student slips (2 per A4 page)
- **MIT Logo**: `mit_logo.png` - Auto-generated logo image
- Individual slip PDFs are generated temporarily during processing

## API Endpoints

### Health Check

- **GET** `/api/health` - Check if server is running

### Process PDF

- **POST** `/api/process` - Upload and process PDF
  - Form data:
    - `file` (required) - PDF file
    - `college` (optional) - College name
    - `dept` (optional) - Department name
  - Response: PDF binary data (with logo and 2-up layout)

## Troubleshooting

### "No student data found"

- Check that your PDF has the correct format
- Ensure text is extractable (not scanned image)
- Verify Register Number and Student Name fields are present

### File too large error

- Maximum file size is 50MB
- Reduce the number of pages or use a smaller PDF

### Logo not appearing

- Pillow (PIL) might not be installed correctly
- Run: `pip install --upgrade Pillow`
- The app will auto-generate a simple text logo if needed

### Module not found errors

```bash
pip install --upgrade -r requirements.txt
````

### Port already in use

- Change port in app.py (line ~50): `port=5000` → `port=5001`

## Configuration

Edit `app.py` to customize:

- **Port**: Line ~50 - Change `port=5000`
- **Max file size**: Line 17 - Change `MAX_FILE_SIZE`
- **Allowed extensions**: Line 16 - Modify `ALLOWED_EXTENSIONS`

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **PDF Processing**: pdfplumber, reportlab, pypdf
- **Image Generation**: Pillow (PIL)
- **Server**: Werkzeug

## License

Created for educational purposes.

## Support

For issues related to:

- **Mark extraction**: Check PDF format and text extractability
- **Web interface**: Ensure JavaScript is enabled in browser
- **Dependencies**: Run `pip install --upgrade -r requirements.txt`
- **Logo generation**: Ensure Pillow is installed
