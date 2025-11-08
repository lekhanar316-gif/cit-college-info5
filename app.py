from flask import Flask, render_template, request, url_for, abort, send_from_directory
import csv
import os
import qrcode

app = Flask(__name__,
static_folder='static',static_url_path='/static')

# ---------- COLLEGE INFO ----------
COLLEGE = {
    "Name": "Cauvery Institute of Technology, Mandya",
    "Address": "Siddaiahnakoppalu Gate, Sundahalli, Mandya",
    "Pincode": "571402",
    "NAAC grade": "B++",
    "Phone": "+91-9448589780",
    "Email": "citmandya@gmail.com",
    "Established": "2014",
    "Vision": "To provide best technical education, training and research opportunities to inculcate good personality, discipline and ethical values to pursue Excellence, Empowering people and partnering in community development.",
    "Affiliation": "Visvesvaraya Technological University (VTU), Belagavi",
    "CET_code": "E227",
    "Accreditation": "AICTE Approved, NAAC Accredited, ISO 9001:2015"
}

# ✅ YouTube Embed Link (change video ID if you want)
YOUTUBE_EMBED = "https://www.youtube.com/embed/YmKzB9fmOXM"

# ---------- QR CONFIG ----------
QR_FOLDER = os.path.join('static', 'images', 'qr')
QR_FILE = os.path.join(QR_FOLDER, 'college_qr.png')
# -------------------------------


def load_csv_rows(path):
    """Helper to load CSV data (staff, facilities, etc)."""
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def ensure_qr_for_url(target_url):
    """Generate QR for the given full target_url (always regenerate for safety)."""
    try:
        os.makedirs(QR_FOLDER, exist_ok=True)
        img = qrcode.make(target_url)
        img.save(QR_FILE)
    except Exception as e:
        print("QR generation failed:", e)

# ---------- ROUTES ----------

@app.route('/')
def index():
    """Home page showing QR code and college summary."""
    base = request.url_root.rstrip('/')
    college_url = f"{base}{url_for('college_info')}"
    ensure_qr_for_url(college_url)
    return render_template('index.html', college=COLLEGE, qr_file='images/qr/college_qr.png')


@app.route('/college')
def college_info():
    """Main college info page — includes YouTube, facilities, visits, etc."""
    staff = load_csv_rows(os.path.join('data', 'staff.csv'))
    facilities = load_csv_rows(os.path.join('data', 'facilities.csv'))
    workshops = load_csv_rows(os.path.join('data', 'workshops.csv'))
    base = request.url_root.rstrip('/')
    ensure_qr_for_url(f"{base}{url_for('college_info')}")

    tied_companies = load_csv_rows(os.path.join('data', 'companies.csv'))  # companies with logos

    return render_template(
        'college_info.html',
        college=COLLEGE,
        staff_count=len(staff),
        facilities=facilities,
        workshops=workshops,
        youtube_embed=YOUTUBE_EMBED,
        tied_companies=tied_companies
    )


@app.route('/staff')
def staff_index():
    """Group staff by department."""
    staff = load_csv_rows(os.path.join('data', 'staff.csv'))
    depts = {}
    for s in staff:
        dept = s.get('department', 'Others').strip()
        depts.setdefault(dept, []).append(s)
    return render_template('staff.html', departments=depts)


@app.route('/staff/department/<dept>')
def staff_department(dept):
    """Show staff of specific department."""
    staff = load_csv_rows(os.path.join('data', 'staff.csv'))
    filtered = [s for s in staff if s.get('department', '').strip().lower() == dept.lower()]
    if not filtered:
        abort(404)
    return render_template('staff_department.html', department=dept, staff=filtered)


@app.route('/facilities')
def facilities_page():
    """Facilities page."""
    facilities = load_csv_rows(os.path.join('data', 'facilities.csv'))
    return render_template('facilities.html', facilities=facilities)


@app.route('/static/images/qr/<path:filename>')
def qr_img(filename):
    """Serve QR code image."""
    return send_from_directory(os.path.join('static', 'images', 'qr'), filename)

@app.route('/companies')
def companies_page():
    """Display tied-up companies."""
    companies = load_csv_rows(os.path.join('data', 'companies.csv'))
    return render_template('companies.html', companies=companies)


@app.route('/workshops')
def workshops():
    """Display workshops (replaces industrial visits)."""
    workshops = load_csv_rows(os.path.join('data', 'workshops.csv'))
    return render_template('workshops.html', workshops=workshops)


@app.route('/gallery')
def gallery():
    """Display gallery of cultural activities."""
    return render_template('gallery.html')


# ---------- RUN LOCALLY ----------
if __name__ == '__main__':
    # When testing locally use 0.0.0.0 (Render auto uses gunicorn)
    app.run(host='0.0.0.0', port=5000, debug=True)