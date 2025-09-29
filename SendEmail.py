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



from email.mime.base import MIMEBase  # kept only to avoid breaking imports elsewhere
import os
import time
import base64
import datetime
import mimetypes
import requests  # <— HTTPS API client


def _as_recipient_list(value: str):
    """Accept 'a@x.com, b@y.com; c@z.com' or single email and return a clean list."""
    if not value:
        return []
    for sep in [",", ";"]:
        value = value.replace(sep, " ")
    return [p.strip() for p in value.split() if "@" in p]


def _attachment_dict(path: str) -> dict:
    """Build Resend attachment dict with base64 content."""
    with open(path, "rb") as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode("ascii")
    # MIME type is optional for Resend; include if we can guess it
    mt, _ = mimetypes.guess_type(path)
    att = {"filename": os.path.basename(path), "content": b64}
    if mt:
        att["type"] = mt
    return att


def send_email_with_attachment(
    sender_email: str,
    receiver_email: str,
    subject: str,
    body: str,
    file_path: str,
    smtp_server: str,   # ignored for HTTPS API
    smtp_port,          # ignored for HTTPS API
    login: str,         # ignored for HTTPS API
    password: str,      # ignored for HTTPS API
) -> bool:
    """Send via Resend HTTPS API (port 443). Returns True on success."""
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        print("[RESEND] ERROR: RESEND_API_KEY is not set")
        return False

    if not sender_email:
        print("[RESEND] ERROR: SENDER_EMAIL not provided")
        return False

    recipients = _as_recipient_list(receiver_email)
    if not recipients:
        print("[RESEND] ERROR: receiver_email is empty/invalid")
        return False

    if not file_path or not os.path.exists(file_path):
        print(f"[RESEND] ERROR: attachment not found at {file_path}")
        return False

    payload = {
        "from": sender_email,                # must belong to a verified sender/domain in Resend
        "to": recipients,                    # list of strings
        "subject": subject or "",
        "text": body or "",
        "attachments": [_attachment_dict(file_path)],
    }

    # Optional: make replies go to your personal inbox
    reply_to = os.getenv("REPLY_TO_EMAIL")
    if reply_to:
        payload["reply_to"] = [reply_to]

    headers = {"Authorization": f"Bearer {api_key}"}

    # Simple retries with backoff
    for attempt in range(1, 4):
        try:
            r = requests.post(
                "https://api.resend.com/emails",
                json=payload,               # IMPORTANT: JSON, not multipart
                headers=headers,
                timeout=20,
            )
            if r.status_code < 300:
                print(f"[RESEND] Sent OK at {datetime.datetime.now()} id={r.json().get('id')}")
                return True
            else:
                print(f"[RESEND] API error {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[RESEND] Attempt {attempt} failed: {e}")

        if attempt < 3:
            time.sleep(2 * attempt)

    print("[RESEND] Giving up after retries.")
    return False