import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def sent_otp(email,otp_sented):
    # Email configuration
    sender_email = 'legalexecution.app@gmail.com'
    sender_password = 'cdvliiztutkrwooa' 
    receiver_email = email
    subject = 'OTP from LED APP'
    message_text = f'OTP is <{otp_sented}>'

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message_text, 'plain'))

    # Connect to the SMTP server (Gmail in this case)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print('Email sent successfully!')
        server.quit()
        return True

    except Exception as e:
        print('An error occurred:', str(e))
        server.quit()
        return False

    # finally:
    #     server.quit()





