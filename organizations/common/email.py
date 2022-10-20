import smtplib
from email.message import EmailMessage
from django.conf import settings


def send_an_email(receiver_email, message):

    try:
        smtp_gmail = settings.SMTP["EMAIL_HOST"]["SMTP_GMAIL"]
        smtp_port = settings.SMTP["EMAIL_PORT"]
        login_user = settings.LOGIN_USER
        login_pw = settings.LOGIN_PW

        # Create your SMTP session

        smtp = smtplib.SMTP(smtp_gmail, smtp_port)
        # Use TLS to add security
        smtp.starttls()
        # User Authentication
        smtp.login(login_user, login_pw)
        # Defining The Message
        # message = "Welcome to Turf"

        # Sending the Email
        smtp.sendmail(login_user, receiver_email, message)

        # Terminating the session
        smtp.quit()
        print("Email sent successfully!")

    except Exception as e:
        print("Something went wrong....", e)
