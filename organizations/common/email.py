import smtplib
from email.message import EmailMessage
from django.conf import settings


# def send_an_email(receiver_email, message):
#     print("msg================", message)
#     try:
#         smtp_gmail = settings.SMTP["EMAIL_HOST"]["SMTP_GMAIL"]
#         smtp_port = settings.SMTP["EMAIL_PORT"]
#         login_user = settings.LOGIN_USER
#         login_pw = settings.LOGIN_PW

#         # Create your SMTP session

#         smtp = smtplib.SMTP(smtp_gmail, smtp_port)
#         # Use TLS to add security
#         smtp.starttls()
#         # User Authentication
#         smtp.login(login_user, login_pw)
#         # Defining The Message
#         # message = "Welcome to Turf"

#         # Sending the Email
#         smtp.sendmail(login_user, receiver_email, message)

#         # Terminating the session
#         smtp.quit()
#         print("Email sent successfully!")

#     except Exception as e:
#         print("Something went wrong....", e)


def send_an_email(receiver_email, message, sub):
    print(message)
    smtp_gmail = settings.SMTP["EMAIL_HOST"]["SMTP_GMAIL"]
    smtp_port = settings.SMTP["EMAIL_PORT"]
    login_user = settings.LOGIN_USER
    login_pw = settings.LOGIN_PW

    # gmail_user = "your_email@gmail.com"
    # gmail_password = "your_password"

    sent_from = login_user
    to = [receiver_email]
    subject = sub
    body = message
    # email_text = f"From : {sent_from}===>To : {to}===> Subject : {subject}: {body} "
    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (
        sent_from,
        ", ".join(to),
        subject,
        body,
    )

    try:
        smtp_server = smtplib.SMTP_SSL(smtp_gmail, 465)
        smtp_server.ehlo()
        smtp_server.login(login_user, login_pw)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong….", ex)
