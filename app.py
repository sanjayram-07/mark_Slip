"""
Flask Backend for Student Mark Slip Generator
Production-ready version with environment configuration
"""
import os
import re
import sys
import logging
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the mark slip generation functions
from a1 import extract_students, build_slip, combine_slips_simple, create_mit_logo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask Configuration
app = Flask(__name__, template_folder='templates')
CORS(app)

# Configuration from environment variables
class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', tempfile.gettempdir())
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))  # 50MB default
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        logger.error("SECRET_KEY environment variable is not set!")
        sys.exit(1)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Load appropriate configuration
config_name = os.getenv('FLASK_ENV', 'development')
if config_name == 'production':
    app.config.from_object(ProductionConfig)
    logger.info("Running in PRODUCTION mode")
elif config_name == 'testing':
    app.config.from_object(TestingConfig)
    logger.info("Running in TESTING mode")
else:
    app.config.from_object(DevelopmentConfig)
    logger.info("Running in DEVELOPMENT mode")

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Serve the frontend"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index: {str(e)}")
        return jsonify({'error': 'Failed to load interface'}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Student Mark Slip Generator API is running',
        'version': '1.0.0',
        'environment': config_name
    })


@app.route('/api/process', methods=['POST'])
def process_pdf():
    """Process uploaded PDF and generate mark slips"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            logger.warning("No file provided in request")
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            logger.warning("Empty filename provided")
            return jsonify({'error': 'No file selected'}), 400

        # Check file extension
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Get optional parameters
        college_name = request.form.get('college', 'Madras Institute of Technology')
        dept_name = request.form.get('dept', 'Department of Computer Technology')

        # Validate input sanitization
        college_name = college_name[:100] if college_name else 'Institution'
        dept_name = dept_name[:100] if dept_name else 'Department'

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_input = os.path.join(app.config['UPLOAD_FOLDER'], f"input_{filename}")
        
        try:
            file.save(temp_input)
            logger.info(f"File uploaded: {filename}")

            # Create MIT logo
            temp_dir = tempfile.mkdtemp()
            logo_path = create_mit_logo(os.path.join(temp_dir, "mit_logo.png"), size=60)

            # Extract student data
            logger.info(f"[1/3] Reading PDF: {temp_input}")
            students = extract_students(temp_input)
            logger.info(f"      Found {len(students)} student(s)")

            if not students:
                logger.warning(f"No student data found in {filename}")
                return jsonify({'error': 'No student data found in PDF. Check PDF format.'}), 400

            # Generate individual slips
            logger.info("[2/3] Generating individual slips with logo...")
            slip_paths = []

            for i, student in enumerate(students, start=1):
                safe_name = re.sub(r"[^\w]", "_", student["reg_no"] or f"student_{i}")
                out_path = os.path.join(temp_dir, f"{safe_name}.pdf")
                build_slip(student, out_path, college_name, dept_name, logo_path)
                slip_paths.append(out_path)
                logger.debug(f"      [{i}/{len(students)}] Generated slip for {student.get('name', 'Unknown')}")

            # Combine into one PDF
            logger.info("[3/3] Combining slips...")
            combined_path = os.path.join(temp_dir, "ALL_SLIPS.pdf")
            combine_slips_simple(slip_paths, combined_path)
            logger.info(f"✓ Done! Generated {len(students)} slips")

            # Read the combined PDF
            with open(combined_path, 'rb') as f:
                pdf_data = f.read()

            # Clean up temporary files
            import shutil
            shutil.rmtree(temp_dir)
            os.remove(temp_input)

            # Return the PDF
            logger.info(f"Successfully processed {len(students)} student records")
            return send_file(
                BytesIO(pdf_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='student_mark_slips.pdf'
            )

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
            return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500

    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    logger.warning("File too large uploaded")
    return jsonify({'error': 'File is too large. Maximum size is 50MB'}), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


@app.before_request
def log_request():
    """Log incoming requests"""
    logger.debug(f"Request: {request.method} {request.path}")


@app.after_request
def log_response(response):
    """Log outgoing responses"""
    logger.debug(f"Response: {response.status_code}")
    return response


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    if config_name == 'production':
        logger.info("Starting production server...")
        # In production, use gunicorn (see Procfile)
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        logger.info("Starting development server...")
        print("=" * 60)
        print("Student Mark Slip Generator - Backend")
        print("=" * 60)
        print("Starting Flask server...")
        print(f"Open http://localhost:{port} in your browser")
        print("=" * 60)
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
