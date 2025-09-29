# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders
# import smtplib
# import os
# import time
# import datetime


# def send_email_with_attachment(sender_email, receiver_email, subject, body, file_path, smtp_server, smtp_port, login, password):
#     message = MIMEMultipart()
#     message['From'] = sender_email
#     message['To'] = receiver_email
#     message['Subject'] = subject

#     message.attach(MIMEText(body, 'plain'))

#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as attachment:
#             part = MIMEBase('application', 'octet-stream')
#             part.set_payload(attachment.read())
#         encoders.encode_base64(part)  
#         part.add_header(
#             'Content-Disposition',
#             f'attachment; filename={os.path.basename(file_path)}'
#         )
#         message.attach(part)
#     else:
#         print(f"File not found: {file_path}")
#         return

#     try:
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()  
#             server.login(login, password)
#             server.send_message(message)
#             print(f"Email sent successfully! at {datetime.datetime.now()}")
#     except Exception as e:
#         print(f"Failed to send email: {e} {datetime.datetime.now()}")



# SendEmail.py
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import time
import datetime
import mimetypes
import requests  # HTTPS email API
import smtplib
import ssl


def _as_recipient_list(receiver_email: str):
    parts = []
    for sep in [",", ";"]:
        receiver_email = receiver_email.replace(sep, " ")
    for p in receiver_email.split():
        if "@" in p:
            parts.append(p.strip())
    return parts or [receiver_email.strip()]


def _mime_for(path: str) -> str:
    mt, _ = mimetypes.guess_type(path)
    return mt or "application/octet-stream"


def _send_via_resend(sender_email: str, receiver_email: str, subject: str, body: str, file_path: str) -> bool:
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        print("[RESEND] RESEND_API_KEY not set; skipping Resend path.")
        return False

    recipients = _as_recipient_list(receiver_email)
    files = []
    if file_path and os.path.exists(file_path):
        files = [
            (
                "attachments",
                (os.path.basename(file_path), open(file_path, "rb"), _mime_for(file_path)),
            )
        ]
        print(f"[RESEND] Attachment prepared: {file_path}")
    else:
        print(f"[RESEND] File not found: {file_path}")
        return False

    data = {
        "from": sender_email,       # e.g. "Reports <reports@yourdomain.com>"
        "to": recipients,           # list of strings
        "subject": subject,
        "text": body,
    }

    # simple retries
    for attempt in range(1, 4):
        try:
            r = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}"},
                data=data,
                files=files,
                timeout=20,
            )
            if r.status_code >= 400:
                print(f"[RESEND] API error {r.status_code}: {r.text}")
                time.sleep(2 * attempt)
                continue
            print(f"[RESEND] Email sent OK at {datetime.datetime.now()}")
            return True
        except Exception as e:
            print(f"[RESEND] Attempt {attempt} failed: {e}")
            time.sleep(2 * attempt)

    print("[RESEND] Giving up after retries.")
    return False


def _send_via_smtp(sender_email, receiver_email, subject, body, file_path, smtp_server, smtp_port, login, password) -> bool:
    """
    Legacy SMTP path (kept for compatibility). This will still fail if your host blocks SMTP egress.
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        message.attach(part)
    else:
        print(f"[SMTP] File not found: {file_path}")
        return False

    try:
        port = int(smtp_port)
    except Exception:
        port = 587

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port, timeout=20) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()
            server.login(login, password)
            server.send_message(message)
        print(f"[SMTP] Email sent successfully! at {datetime.datetime.now()}")
        return True
    except Exception as e:
        print(f"[SMTP] Failed to send email: {e} {datetime.datetime.now()}")
        return False


def send_email_with_attachment(
    sender_email,
    receiver_email,
    subject,
    body,
    file_path,
    smtp_server,
    smtp_port,
    login,
    password,
):
    """
    Preferred path: Resend API (HTTPS, port 443). If RESEND_API_KEY is unset, falls back to SMTP.
    """
    if os.getenv("RESEND_API_KEY"):
        ok = _send_via_resend(sender_email, receiver_email, subject, body, file_path)
        if ok:
            return
        # If Resend failed for any reason, stop here (most common issue: unverified sender).
        return

    # Fallback if you deliberately want SMTP when API key is missing.
    _send_via_smtp(sender_email, receiver_email, subject, body, file_path, smtp_server, smtp_port, login, password)
