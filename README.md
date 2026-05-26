# 🎓 AI-Powered Internship Maintenance Portal

A full-stack web application built with **Python Flask**, **MySQL**, **Bootstrap 5**, and **AI/ML modules** for managing internships, tracking student performance, and automating resume screening.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Database Setup (XAMPP)](#database-setup)
- [Running the Project](#running-the-project)
- [User Roles & Login](#user-roles)
- [API Endpoints](#api-endpoints)
- [AI Modules](#ai-modules)
- [Deployment](#deployment)

---

## 🌟 Overview

The **AI-Powered Internship Maintenance Portal** manages the complete internship lifecycle:
- Students apply for internships, upload resumes, submit reports, and track progress
- Mentors assign tasks, review reports, and provide feedback
- Admins manage everything and generate certificates
- AI automatically screens resumes and predicts student performance

---

## ✅ Features

### Authentication
- Role-based login (Admin / Mentor / Student)
- Secure password hashing (Werkzeug pbkdf2:sha256)
- Session management with Flask-Login
- Flash messages and form validation

### Admin Module
- Dashboard with live analytics and charts
- Add/Edit/Delete students and mentors
- Create and manage internships
- Approve/Reject student applications
- Generate completion certificates
- Monitor all reports and attendance

### Student Module
- Personal dashboard with progress tracker
- Browse and apply for open internships
- Upload resume for AI screening
- Mark daily attendance
- Submit weekly/monthly/final reports
- View mentor feedback and task status
- Download certificates

### Mentor Module
- View all assigned students
- Assign tasks with deadlines and priorities
- Review and approve student reports
- Provide star-rated feedback
- Monitor attendance and task completion

### AI/ML Modules
- **Resume Analyzer** — NLP-based skill extraction + TF-IDF cosine similarity scoring
- **Performance Predictor** — Ensemble ML model (Random Forest + Logistic Regression)

---

## 🛠 Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js |
| Backend     | Python 3.10+, Flask 3.0             |
| Database    | MySQL 8.0 (via XAMPP phpMyAdmin)    |
| ORM         | SQLAlchemy 2.0                      |
| Auth        | Flask-Login, Werkzeug               |
| AI/ML       | scikit-learn, NLTK, spaCy, PyPDF2   |
| Security    | Flask-WTF CSRF, password hashing    |

---

## 📁 Project Structure

```
internship-portal/
├── backend/
│   ├── app.py                  ← Flask app factory & entry point
│   ├── config.py               ← Configuration (DB, uploads, secrets)
│   ├── requirements.txt        ← Python dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_model.py       ← User auth model
│   │   ├── student_model.py    ← Student profile
│   │   ├── mentor_model.py     ← Mentor profile
│   │   ├── internship_model.py ← Internship + Application
│   │   └── attendance_model.py ← Attendance, Task, Report, Feedback, Certificate
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py      ← Login, Register, Logout
│   │   ├── admin_routes.py     ← Admin CRUD + approvals
│   │   ├── student_routes.py   ← Student dashboard + actions
│   │   ├── mentor_routes.py    ← Mentor dashboard + actions
│   │   ├── attendance_routes.py
│   │   ├── task_routes.py
│   │   ├── report_routes.py
│   │   └── ai_routes.py        ← AI/ML REST APIs
│   ├── templates/              ← Jinja2 HTML templates
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── uploads/            ← Uploaded files
│   ├── ai/
│   │   ├── resume_analyzer.py  ← NLP resume screening
│   │   └── performance_predictor.py ← ML performance prediction
│   └── database/
│       └── internship_portal_db.sql
├── certificates/               ← Generated certificates
└── README.md
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- XAMPP (for MySQL)
- Git

### Step 1 — Clone the Repository
```bash
git clone https://github.com/yourusername/internship-portal.git
cd internship-portal
```

### Step 2 — Create Virtual Environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3 — Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Download AI Model Data
```bash
# NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"

# spaCy English model
python -m spacy download en_core_web_sm
```

---

## 🗄 Database Setup (XAMPP)

### Step 1 — Install XAMPP
Download from: https://www.apachefriends.org/download.html

### Step 2 — Start Apache and MySQL
1. Open **XAMPP Control Panel**
2. Click **Start** next to **Apache**
3. Click **Start** next to **MySQL**

### Step 3 — Create the Database
1. Open browser → go to `http://localhost/phpmyadmin`
2. Click **"New"** in the left sidebar
3. Enter database name: `internship_portal_db`
4. Click **Create**

### Step 4 — Import the SQL File
1. Click on `internship_portal_db` in the left sidebar
2. Click the **"Import"** tab at the top
3. Click **"Choose File"**
4. Navigate to: `backend/database/internship_portal_db.sql`
5. Click **"Go"** at the bottom

### Step 5 — Verify Connection String
In `backend/config.py`, the connection string should be:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/internship_portal_db'
```
> If your MySQL has a password, update it: `mysql+pymysql://root:YOUR_PASSWORD@localhost/internship_portal_db`

---

## ▶️ Running the Project

```bash
# Make sure you're in the backend/ directory with venv activated
cd backend
python app.py
```

Open browser: **http://localhost:5000**

---

## 👥 User Roles & Default Login

| Role    | Email                      | Password   |
|---------|----------------------------|------------|
| Admin   | admin@internship.com       | Admin@123  |
| Mentor  | mentor1@internship.com     | Admin@123  |
| Student | student1@internship.com    | Admin@123  |

> ⚠️ **Change these passwords after first login!**

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint         | Description        |
|--------|------------------|--------------------|
| POST   | /auth/api/login  | Login (JSON)       |
| GET    | /auth/logout     | Logout             |

### Admin
| Method | Endpoint                    | Description           |
|--------|-----------------------------|-----------------------|
| GET    | /admin/api/stats            | Dashboard statistics  |
| GET    | /admin/api/students         | All students (JSON)   |
| GET    | /admin/api/internships      | All internships (JSON)|
| POST   | /admin/applications/approve/<id> | Approve application |
| POST   | /admin/applications/reject/<id>  | Reject application  |

### Student
| Method | Endpoint                        | Description        |
|--------|---------------------------------|--------------------|
| GET    | /student/api/profile            | Student profile    |
| POST   | /student/apply/<internship_id>  | Apply internship   |
| POST   | /student/mark-attendance        | Mark attendance    |

### AI/ML
| Method | Endpoint                  | Description               |
|--------|---------------------------|---------------------------|
| POST   | /ai/resume-analyze        | Analyze resume PDF        |
| POST   | /ai/performance-predict   | Predict performance (JSON)|
| POST   | /ai/api/batch-predict     | Batch predict (admin)     |

### Performance Predict Payload
```json
{
  "attendance_pct": 85,
  "task_completion": 90,
  "report_submissions": 4,
  "mentor_rating": 4.5
}
```

### Performance Predict Response
```json
{
  "success": true,
  "prediction": {
    "performance_grade": "Excellent",
    "overall_score": 87.5,
    "confidence": 92.3,
    "recommendations": ["Keep maintaining this performance!"],
    "model_used": "Ensemble (Random Forest + Logistic Regression)"
  }
}
```

---

## 🤖 AI Modules

### 1. Resume Analyzer (`ai/resume_analyzer.py`)

**How it works:**
1. Extracts text from uploaded PDF using **PyPDF2**
2. Tokenizes and removes stopwords using **NLTK**
3. Identifies named entities and noun chunks using **spaCy**
4. Matches extracted skills against a database of 80+ tech skills
5. Computes **TF-IDF cosine similarity** between resume and job requirements
6. Final score = 70% skill match + 30% TF-IDF similarity

**Output:**
- Match score (0–100%)
- Matched skills ✅
- Missing skills ❌
- Recommendation grade (A/B/C/D)

### 2. Performance Predictor (`ai/performance_predictor.py`)

**Features used:**
| Feature            | Weight |
|--------------------|--------|
| Attendance %       | 30%    |
| Task Completion %  | 35%    |
| Report Submissions | 15%    |
| Mentor Rating      | 20%    |

**Algorithms:**
- **Random Forest** (100 trees, balanced class weights) — 65% weight
- **Logistic Regression** (multinomial, L2) — 35% weight
- **Ensemble** of both for final prediction

**Output Grades:**
- 🏆 Excellent (≥80%)
- 👍 Good (65–79%)
- ➖ Average (50–64%)
- ⚠️ Needs Improvement (<50%)

---

## ☁️ Deployment

### Option 1: Render (Recommended — Free tier)

1. Push code to GitHub
2. Go to https://render.com → New Web Service
3. Connect your GitHub repo
4. Configure:
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && gunicorn app:create_app()`
5. Add environment variables:
   - `DATABASE_URL` = your MySQL connection string
   - `SECRET_KEY` = a long random string
6. Click **Deploy**

### Option 2: Railway

1. Go to https://railway.app
2. New Project → Deploy from GitHub repo
3. Add MySQL plugin → copy `DATABASE_URL`
4. Set environment variables
5. Railway auto-detects Python and deploys

### Option 3: PythonAnywhere (Free)

1. Go to https://www.pythonanywhere.com
2. Upload your project files
3. Create a MySQL database in the Databases tab
4. Configure WSGI file to point to your `app.py`
5. Reload the web app

### Production Environment Variables
```bash
SECRET_KEY=your-very-long-random-secret-key-here
DATABASE_URL=mysql+pymysql://user:password@host/internship_portal_db
FLASK_ENV=production
```

---

## 🔒 Security Features

- ✅ Password hashing with `pbkdf2:sha256` (Werkzeug)
- ✅ CSRF protection on all forms (Flask-WTF)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Role-based access control decorators
- ✅ File upload validation (type + size)
- ✅ Session management (Flask-Login)
- ✅ Input validation and sanitization

---

## 🐛 Troubleshooting

**MySQL connection error:**
```
Check XAMPP MySQL is running
Verify connection string in config.py
```

**spaCy model not found:**
```bash
python -m spacy download en_core_web_sm
```

**PyPDF2 import error:**
```bash
pip install PyPDF2==3.0.1
# or newer
pip install pypdf
```

**Port 5000 already in use:**
```python
# In app.py, change port:
app.run(port=5001)
```

---

## 📜 License

MIT License — Free to use and modify.

---

## 👨‍💻 Author

Built with ❤️ using Flask + AI/ML  
**AI-Powered Internship Maintenance Portal** — 2024
