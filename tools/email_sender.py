import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def send_email(to , subject, body):
    gmail = os.getenv("GMAIL")
    password = os.getenv("GMAIL_APP_PASSWORD")

    msg = MIMEMultipart()
    msg["FROM"] = gmail
    msg["TO"] = to
    msg["SUBJECT"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server :
        server.starttls()
        server.login(gmail, password)
        server.sendmail(gmail, to, msg.as_string())
        print("EMAIL send successfully !")
        