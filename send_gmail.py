#!/bin/python

import json
import smtplib

email_data_file = './email_daa.json'
sender_data_file = './sender_mail_config.json'

def sendGMAIL(doctor_name, search_url, next_appointment):
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.ehlo()
        session.starttls()
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        headers = "\r\n".join(["from: " + GMAIL_USERNAME,
                       "subject: " + next_appointment + SUBJECT.replace(JOKER, doc_name),
                       "to: " + RECIPIENT,
                       "mime-version: 1.0",
                       "content-type: text/html"])
        content = headers + "\r\n\r\n" + EMAIL_BODY_1.replace(JOKER, doc_name) + next_appointment + "." + "\r\n\r\n" + EMAIL_BODY_2 + search_url
        session.sendmail(GMAIL_USERNAME, RECIPIENT, content)
