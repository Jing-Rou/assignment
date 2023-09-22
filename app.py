from flask import Flask, render_template, request, redirect, url_for, session
from pymysql import connections
import os
import boto3
from config import *
from flask import send_from_directory
import urllib.parse 
from urllib.parse import unquote_plus

app = Flask(__name__)
app.secret_key = 'my_super_secret_key_12345'

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


def getCompFiles(path):
    contents = []
    folder_prefix = path

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(custombucket)
    expiration = 315360000  # 10 years in seconds
    for image in bucket.objects.filter(Prefix=folder_prefix):
        if (image.key.split('/')[1]):
            # Extract file name without the folder prefix
            file_name = image.key[len(folder_prefix):]
            contents.append("https://" + bucket.name + ".s3.amazonaws.com/Company/" + file_name)

    return contents


@app.route("/", methods=['GET'], endpoint='index')
def index():
    # retrive from database
    cursor = db_conn.cursor()
    select_sql = "SELECT c.compName, c.compProfile, j.job_title, j.comp_state, j.sal_range \
                 from company c \
                 JOIN jobApply j ON c.compID = j.compID \
                 where upper(c.compStatus) = 'APPROVED'"

    try:
        cursor.execute(select_sql)
        data = cursor.fetchall()  # Fetch a single row
        print(data)

    except Exception as e:
        return str(e)

    print(data)
    return render_template('index.html', comp_data=data)


@app.route("/job_listing", methods=['GET'])
def job_listing():
    # get approved company name
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

        ucSupervisor_split = ucSupervisor.split(', ')
        ucSuperName = ucSupervisor_split[0]
        ucSuperEmail = ucSupervisor_split[1]

        # Fetch data from the database here
        cursor = db_conn.cursor()
        select_sql = "SELECT lectName, lectEmail FROM lecturer"
        cursor.execute(select_sql)
        data = cursor.fetchall()  # Fetch a single row

        # If the email is already in the database, return an error message to the user and display it on the register.html page.
        if len(ic) != 12:
            return render_template('register.html', ic_error="Invalid IC number", list_of_lect=data)

        # Check if the email is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM students WHERE stud_email=%s", (email))
        results = cursor.fetchall()
        cursor.close()

        # If the email is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', email_error="The email is already in use.", list_of_lect=data)

        # Otherwise, check if the IC is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM students WHERE ic=%s", (ic))
        results = cursor.fetchall()
        cursor.close()

        # If the IC is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', ic_error="The IC is already in use.", list_of_lect=data)

        # Otherwise, check if the student ID is already in the database.
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE studentID=%s", (studentID))
        results = cursor.fetchall()
        cursor.close()

        # If the student ID is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', studentID_error="The student ID is already in use.", list_of_lect=data)

        # Extract the birthdate portion from the IC number
        birthdate_part = ic[:6]

        # Parse the birthdate in YYMMDD format
        year = int(birthdate_part[:2])
        month = int(birthdate_part[2:4])
        day = int(birthdate_part[4:])

        # Convert to a full date of birth
        # Assumption: This code assumes the IC number represents birthdates from 1900 to 2099
        if year >= 0 and year <= 99:
            if year >= 0 and year <= 30:
                year += 2000
            else:
                year += 1900

        dob = f"{year:04}-{month:02}-{day:02}"

        insert_sql = "INSERT INTO students (studentID, firstName, lastName, gender, stud_email, password, ic, programme, tutGroup, cgpa, ucSupevisor, ucSuperEmail, dob) \
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
                                        ucSuperName,
                                        ucSuperEmail,
                                        dob
                                        ))
            db_conn.commit()
            cursor.close()
            # Redirect to the homepage after successful registration
            return redirect(url_for('login'))
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here

    # Fetch data from the database here
    cursor = db_conn.cursor()
    select_sql = "SELECT lectName, lectEmail FROM lecturer"
    cursor.execute(select_sql)
    data = cursor.fetchall()  # Fetch a single row

    return render_template('register.html', list_of_lect=data)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if role == 'Student':
            # Fetch data from the database here
            cursor = db_conn.cursor()
            select_sql = "SELECT stud_email, password, firstName, studentID FROM students WHERE stud_email = %s"
            cursor.execute(select_sql, (email,))
            data = cursor.fetchone()  # Fetch a single row

            if data:
                # Data is found in the database
                stored_password = data[1]
                name = data[2]
                studID = data[3]

                if password == stored_password:
                    # Passwords match, user is authenticated
                    return render_template('index.html', user_login_name=name, studentID=studID, user_authenticated=True)
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")
        elif role == 'Company':
            # Fetch data from the database here
            cursor = db_conn.cursor()
            select_sql = "SELECT compEmail, comPassword, compName, compID FROM company WHERE compEmail = %s"
            cursor.execute(select_sql, (email,))
            data = cursor.fetchone()  # Fetch a single row

            if data:
                # Data is found in the database
                stored_password = data[1]
                name = data[2]

                if password == stored_password:
                    session['user_login_name'] = name
                    session['compID'] = data[3] 

                    # Fetch job data from the database (assuming you have a SQL query for this)
                    select_sql = "SELECT * FROM jobApply J JOIN company C ON C.compID = J.compID WHERE C.compID = %s"
                    cursor = db_conn.cursor()
                    cursor.execute(select_sql, (data[3],))
                    job_data = cursor.fetchall()
                    cursor.close()

                    # Passwords match, user is authenticated
                    return render_template('companyDashboard.html', user_login_name=name, job_data=job_data)
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")
        elif role == 'Admin':
            # Fetch data from the database here
            cursor = db_conn.cursor()
            select_sql = "SELECT adminEmail, adminPassword, adminName FROM admin WHERE adminEmail = %s"
            cursor.execute(select_sql, (email,))
            data = cursor.fetchone()  # Fetch a single row

            if data:
                # Data is found in the database
                stored_password = data[1]
                name = data[2]

                if password == stored_password:
                    # Passwords match, user is authenticated
                    return render_template('index.html', user_login_name=name, studentID=None, user_authenticated=True)
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")
        elif role == 'Lecturer':
            # Fetch data from the database here
            cursor = db_conn.cursor()
            select_sql = "SELECT lectEmail, password, lectID FROM lecturer WHERE lectEmail = %s"
            cursor.execute(select_sql, (email,))
            data = cursor.fetchone()  # Fetch a single row

            if data:
                # Data is found in the database
                stored_password = data[1]
                lecturer_id = data[2]

                if password == stored_password:
                    # Passwords match, user is authenticated
                    # Fetch student data for this lecturer
                    select_students_sql = "SELECT * \
                                        FROM students s\
                                        JOIN lecturer l on s.ucSuperEmail = l.lectEmail \
                                        WHERE l.lectEmail = %s"
                    cursor.execute(select_students_sql, (email,))
                    student_data = cursor.fetchall()

                    return render_template('lectDashboard.html', lectID=lecturer_id, student_data=student_data)
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")

    return render_template('login.html')


@app.route("/studentDashboard", methods=['GET'])
def studentDashboard():
    # Retrieve the studentID from the query parameters
    student_id = request.args.get('studentID')

    # Pass the studentID to the studentDashboard.html template
    return render_template('studentDashboard.html', studentID=student_id)


@app.route("/studentProfile", methods=['GET', 'POST'])
def studentProfile():
    # Retrieve the studentID from the query parameters
    student_id = request.args.get('studentID')

    # retrive from database
    cursor = db_conn.cursor()
    select_sql = "SELECT * from students where studentID = %s"

    try:
        cursor.execute(select_sql, (student_id))
        data = cursor.fetchall()  # Fetch a single row
        data = data[0]

        # Create a new list with the modified value
        data_list = list(data)
        data_list[12] = str(data_list[12])[:10]
        data = tuple(data_list)  # Convert the list back to a tuple

    except Exception as e:
        return str(e)

    # Pass the studentID to the studentDashboard.html template
    return render_template('studentProfile.html', studentID=student_id, student_infor=data)

@app.route("/studentProfilePersonal", methods=['POST'])
def studentProfilePersonal():
    # Get the form data from the request
    gender = request.form.get('genderField')
    nric = request.form.get('nric')
    dob = request.form.get('dob')
    contact = request.form.get('contact')
    homeAdd = request.form.get('homeAdd')
    correspondenceAdd = request.form.get('correspondenceAdd')

    # Retrieve the studentID from the query parameters
    student_id = request.form.get('studentID')
    print(gender, nric, dob, contact, homeAdd, correspondenceAdd)
    
    # Update database
    update_sql = "UPDATE students SET gender = %s, \
                                      ic = %s, \
                                      dob = %s, \
                                      contact = %s, \
                                      homeAddress = %s, \
                                      correspondenceAddress = %s \
                  WHERE studentID = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (gender, nric, dob, contact, homeAdd, correspondenceAdd, student_id))
        db_conn.commit()
        cursor.close()

        # retrive from database
        cursor = db_conn.cursor()
        select_sql = "SELECT * from students where studentID = %s"

        try:
            cursor.execute(select_sql, (student_id))
            data = cursor.fetchall()  # Fetch a single row
            data = data[0]

            # Create a new list with the modified value
            data_list = list(data)
            data_list[12] = str(data_list[12])[:10]
            data = tuple(data_list)  # Convert the list back to a tuple

        except Exception as e:
            return str(e)

        # Pass the studentID to the studentDashboard.html template
        return render_template('studentProfile.html', studentID=student_id, student_infor=data)
    except Exception as e:
        cursor.close()
        return str(e)  # Handle any database errors here
    
@app.route("/studentPersonal", methods=['POST'])
def studentPersonal():
    # Get the form data from the request
    stud_email = request.form.get('email')
    programme = request.form.get('programme')
    tutGroup = request.form.get('tutGroup')
    cgpa = request.form.get('cgpa')

    # Retrieve the studentID from the query parameters
    student_id = request.form.get('studentID')
    
    # Update database
    update_sql = "UPDATE students SET stud_email = %s, \
                                      programme = %s, \
                                      tutGroup = %s, \
                                      cgpa = %s \
                  WHERE studentID = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (stud_email, programme, tutGroup, cgpa, student_id))
        db_conn.commit()
        cursor.close()

        # retrive from database
        cursor = db_conn.cursor()
        select_sql = "SELECT * from students where studentID = %s"

        try:
            cursor.execute(select_sql, (student_id))
            data = cursor.fetchall()  # Fetch a single row
            data = data[0]

            # Create a new list with the modified value
            data_list = list(data)
            data_list[12] = str(data_list[12])[:10]
            data = tuple(data_list)  # Convert the list back to a tuple

        except Exception as e:
            return str(e)

        # Pass the studentID to the studentDashboard.html template
        return render_template('studentProfile.html', studentID=student_id, student_infor=data)
    except Exception as e:
        cursor.close()
        return str(e)  # Handle any database errors here

@app.route("/form", methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        studID = request.form['studentID']

        # put the files into array
        # use the get() method to return None if the field is not present.
        uploaded_files = [' ', ' ', ' ', ' ']
        uploaded_files[0] = request.files.get('acceptanceForm')
        uploaded_files[1] = request.files.get('parentForm')
        uploaded_files[2] = request.files.get('letterForm')
        uploaded_files[3] = request.files.get('hireEvi')

        comp_form = request.form.get('acceptanceFormFileName', None)
        parent_form = request.form.get('parentFormFileName', None)
        letter = request.form.get('letterFormFileName', None)
        hire_evi = request.form.get('hireEviFileName', None)

        # Uplaod image file in S3
        s3 = boto3.resource('s3')

        # Create a folder or prefix for the files in S3
        # submit form and store into student s3
        folder_name = 'Student/' + studID + "/" + "Form/"

        # Fetch data from the lecturer database
        cursor = db_conn.cursor()
        select_sql = "SELECT l.lectID \
                      FROM students s\
                      JOIN lecturer l on s.ucSuperEmail = l.lectEmail \
                      WHERE studentID = %s"
        cursor.execute(select_sql, (studID,))
        data = cursor.fetchone()  # Fetch a single row

        lecturerID = data[0]

        # submit form to lecturer
        lect_folder_name = 'Lecturer/' + lecturerID + "/" + studID + "/" + "Form/"

        list_files = []
        form_list = ['_comp_form.', '_parent_form.', '_letter.', '_hire_evi.']
        ctr = 0

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")

            for file in uploaded_files:
                if file is None:
                    list_files.append('')
                else:
                    list_files.append(file.filename)

                # if not empty
                if file and file is not None:
                    filename = file.filename.split('.')

                    # Construct the key with the folder prefix and file name
                    # student
                    stud_key = folder_name + \
                        filename[0] + form_list[ctr] + filename[1]
                    # lecture
                    lect_key = lect_folder_name + \
                        filename[0] + form_list[ctr] + filename[1]

                    # Upload the file into the specified folder
                    # to student folder
                    s3.Bucket(custombucket).put_object(Key=stud_key, Body=file)
                    # to lecturer folder
                    s3.Bucket(custombucket).put_object(Key=lect_key, Body=file)

                    # Generate the object URL
                    bucket_location = boto3.client(
                        's3').get_bucket_location(Bucket=custombucket)
                    s3_location = (bucket_location['LocationConstraint'])

                    if s3_location is None:
                        s3_location = ''
                    else:
                        s3_location = '-' + s3_location

                ctr += 1

        except Exception as e:
            return str('bucket', str(e))

        # get the submitted form w/o reupload it into s3
        if comp_form:
            list_files[0] = comp_form

        if parent_form:
            list_files[1] = parent_form

        if letter:
            list_files[2] = letter

        if hire_evi:
            list_files[3] = hire_evi

        bucket = s3.Bucket(custombucket)

        return render_template('form.html', my_bucket=bucket, studentID=studID, list_of_files=list_files)

    # Retrieve the studentID from the query parameters
    student_id = request.args.get('studentID')

    return render_template('form.html', studentID=student_id)


def list_files(bucket, path):
    contents = []
    folder_prefix = path

    for object_summary in bucket.objects.filter(Prefix=folder_prefix):
        # Extract file name without the folder prefix
        file_name = object_summary.key[len(folder_prefix):]
        if file_name:
            last_modified = object_summary.last_modified
            size = object_summary.size
            contents.append({
                'file_name': file_name,
                'last_modified': last_modified,
                'size': size
            })

    return contents


@app.route("/report", methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        studID = request.form['studentID']
        reportForm_files = request.files['reportForm']

        # Uplaod image file in S3
        s3 = boto3.resource('s3')

        # Create a folder or prefix for the files in S3
        # to student s3 folder
        folder_name = 'Student/' + studID + "/" + "report/"

        # Fetch data from the lecturer database
        cursor = db_conn.cursor()
        select_sql = "SELECT l.lectID \
                      FROM students s\
                      JOIN lecturer l on s.ucSuperEmail = l.lectEmail \
                      WHERE studentID = %s"
        cursor.execute(select_sql, (studID,))
        data = cursor.fetchone()  # Fetch a single row

        lecturerID = data[0]

        # submit form to lecturer
        lect_folder_name = 'Lecturer/' + lecturerID + "/" + studID + "/" + "report/"

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")

            filename = reportForm_files.filename.split('.')

            # Construct the key with the folder prefix and file name
            stud_key = folder_name + \
                filename[0] + "_progress_report." + filename[1]
            # lecture
            lect_key = lect_folder_name + \
                filename[0] + "_progress_report." + filename[1]

            # Upload the file into the specified folder
            # to student folder
            s3.Bucket(custombucket).put_object(
                Key=stud_key, Body=reportForm_files)
            # to lecturer folder
            s3.Bucket(custombucket).put_object(
                Key=lect_key, Body=reportForm_files)

            # Generate the object URL
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

        except Exception as e:
            return str('bucket', str(e))

        bucket = s3.Bucket(custombucket)
        list_of_files = list_files(bucket, folder_name)

        return render_template('report.html', my_bucket=bucket, studentID=studID, list_of_files=list_of_files)

    # Retrieve the studentID from the query parameters
    studID = request.args.get('studentID')

    folder_name = 'Student/' + studID + "/" + "report/"

    # Uplaod image file in S3
    s3 = boto3.resource('s3')

    bucket = s3.Bucket(custombucket)
    list_of_files = list_files(bucket, folder_name)

    # Sort the list by last modified timestamp in descending order
    list_of_files.sort(key=lambda x: x['last_modified'], reverse=True)

    return render_template('report.html', my_bucket=bucket, studentID=studID, list_of_files=list_of_files)


@app.route("/delete", methods=['POST'])
def delete_file():
    if request.method == 'POST':
        studID = request.form['studentID']
        print(studID)
        # Get the file key to delete from the form data
        file_key = request.form['file_name']

        # Fetch data from the lecturer database
        cursor = db_conn.cursor()
        select_sql = "SELECT l.lectID \
                      FROM students s\
                      JOIN lecturer l on s.ucSuperEmail = l.lectEmail \
                      WHERE studentID = %s"
        cursor.execute(select_sql, (studID,))
        data = cursor.fetchone()  # Fetch a single row

        lecturerID = data[0]

        stud_file_key = 'Student/' + studID + "/" + "report/" + file_key
        lect_file_key = 'Lecturer/' + lecturerID + "/" + studID + "/" + file_key

        # Delete the file from S3
        try:
            s3 = boto3.client('s3')
            s3.delete_object(Bucket=custombucket, Key=stud_file_key)
            s3.delete_object(Bucket=custombucket, Key=lect_file_key)

            # Uplaod image file in S3
            s3 = boto3.resource('s3')

            folder_name = 'Student/' + studID + "/" + "report/"

            bucket = s3.Bucket(custombucket)
            list_of_files = list_files(bucket, folder_name)

            # Sort the list by last modified timestamp in descending order
            list_of_files.sort(key=lambda x: x['last_modified'], reverse=True)

            return render_template('report.html', my_bucket=bucket, studentID=studID, list_of_files=list_of_files)
        except Exception as e:
            return str(e)

# -------------------------------------------------------------- Student End --------------------------------------------------------------#


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
            # Go to the dashboard after successful registration
            return redirect(url_for('login'))
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
    return render_template('lectDashboard.html', student_data=student_data)

# ------------------------------------------------------------------- Lecturer END -------------------------------------------------------------------#

# ------------------------------------------------------------------- Company START (Wong Kar Yan) -------------------------------------------------------------------#

@app.route("/companyRegister", methods=['GET', 'POST'])
def companyRegister():
    if request.method == 'POST':
        compName = request.form['compName']
        compEmail = request.form['compEmail']
        comPassword = request.form['comPassword']
        companyImage = request.files['companyImage']
        
        # Uplaod image file in S3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(custombucket)
        compProfile = "https://" + bucket.name + ".s3.amazonaws.com/" + "company-" + compName + "_image_file"
        
        # Fetch data from the database here
        cursor = db_conn.cursor()
        select_sql = "SELECT max(compID) FROM company"
        cursor.execute(select_sql)
        data = cursor.fetchone()  # Fetch a single row
        data = str(data[0])

        if data == None:
            compID = 'C' + str(10001)
        else:
            comp_no = int(data[1:]) + 1
            compID = 'C' + str(comp_no)

        # Check if the email is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM company WHERE compEmail=%s", (compEmail))
        results = cursor.fetchall()
        cursor.close()

        # If the email is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('compRegister.html', email_error="This company email is already in use.")
        
        if companyImage.filename == "":
            return "Please select a file"
        
        insert_sql = "INSERT INTO company VALUES (%s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        
        try:
            cursor.execute(insert_sql, (compID,
                                        compName, 
                                        compEmail,
                                        comPassword,
                                        'pending',
                                        compProfile
                                        ))
            db_conn.commit()
            cursor.close()

             # Uplaod image file in S3 #
            comp_image_file_name_in_s3 = "company-" + str(compName) + "_image_file"
        
            try:
                print("Data inserted in MySQL RDS... uploading image to S3...")
                s3.Bucket(custombucket).put_object(Key=comp_image_file_name_in_s3, Body=companyImage)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3%7B0%7D.amazonaws.com/%7B1%7D/%7B2%7D".format(
                    s3_location,
                    custombucket,
                    comp_image_file_name_in_s3)
                return redirect(url_for('login'))  # Go to the dashboard after successful registration
            except Exception as e:
                cursor.close()
                print(f"Error during database insertion: {e}")
                return str(e)  # Handle any database errors here
                
        finally:
            cursor.close()
            
    return render_template('companyRegister.html')

@app.route("/jobReg", methods=['GET', 'POST'])
def jobReg():
    if request.method == 'POST':
        # comp_name = request.form['comp_name']
        job_title = request.form['job_title']
        job_desc = request.form['job_desc']
        job_req = request.form['job_req']
        sal_range = request.form['sal_range']
        contact_person_name = request.form['contact_person_name']
        contact_person_email = request.form['contact_person_email']
        contact_number = request.form['contact_number']
        comp_state = request.form['comp_state']
        compID = session.get('compID', None)
        print(compID)

        # Fetch data from the database here
        cursor = db_conn.cursor()
        select_sql = "SELECT max(job_id) FROM company"
        cursor.execute(select_sql)
        data = cursor.fetchone()  # Fetch a single row
        data = str(data[0])

        if data == None:
            job_id = 'C' + str(10001)
        else:
            comp_no = int(data[1:]) + 1
            job_id = 'C' + str(comp_no)

        insert_sql = "INSERT INTO jobApply VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        cursor.execute(insert_sql, (job_id, compID, job_title, job_desc, job_req, sal_range, contact_person_name, contact_person_email, contact_number, comp_state))
        db_conn.commit()
        cursor.close()

    return render_template('jobReg.html')


@app.route("/companyDashboard", methods=['GET'])
def companyDashboard():

    name = session.get('user_login_name', None)
    compID = session.get('compID', None)

    # Fetch job data from the database (assuming you have a SQL query for this)
    select_sql = "SELECT * FROM jobApply J JOIN company C ON C.compID = J.compID WHERE C.compID = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql, (compID,))
    job_data = cursor.fetchall()
    cursor.close()

    return render_template('companyDashboard.html', user_login_name=name, job_data=job_data)

def list_files(bucket, path_name):

    contents = []

    for image in bucket.objects.filter(Prefix=path_name):
        contents.append("https://wky-company.s3.amazonaws.com/" + image.key)
    return contents

@app.route('/jobDetail/<string:user_login_name>/<string:job_name>', methods=['GET'])
def jobDetail(user_login_name, job_name):
    
     # URL-decode the job_name to get the original string
    decoded_job_name = unquote_plus(job_name)

    # Fetch job details from the database using job_id
    cursor = db_conn.cursor()
    select_sql = "SELECT * FROM jobApply J JOIN company C ON C.compID = J.compID WHERE C.compName = %s AND J.job_title = %s"
    cursor.execute(select_sql, (user_login_name, decoded_job_name,))
    job_data = cursor.fetchall()
    cursor.close()
    session['job_data'] = job_data

    # Assuming job_data is a list of rows fetched from the database
    job_data_with_description = []

    for row in job_data:
        # Assuming job_desc is in the third column (index 2)
        job_desc = row[3]
        description_points = job_desc.split('-')

        # Assuming job_req is in a different column (index X)
        job_req = row[4]  # Replace X with the appropriate index of job_req
        req_points = job_req.split('-')

        # Update the row with the split description and requirement points
        row_with_description = list(row)
        row_with_description[3] = description_points  # Assuming job_desc is in the third column (index 2)
        row_with_description[4] = req_points  # Replace X with the appropriate index of job_req
        
        # Append the updated row to the new list
        job_data_with_description.append(tuple(row_with_description))

    #here code for print the image 
    # Build the object key and URL
    comp_image_file_name_in_s3 = f"company-{urllib.parse.quote_plus(user_login_name)}_image_file"
   
    # Uplaod image file in S3
    s3 = boto3.resource('s3')

    bucket = s3.Bucket(custombucket)
    list_of_files = list_files(bucket, comp_image_file_name_in_s3)

    # Render the job details template and pass the job_data, job_name, and user_login_name
    return render_template('jobDetails.html', job_data=job_data_with_description, list_of_files=list_of_files)


@app.route('/edit/<string:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):

    if request.method == 'POST':
        
        column = request.form.get('column') 
        updated_value = request.form.get('updated_value')   

        if column == 'job_title':

            update_sql = "UPDATE jobApply SET job_title = %s WHERE job_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (updated_value, job_id,))
            db_conn.commit()
            cursor.close()
        elif column == 'job_desc':

            update_sql = "UPDATE jobApply SET job_desc = %s WHERE job_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (updated_value, job_id,))
            db_conn.commit()
            cursor.close()
        elif column == 'job_req':

            update_sql = "UPDATE jobApply SET job_req = %s WHERE job_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (updated_value, job_id,))
            db_conn.commit()
            cursor.close()
        elif column == 'sal_range':

            update_sql = "UPDATE jobApply SET sal_range = %s WHERE job_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (updated_value, job_id,))
            db_conn.commit()
            cursor.close()
        elif column == 'contact_person_name':

            update_sql = "UPDATE jobApply SET contact_person_name = %s WHERE job_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (updated_value, job_id,))
            db_conn.commit()
            cursor.close()
        elif column == 'contact_person_email':

            update_sql = "UPDATE jobApply SET contact_person_email = %s WHERE job_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (updated_value, job_id,))
            db_conn.commit()
            cursor.close()
        elif column == 'contact_number':

            update_sql = "UPDATE jobApply SET contact_number = %s WHERE job_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (updated_value, job_id,))
            db_conn.commit()
            cursor.close()
        else:

            update_sql = "UPDATE jobApply SET comp_state = %s WHERE job_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (updated_value, job_id,))
            db_conn.commit()
            cursor.close()
        
    # Redirect to a confirmation page or back to the job details page
    return redirect(url_for('companyDashboard'))

@app.route('/delete_job/<string:job_id>', methods=['POST'])
def delete_job(job_id):
    
    delete_sql = "DELETE FROM jobApply WHERE job_id= %s"
    cursor = db_conn.cursor()
    cursor.execute(delete_sql, (job_id,))
    db_conn.commit()
    cursor.close()

    return redirect(url_for('companyDashboard'))
# ------------------------------------------------------------------- Company END -------------------------------------------------------------------#

# Define the route for admin registration


@app.route("/adminRegister", methods=['GET', 'POST'])
def adminRegister():
    if request.method == 'POST':
        adminName = request.form['adminName']
        adminEmail = request.form['adminEmail']
        adminContact = request.form['adminContact']
        password = request.form['password']

        # Fetch data from the database here
        cursor = db_conn.cursor()
        select_sql = "SELECT max(adminID) FROM admin"
        cursor.execute(select_sql)
        data = cursor.fetchone()  # Fetch a single row
        data = data[0]

        print(data)
        if data == None:
            adminID = 'A' + str(10001)
        else:
            admin_no = int(data[1:]) + 1
            adminID = 'A' + str(admin_no)

        insert_sql = "INSERT INTO admin VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(insert_sql, (adminID, adminName,
                           adminEmail, adminContact, password))
            db_conn.commit()
            cursor.close()
            # Redirect to admin login after successful registration
            return redirect(url_for('login'))
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here

    return render_template('adminRegister.html')


@app.route('/approve-company', methods=['POST'])
def approve_company():
    data = request.json  # Assuming you send JSON data with company_id

    # Extract company_id from the request
    company_id = data.get('company_id')

    if not company_id:
        return jsonify({"error": "Company ID is missing"}), 400

    try:
        with db_conn.cursor() as cursor:
            # Update the company's status to 'approved' in the database
            update_query = "UPDATE companies SET status = 'approved' WHERE id = %s"
            cursor.execute(update_query, (company_id,))
            db_conn.commit()

            return jsonify({"message": "Company approved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reject-company', methods=['POST'])
def reject_company():
    data = request.json  # Assuming you send JSON data with company_id

    # Extract company_id from the request
    company_id = data.get('company_id')

    if not company_id:
        return jsonify({"error": "Company ID is missing"}), 400

    try:
        with db_conn.cursor() as cursor:
            # Update the company's status to 'rejected' in the database
            update_query = "UPDATE companies SET status = 'rejected' WHERE id = %s"
            cursor.execute(update_query, (company_id,))
            db_conn.commit()

            return jsonify({"message": "Company rejected successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
