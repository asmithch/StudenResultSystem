# StudenResultSystem


# 🎓 Student Result Management System

A web-based system built using **Flask** and **MySQL** to manage and display student academic records, including subject-wise and class-wise rankings.

---

## 🚀 Features

- Add and manage student profiles.
- Assign grades and marks to students by subject.
- Automatically calculate:
  - Total marks per student.
  - Overall grade based on average.
  - Class-wise ranking.
  - Subject-wise ranking across all classes.
- Display results dynamically on a web interface.
- Validation and error handling included.

---

## 🏗️ Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, Jinja2 (templating), Bootstrap (optional)
- **Database**: MySQL
- **ORM**: MySQLdb connector

---

## 🔧 Setup Instructions

### ✅ Prerequisites

- Python 3.x
- MySQL Server installed and running
- Create a MySQL database (e.g. `student_result_db`)
- Install dependencies:

```bash
pip install flask mysqlclient


StudentResultSystem/
├── app.py                 # Main Flask app
├── config.py              # DB config
├── templates/
│   └── home.html          # Jinja2 Template
├── static/
│   └── style.css          # Optional CSS
└── README.md



# config.py
MYSQL_HOST = 'localhost'
MYSQL_USER = 'your_mysql_user'
MYSQL_PASSWORD = 'your_mysql_password'
MYSQL_DB = 'student_result_db'
SECRET_KEY = 'yoursecretkey'

DEBUG = True
HOST = '127.0.0.1'
PORT = 5000
Make sure your database student_result_db exists and the user has access to it.

▶️ Running the App
python app.py
Open http://127.0.0.1:5000 in your browser.
📝 Functional Overview
1. Add Students
Form to submit student details:
Name, DOB, Class, Email, Phone

2. Add Grades
Form to add/edit grades per subject:

Input: Student ID, Subject, Marks, Grade

If grade exists, it's updated. Otherwise, inserted.

3. Auto Calculations
Total Marks: Sum of all subject marks.

Overall Grade: Based on average:

A: 90+

B: 80–89

C: 70–79

D: 60–69

F: <60

4. Rankings
Class-wise: Sorted by total marks and grade.

Subject-wise: Sorted by subject marks and grade.

💻 Output Sections (UI)
Student listing

Grade sheet table

Subject-wise ranking table

Class-wise ranking table

📬 Future Improvements
Add authentication (admin login)

Export results to PDF

AJAX support for live updating

Mobile responsiveness

🧑‍💻 Author
Developed by Asmitha Challagundla

For educational and project submission purposes.

📄 License
This project is licensed under the MIT License.

✅ requirements.txt
Use this to install all necessary Python dependencies:
Flask==2.3.2
mysqlclient==2.2.0
📦 To install dependencies, run:
pip install -r requirements.txt
🗄️ schema.sql
Use this file to create the MySQL database and required tables manually (if not auto-created by app.py):
-- Create database
CREATE DATABASE IF NOT EXISTS student_result_db;
USE student_result_db;

-- Table: students
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
);

-- Table: grades
CREATE TABLE IF NOT EXISTS grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    marks INT NOT NULL,
    grade VARCHAR(2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
📥 To import into MySQL:

Log in to MySQL from the terminal:
mysql -u your_username -p
Run the script:
SOURCE path/to/schema.sql;

