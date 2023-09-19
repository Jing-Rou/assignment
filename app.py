from flask import Flask, render_template, request, redirect, url_for, flash
from pymysql import connections
import os
import boto3
from config import *
import hashlib
import secrets

secret_key = secrets.token_hex(16)  # Generate a 32-character (16-byte) hexadecimal key
print(secret_key)

app = Flask(__name__)
# Configure the 'templates' folder for HTML templates.
app.template_folder = 'pages'
app.static_folder = 'static'

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'students'

@app.route("/", methods=['GET'], endpoint='index')
def index():
    return render_template('index.html')

@app.route("/job_listing", methods=['GET'])
def job_listing():
    return render_template('job_listing.html')

@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')

@app.route("/blog", methods=['GET'])
def blog():
    return render_template('blog.html')

@app.route("/single_blog", methods=['GET'])
def single_blog():
    return render_template('single_blog.html')

@app.route("/elements", methods=['GET'])
def elements():
    return render_template('elements.html')

@app.route("/job_details", methods=['GET'])
def job_details():
    return render_template('job_details.html')

@app.route("/contact", methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']
        ic = request.form['ic']
        programmeSelect = request.form['programmeSelect']
        tutorialGrp = request.form['tutorialGrp']
        studentID = request.form['studentID']
        cgpa = request.form['cgpa']
        ucSupervisor = request.form['ucSupervisor']
        ucSupervisorEmail = request.form['ucSupervisorEmail']
        
        # Check if the email is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM students WHERE stud_email=%s", (email))
        results = cursor.fetchall()
        cursor.close()

        # If the email is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', email_error="The email is already in use.")

        # Otherwise, check if the IC is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM students WHERE ic=%s", (ic))
        results = cursor.fetchall()
        cursor.close()

        # If the IC is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', ic_error="The IC is already in use.")

        # Otherwise, check if the student ID is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM students WHERE studentID=%s", (studentID))
        results = cursor.fetchall()
        cursor.close()

        # If the student ID is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', studentID_error="The student ID is already in use.")

        insert_sql = "INSERT INTO students VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        
        try:
            cursor.execute(insert_sql, (firstName, 
                                        lastName, 
                                        gender,
                                        email, 
                                        password,
                                        ic,
                                        programmeSelect,
                                        tutorialGrp,
                                        studentID, 
                                        cgpa,
                                        ucSupervisor
                                        ))
            db_conn.commit()
            cursor.close()
            return redirect(url_for('login'))  # Redirect to the homepage after successful registration
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here
    
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Fetch data from the database here
        cursor = db_conn.cursor()
        select_sql = "SELECT stud_email, password FROM students WHERE stud_email = %s"
        cursor.execute(select_sql, (email,))
        data = cursor.fetchone()  # Fetch a single row
        
        if data:
            # Data is found in the database
            stored_password = data[1]
            # You should hash the provided password and compare it to the stored hashed password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            if hashed_password == stored_password:
                # Passwords match, user is authenticated
                return render_template('index.html', user_authenticated=True)
            else:
                flash('Incorrect password. Please try again.', 'danger')
        else:
            flash('Email not found. Please register or try a different email.', 'danger')

        cursor.close()
    
    return render_template('login.html')

@app.route("/studentDashboard", methods=['GET'])
def studentDashboard():
    return render_template('studentDashboard.html')

@app.route("/form", methods=['GET'])
def form():
    return render_template('form.html')

@app.route("/report", methods=['GET'])
def report():
    return render_template('report.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)