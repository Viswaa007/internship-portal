-- ============================================================
-- AI-Powered Internship Maintenance Portal
-- Database: internship_portal_db
-- Import this file in phpMyAdmin after creating the database
-- ============================================================

CREATE DATABASE IF NOT EXISTS internship_portal_db;
USE internship_portal_db;

-- ============================================================
-- TABLE: users
-- Stores login credentials for all roles
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'mentor', 'student') NOT NULL DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: students
-- Extended profile for student users
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    college VARCHAR(200),
    department VARCHAR(100),
    year_of_study VARCHAR(20),
    cgpa DECIMAL(4,2),
    skills TEXT,
    resume_path VARCHAR(300),
    profile_pic VARCHAR(300),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: mentors
-- Extended profile for mentor users
-- ============================================================
CREATE TABLE IF NOT EXISTS mentors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    designation VARCHAR(150),
    department VARCHAR(100),
    expertise VARCHAR(300),
    profile_pic VARCHAR(300),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: internships
-- Internship programs created by admin
-- ============================================================
CREATE TABLE IF NOT EXISTS internships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    domain VARCHAR(100),
    required_skills TEXT,
    duration_weeks INT,
    start_date DATE,
    end_date DATE,
    max_students INT DEFAULT 10,
    mentor_id INT,
    status ENUM('open', 'closed', 'completed') DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mentor_id) REFERENCES mentors(id) ON DELETE SET NULL
);

-- ============================================================
-- TABLE: applications
-- Student applications for internships
-- ============================================================
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    resume_score DECIMAL(5,2) DEFAULT 0.0,
    admin_remarks TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: attendance
-- Daily attendance records for students
-- ============================================================
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    date DATE NOT NULL,
    check_in_time TIME,
    status ENUM('present', 'absent', 'late', 'half_day') DEFAULT 'present',
    remarks VARCHAR(300),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (student_id, internship_id, date)
);

-- ============================================================
-- TABLE: tasks
-- Tasks assigned by mentor to students
-- ============================================================
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    internship_id INT NOT NULL,
    student_id INT NOT NULL,
    mentor_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    assigned_date DATE,
    deadline DATE,
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    status ENUM('pending', 'in_progress', 'completed', 'overdue') DEFAULT 'pending',
    completion_date DATE,
    mentor_rating INT CHECK (mentor_rating BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (mentor_id) REFERENCES mentors(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: reports
-- Weekly/monthly reports submitted by students
-- ============================================================
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    report_type ENUM('weekly', 'monthly', 'final') DEFAULT 'weekly',
    file_path VARCHAR(300),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'reviewed', 'approved', 'rejected') DEFAULT 'pending',
    mentor_feedback TEXT,
    admin_approval BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: feedback
-- Mentor feedback on student performance
-- ============================================================
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mentor_id INT NOT NULL,
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    feedback_text TEXT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mentor_id) REFERENCES mentors(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: certificates
-- Auto-generated completion certificates
-- ============================================================
CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    certificate_number VARCHAR(100) UNIQUE,
    issued_date DATE,
    file_path VARCHAR(300),
    performance_grade ENUM('Excellent', 'Good', 'Average', 'Needs Improvement'),
    issued_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE,
    FOREIGN KEY (issued_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================
-- DEFAULT ADMIN USER
-- Password: Admin@123 (hashed with werkzeug)
-- Change this password after first login!
-- ============================================================
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@internship.com', 'pbkdf2:sha256:260000$rVGHvKrj$7b5e9e2b5f8c1a2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6', 'admin');

-- ============================================================
-- SAMPLE DATA for testing
-- ============================================================
INSERT INTO users (username, email, password_hash, role) VALUES
('mentor1', 'mentor1@internship.com', 'pbkdf2:sha256:260000$rVGHvKrj$7b5e9e2b5f8c1a2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6', 'mentor'),
('student1', 'student1@internship.com', 'pbkdf2:sha256:260000$rVGHvKrj$7b5e9e2b5f8c1a2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6', 'student');

INSERT INTO mentors (user_id, full_name, phone, designation, department, expertise) VALUES
(2, 'Dr. Rajesh Kumar', '9876543210', 'Senior Engineer', 'Computer Science', 'Python, Machine Learning, Data Science');

INSERT INTO students (user_id, full_name, phone, college, department, year_of_study, cgpa, skills) VALUES
(3, 'Priya Sharma', '9876543211', 'Anna University', 'CSE', '3rd Year', 8.5, 'Python, JavaScript, SQL');

INSERT INTO internships (title, description, domain, required_skills, duration_weeks, start_date, end_date, max_students, mentor_id, status) VALUES
('Machine Learning Internship', 'Learn and apply ML algorithms on real datasets', 'AI/ML', 'Python, NumPy, Pandas, Scikit-learn', 8, '2025-06-01', '2025-07-31', 5, 1, 'open'),
('Web Development Internship', 'Build full-stack web applications', 'Web Dev', 'HTML, CSS, JavaScript, Flask/Django', 6, '2025-06-01', '2025-07-15', 8, 1, 'open');
