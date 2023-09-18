from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

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
table = 'student'

<<<<<<< HEAD
@app.route("/", methods=['GET'], endpoint='index')
=======
@app.route("/", methods=['GET', 'POST'], endpoint='index')
>>>>>>> 74a9e8bb43fb35c44e8b5db46b5e85f67ab246af
def home():
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

# @app.route("/about", methods=['POST'])
# def about():
#     return render_template('www.intellipaat.com')


# @app.route("/register", methods=['POST'])
# def AddEmp():
#     stud_email = request.form['email']
#     password = request.form['password']
#     # last_name = request.form['last_name']
#     # pri_skill = request.form['pri_skill']
#     # location = request.form['location']
#     # emp_image_file = request.files['emp_image_file']

#     insert_sql = "INSERT INTO student VALUES (%s, %s)"
#     cursor = db_conn.cursor()

#     # if emp_image_file.filename == "":
#     #     return "Please select a file"

#     try:

#         cursor.execute(insert_sql, (stud_email, password))
#         db_conn.commit()
#         # emp_name = "" + first_name + " " + last_name
#         # # Uplaod image file in S3 #
#         # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
#         s3 = boto3.resource('s3')

#         try:
#             print("Data inserted in MySQL RDS... uploading image to S3...")
#             # s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
#             bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
#             s3_location = (bucket_location['LocationConstraint'])

#             if s3_location is None:
#                 s3_location = ''
#             else:
#                 s3_location = '-' + s3_location

#             object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
#                 s3_location,
#                 custombucket)

#         except Exception as e:
#             return str(e)

#     finally:
#         cursor.close()

#     print("all modification done...")
#     return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

