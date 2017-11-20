#!/bin/python

###add doctor to csv file - doc_name,timeframe for appointment (days),search url where doctor is,number of doctor on page (subtract 1)

import re
import urlparse
import requests
import json
import datetime
import smtplib
import time
import sys

MAC_DOC_LIST = []
JOKER = "&&"

REQUEST_URL = "http://serguide.maccabi4u.co.il/webapi/api/SearchPage/GetSearchPageSearch/"
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"

GMAIL_USERNAME = ""
GMAIL_PASSWORD = ""
RECIPIENT = ""
SUBJECT = " - && Appointment"
EMAIL_BODY_1 = "&&'s next appointment is: "
EMAIL_BODY_2 = "Please click on the following link: "

def getPage(url, params):
        headers = {"User-Agent": USER_AGENT}
        payload = params.copy()
        payload.update({"PageNumber": "1",
                        #"RequestId":"79adaa26-ddae-fa04-fcf0-bb09d3e6b171","ChapterId":"001","IsKosher":"0","InitiatorCode":"001"}
                        "ChapterId":"001",
                        "IsKosher":"0",
                        "InitiatorCode":"001"
                        })
        r = requests.post(url, headers = headers, data = payload)
        d = json.loads(r.content)
        return d["Items"]

def sendGMAIL(doc_name, search_url, next_appointment):
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

def Main(filename):
        with (open(filename, "rb")) as doc_list_file:
                for line in doc_list_file:
                        list_line = line.split(",")
                        #print list_line
                        new_doc_dict = dict(doc_name=list_line[0], comparison_days=int(list_line[1]), search_url=list_line[2], search_result_num=int(list_line[3]))
                        MAC_DOC_LIST.append(new_doc_dict)

        print "#########################################"
        print "Starting Program, current datetime is: " + str(datetime.datetime.now())

        for doc in MAC_DOC_LIST:
                #printing doctor details from csv file
                #print "Doc items: " + str(doc.items())
                print "Doc Name: " + str(doc["doc_name"])
                comparison_datetime = datetime.datetime.now().date() + datetime.timedelta(days=doc["comparison_days"])
                print "Comparison Date: " + str(comparison_datetime)
                
                #preparing url
                params = urlparse.parse_qs(urlparse.urlparse(doc["search_url"]).query)
                #generating url POST request
                list_of_doctors = getPage(REQUEST_URL, params)
                
                #parsing next appointment date from results
                next_appointment_datetime = list_of_doctors[doc["search_result_num"]]["CLOSEST_APPOINMENT_DATE"]
                if ("" == next_appointment_datetime):
                        print "ERROR: Date not found."
                        continue
                next_appointment = datetime.datetime.strptime(next_appointment_datetime[:19], "%Y-%m-%dT%H:%M:%S").date()
                
                print EMAIL_BODY_1.replace(JOKER, doc["doc_name"]) + str(next_appointment.isoformat()) #prints date in dd-mm-yyyy format
                #comparing next appointment date to requested timeframe
                if (next_appointment < comparison_datetime): #if available appointment is earlier
                        print "Found appointment on: " + str(next_appointment.isoformat())
                        print "Sending Mail..."
                        sendGMAIL(doc["doc_name"], doc["search_url"], str(next_appointment.isoformat()))
                        print "Mail Sent."
                else:
                        #print "Next appointment only on: " + str(next_appointment.isoformat())
                        print "Not sending mail."
                time.sleep(2)

        print "#########################################"

if __name__ == "__main__":
        if len(sys.argv) == 1:
                print "Need CSV file as argument"
        else:
                Main(sys.argv[1])
