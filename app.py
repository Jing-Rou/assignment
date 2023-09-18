from flask import Flask, render_template, request, redirect, url_for
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

@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html')

@app.route("/register2", methods=['GET'])
def register2():
    return render_template('register2.html')

# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         stud_email = request.form['email']
#         password = request.form['password']

#         insert_sql = "INSERT INTO students VALUES (%s, %s)"
#         cursor = db_conn.cursor()
        
#         try:
#             cursor.execute(insert_sql, (stud_email, password))
#             db_conn.commit()
#             cursor.close()
#             return redirect(url_for('index'))  # Redirect to the homepage after successful registration
#         except Exception as e:
#             cursor.close()
#             return str(e)  # Handle any database errors here
    
#     return render_template('register.html')

@app.route("/login", methods=['GET'])
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)