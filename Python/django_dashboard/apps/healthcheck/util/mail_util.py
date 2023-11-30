'''
Created on Mar 21, 2016

@author: zbasmajian
'''
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

def sendMail(sender, toaddrs, recipients, subject, message):
    mail_server = getattr(settings, "MAIL_SERVER")
    mail_port = getattr(settings, "MAIL_PORT")
    s = smtplib.SMTP(mail_server, mail_port)
    msg = MIMEMultipart('alternative')
    part1 = MIMEText(message, 'html')
    msg.attach(part1)
    msg['Subject'] = subject
    msg['From'] = sender
    toaddrs = removeInvalid(toaddrs)
    recipients = removeInvalid(recipients)
    if not toaddrs and not recipients:
        return
    if toaddrs:
        msg['To'] = ", ".join(toaddrs)
    if recipients:
        msg['Cc'] = ", ".join(recipients) 
   
    s.sendmail(sender, toaddrs, msg.as_string())
    s.quit()
def isEmailValid(emailAddress):
    if emailAddress:
        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
        return EMAIL_REGEX.match(emailAddress) != None
    else:
        return False
def removeInvalid(emailAddressList):   
    result = []
    for emailAddress in set(emailAddressList):
        if isEmailValid(emailAddress):
            result.append(emailAddress)
    return result  

