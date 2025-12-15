from GetFile import get_file
from SendEmail import send_email_with_attachment
import os 
from dotenv import load_dotenv
import datetime


load_dotenv("/Users/juliacordero/Documents/Python/LogiwaScraping/.env")

print("file script started executing at ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

latest_file = get_file()

sender_email = os.getenv("SENDER_EMAIL")  # must be verified in Resend
receiver_email = "jcordero@the5411.com, holly.abdale@raw.group, melissa@bdadenim.com, gmiquelarena@estudiotripoli.com, avignoni@estudiotripoli.com"  # comma/semicolon separated OK
subject = "Inventory export"
body = "Please find the attached file with the latest inventory data."
file_path = latest_file

# SMTP args are ignored when RESEND_API_KEY is set
send_email_with_attachment(
    sender_email,
    receiver_email,
    subject,
    body,
    file_path,
    os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    os.getenv("SMTP_PORT", "587"),
    os.getenv("SENDER_EMAIL"),
    os.getenv("EMAIL_PASSWORD"),
)