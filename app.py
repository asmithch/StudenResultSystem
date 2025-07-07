from flask import Flask, render_template, request, redirect, flash, url_for
import MySQLdb
import config
import logging
from collections import defaultdict

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        return MySQLdb.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            passwd=config.MYSQL_PASSWORD,
            db=config.MYSQL_DB,
            port=getattr(config, 'MYSQL_PORT', 3306),
            charset=getattr(config, 'MYSQL_CHARSET', 'utf8mb4'),
            autocommit=True
        )
    except MySQLdb.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

db = get_db_connection()
cursor = db.cursor() if db else None

if db and cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            dob DATE NOT NULL,
            class VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            phone VARCHAR(20) NOT NULL,
            total_marks INT DEFAULT 0,
            overall_grade VARCHAR(2) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            subject VARCHAR(100) NOT NULL,
            marks INT NOT NULL,
            grade VARCHAR(2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)
    db.commit()
    logger.info("Database tables created/verified successfully")
else:
    logger.error("Database not connected")

def calculate_student_totals():
    cursor.execute("SELECT id FROM students")
    students = cursor.fetchall()
    for (sid,) in students:
        cursor.execute("SELECT SUM(marks), AVG(marks) FROM grades WHERE student_id = %s", (sid,))
        total, avg = cursor.fetchone()
        total = total or 0
        avg = avg or 0
        grade = None
        if avg >= 90: grade = 'A'
        elif avg >= 80: grade = 'B'
        elif avg >= 70: grade = 'C'
        elif avg >= 60: grade = 'D'
        elif avg > 0: grade = 'F'
        cursor.execute("UPDATE students SET total_marks = %s, overall_grade = %s WHERE id = %s", (total, grade, sid))
    db.commit()

@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.form
    cursor.execute("""
        INSERT INTO students (name, dob, class, email, phone) 
        VALUES (%s, %s, %s, %s, %s)
    """, (data['name'], data['dob'], data['class'], data['email'], data['phone']))
    db.commit()
    return redirect(url_for('index'))

@app.route('/add_grades', methods=['POST'])
def add_grades():
    data = request.form
    sid, subject, marks, grade = data['student_id'], data['subject'], int(data['marks']), data['grade']
    cursor.execute("SELECT id FROM grades WHERE student_id = %s AND subject = %s", (sid, subject))
    if cursor.fetchone():
        cursor.execute("UPDATE grades SET marks = %s, grade = %s WHERE student_id = %s AND subject = %s", (marks, grade, sid, subject))
    else:
        cursor.execute("INSERT INTO grades (student_id, subject, marks, grade) VALUES (%s, %s, %s, %s)", (sid, subject, marks, grade))
    db.commit()
    return redirect(url_for('index'))

@app.route('/')
def index():
    try:
        if db and cursor:
            calculate_student_totals()

            # All students
            cursor.execute("SELECT * FROM students ORDER BY id DESC")
            students = cursor.fetchall()

            # Class-wise rankings
            class_rankings = {}
            cursor.execute("SELECT DISTINCT class FROM students")
            classes = cursor.fetchall()
            for (cls,) in classes:
                cursor.execute("""
                    SELECT * FROM students 
                    WHERE class = %s AND total_marks > 0 
                    ORDER BY total_marks DESC, overall_grade ASC
                """, (cls,))
                class_rankings[cls] = cursor.fetchall()

            # Subject-wise rankings (within each class)
            subject_rankings = {}
            cursor.execute("SELECT DISTINCT subject FROM grades")
            subjects = cursor.fetchall()
            for (subject,) in subjects:
                subject_rankings[subject] = {}
                for (cls,) in classes:
                    cursor.execute("""
                        SELECT s.name, s.class, g.marks, g.grade
                        FROM students s
                        JOIN grades g ON s.id = g.student_id
                        WHERE s.class = %s AND g.subject = %s
                        ORDER BY g.marks DESC, g.grade ASC
                    """, (cls, subject))
                    subject_rankings[subject][cls] = cursor.fetchall()

            # Grade sheets (only one row per student)
            cursor.execute("""
                SELECT s.*, g.subject, g.marks, g.grade 
                FROM students s 
                LEFT JOIN grades g ON s.id = g.student_id 
                ORDER BY s.id, g.subject
            """)
            student_grades_raw = cursor.fetchall()

            student_ids_seen = set()
            student_grades = []
            for row in student_grades_raw:
                if row[0] not in student_ids_seen:
                    student_grades.append(row)
                    student_ids_seen.add(row[0])

            # Subject grades
            cursor.execute("""
                SELECT g.id, g.student_id, g.subject, g.marks, g.grade, s.name 
                FROM grades g 
                JOIN students s ON g.student_id = s.id 
                ORDER BY s.name, g.subject
            """)
            subject_grades = cursor.fetchall()

            return render_template(
                'home.html',
                students=students,
                student_grades=student_grades,
                student_subject_grades=subject_grades,
                class_rankings=class_rankings,
                subject_rankings=subject_rankings
            )
        else:
            flash("Database connection error", "error")
            return render_template('home.html', students=[], student_grades=[], student_subject_grades=[], class_rankings={}, subject_rankings={})
    except MySQLdb.Error as e:
        logger.error(f"Database query error: {e}")
        flash("Error retrieving student data", "error")
        return render_template('home.html', students=[], student_grades=[], student_subject_grades=[], class_rankings={}, subject_rankings={})

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
