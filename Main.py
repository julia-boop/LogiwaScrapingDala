from GetFile import get_file
from SendEmail import send_email_with_attachment
import os 
from dotenv import load_dotenv
import datetime


load_dotenv("/Users/juliacordero/Documents/Python/LogiwaScraping/.env")

print("file script started executing at ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

latest_file = get_file()

sender_email = os.getenv("SENDER_EMAIL")
# receiver_email = "jcordero@the5411.com, holly.abdale@rawgroup.co, melissa@bdadenim.com, gmiquelarena@estudiotripoli.com, avignoni@estudiotripoli.com"
receiver_email = "jcordero@the5411.com"
subject = "Inventory export"
body = "Please find the attached file with the latest inventory data."
file_path = latest_file  
smtp_server = os.getenv("SMTP_SERVER") 
smtp_port = os.getenv("SMTP_PORT") 
login = os.getenv("SENDER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")

send_email_with_attachment(sender_email, receiver_email, subject, body, file_path, smtp_server, smtp_port, login, password)



