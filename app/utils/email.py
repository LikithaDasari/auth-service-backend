import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()


def send_email(to_email: str, subject: str, body: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    try:
        print("smtp_user", smtp_user, smtp_password)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        print(f"Mail sent successfully to {to_email}")
    except Exception as e:
        print("Mail error:", e)


def send_otp_email(to_email: str, otp: str):
    body = f"Your OTP is: {otp}\n\nThis OTP is valid for 5 minutes."
    send_email(to_email, "Verify your account", body)


def send_success_email(to_email: str):
    body = (
        "Congratulations!\n\n"
        "Your account has been successfully verified.\n\n"
        "You can now log in."
    )
    send_email(to_email, "Account Verified Successfully", body)

def send_password_change_email(to_email: str):
    body = (
        "Your account password has been changed.\n\nIf this wasn’t you, please reset your password immediately."
    )
    send_email(to_email, "Password changed Successfully", body)

def reset_password_email(to_email: str, otp: str):
    body = f"Your OTP is: {otp}\n\nThis OTP is valid for 5 minutes."
    send_email(to_email, "Reset Password", body)
