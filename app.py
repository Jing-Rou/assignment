from flask import Flask, render_template, request, redirect, url_for
from pymysql import connections
import os
import boto3
from config import *
import hashlib

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
            cursor.execute(insert_sql, (studentID, 
                                        firstName, 
                                        lastName, 
                                        gender,
                                        email, 
                                        password,
                                        ic,
                                        programmeSelect,
                                        tutorialGrp,
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
        role = request.form.get('role')
        
        if role == 'Student':
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

                if password == stored_password:
                    # Passwords match, user is authenticated
                    return render_template('index.html', user_authenticated=True)
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")
        # else your own role bah

    return render_template('login.html')

@app.route("/studentDashboard", methods=['GET'])
def studentDashboard():
    return render_template('studentDashboard.html')

@app.route("/form", methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        acceptanceForm = request.files['acceptanceForm']
        parentForm = request.files['parentForm']
        letterForm = request.files['letterForm']
        hireEvi = request.files['hireEvi']

        if acceptanceForm.filename == "" and parentForm.filename == "" and letterForm.filename == "" and hireEvi.filename == "":
            return "Please select a file"
        
        # Uplaod image file in S3 #
        # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=acceptanceForm.filename, Body=acceptanceForm)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                acceptanceForm.filename)

        except Exception as e:
            return str(e)
            
    return render_template('form.html')

@app.route("/report", methods=['GET'])
def report():
    return render_template('report.html')

# -------------------------------------------------------------- Lecturer START (Kuah Jia Yu) --------------------------------------------------------------#
    
@app.route("/lectRegister", methods=['GET', 'POST'])
def lectRegister():
    if request.method == 'POST':
        lectName = request.form['lectName']
        lectID = request.form['lectID']
        lectEmail = request.form['lectEmail']
        gender = request.form['gender']
        password = request.form['password']

        insert_sql = "INSERT INTO lecturer VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        
        try:
            cursor.execute(insert_sql, (lectName, 
                                        lectID, 
                                        lectEmail, 
                                        gender, 
                                        password
                                        ))
            db_conn.commit()
            cursor.close()
            return redirect(url_for('login'))  # Go to the dashboard after successful registration
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here
    return render_template('lectRegister.html')
    
@app.route("/lectLogin", methods=['GET', 'POST'])
def lectLogin():
    if request.method == 'POST':
        return render_template('index.html', user_authenticated=True)
    
    # Fetch data from the database here
    cursor = db_conn.cursor()
    select_sql = "SELECT lectEmail, password FROM lecturer"
    cursor.execute(select_sql)
    data = cursor.fetchall()
    cursor.close()
    return render_template('lectLogin.html', lecturer=data)
    
@app.route("/lectDashboard", methods=['GET'])
def lectDashboard():
    return render_template('lectDashboard.html')
    
# ------------------------------------------------------------------- Lecturer END -------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)