from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import os
import time
import datetime


def send_email_with_attachment(sender_email, receiver_email, subject, body, file_path, smtp_server, smtp_port, login, password):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    if os.path.exists(file_path):
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)  
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={os.path.basename(file_path)}'
        )
        message.attach(part)
    else:
        print(f"File not found: {file_path}")
        return

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  
            server.login(login, password)
            server.send_message(message)
            print(f"Email sent successfully! at {datetime.datetime.now()}")
    except Exception as e:
        print(f"Failed to send email: {e} {datetime.datetime.now()}")



