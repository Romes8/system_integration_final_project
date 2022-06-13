from email.quoprimime import body_check
from lib2to3.pgen2 import token
import os
import sys
import json
from tkinter import E
from xml.sax.handler import property_interning_dict
import jwt
from paste import httpserver
from bottle import Bottle, run, get, post, template, request, response, redirect, static_file, view
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import requests
from db import *
from credentials import *
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY="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"



# Define the application

@get('/')
@view('index')
def _():
    return 

@post('/validate_jwt')
def _():
    try:  
        token = json.load(request.body)

        jwt_decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
        if (len(jwt_decoded['cpr']) == 11):
            cpr = jwt_decoded['cpr']

            #save as cookie 
            response.set_cookie('cpr', cpr)

            auth_code = str(random.randint(100000, 999999))
            print(auth_code)
            save_code(auth_code, cpr)
            data = get_info(cpr)
        
            phone = data[0]
            email = data[1]
        
            #comment while developing - this works 
            # print("Before email function")
            send_email(auth_code, email)

            # print("Before SMS send")
            send_sms(auth_code, phone)

            response.status = 200
        else:
            print("CPR is invalid")
            response.status = 400
    except Exception as e:
        print(e)

@get("/validate_code")
@view("welcome")
def _():
    input_code = request.query.code
    print("User inserted code: ")
    print(input_code)
    auth_code = get_auth_code(request.get_cookie('cpr')) #take from DB 

    if (input_code == auth_code):
        print("Code is valid")
        response.status = 200
        #redirect to a new page
        return redirect("/esb")

@get('/esb')
@view('esb')
def _():
    mes_code = str(random.randint(100000, 999999))
    #load cookie 
    cpr = request.get_cookie('cpr')

    #delete cookie 
    response.delete_cookie('cpr')

    if save_mes_code(mes_code, cpr): 
        return dict(token=mes_code)
    else:
        return dict(token="BADLY GENERATED TOKEN, Try again")


def send_email(auth_code, email):
    #possible to store in env. 

    # password = "Romesdeveloper+"

    # message = MIMEMultipart("alternative")
    # message["Subject"] = "Verification code"
    # message["From"] = email
    # message["To"] = email

    # html = f"""\
    # <html>
    #     <body>
    #         <p>
    #             Hi, Thank you for reg istering at ZAQA .
    #             <br>
    #             <h3>Your verfication code is: {auth_code}</h3>
    #             <br>
    #         </p>
    #     </body>
    # </html>
    # """
    # part = MIMEText(html, "html")
            
    # message.attach(part)

    # context = ssl.create_default_context()
    # with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    #     try:
    #         server.login(email, password)
    #         server.sendmail(email, email, message.as_string())
    #         print("Email send successfully")
    #     except Exception as ex:
    #         print("Exception: ")
    #         print(ex)
    # return

    
    message = Mail(
        from_email=email,
        to_emails=email,
        subject='Verification code',
        html_content=f'Thank you for signing up at ZAQA! Your verification code is: {auth_code}')

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print("Email send successfully")
        return

    except Exception as e:
        print(os.environ.get('SENDGRID_API_KEY'))
        print("Error: {}".format(e))

def send_sms(auth_code, phone):
    API_ENDPOINT = "https://fatsms.com/send-sms"

    API_KEY = "15fcdb7b-1e3e-445d-bf1a-e8dd41aa3554"

    message = f"Hello {first_name} {last_name}, your verification code is {auth_code}."

    data = {
        "to_phone": phone,
        "message": message,
        "api_key": API_KEY,
    }

    r = requests.post(url = API_ENDPOINT, data=data)
    print(r.status_code)
    print(r.text)
    print("SMS send successfully")


run(host="127.0.0.1", port=4444, debug=True, reloader=True, server="paste")
