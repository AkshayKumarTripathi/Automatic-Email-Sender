from flask import Flask, render_template, request, flash, redirect
from werkzeug.utils import secure_filename
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

app = Flask(__name__)

PORT = 587 # FOR SSL
ALLOWED_EXTENSIONS = {'txt'}

@app.route('/home')
@app.route('/')
def home():
    return render_template('base.html')

@app.route('/uploader', methods = ["POST"])
def upload():
    if request.method == "POST":
        # check if post request has the file path
        if 'file' not in request.files:
            return render_template('base.html')

        user_details = request.files['file']

        #if empty file
        if user_details.filename == '':
            return render_template('base.html')
        if user_details and allowed_file(user_details.filename):
            filename = secure_filename(user_details.filename)
            user_details.save(os.path.join(filename))
            names , emails = get_contacts(filename)
            send_emails(names, emails, request.form['email'],request.form['password'])

        
        return render_template('base.html')


# Helper Functions

def get_contacts(filename):
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for contact in contacts_file:
            # Check if the length of contact is 2 i.e. first name and email
            if len(contact.split()) != 2:
                continue
            else:
                names.append(contact.split()[0])
                emails.append(contact.split()[1])
        return names, emails



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS        

def send_emails(names:list, emails:list, MY_ADDRESS:str, PASSWORD:str):
    temp_login = smtplib.SMTP(host='smtp.gmail.com', port=587 )
    temp_login.ehlo()
    temp_login.starttls()
    temp_login.ehlo()
    temp_login.login(MY_ADDRESS, PASSWORD)

    for name,email in zip(names,emails):
        msg = MIMEMultipart()

        # configuring Message
        message = f"Hello {name}! this is a test email"
        msg['From'] = MY_ADDRESS
        msg['To']= email
        msg['Subject'] = "THIS IS TEST"
        msg.attach(MIMEText(message,'plain'))

        temp_login.send_message(msg)

        del msg
    return render_template('base.html')

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run()