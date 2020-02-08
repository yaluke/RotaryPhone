#!/usr/bin/env python3

"""
Module responsible for decoding sms in PDU format and forwarding it to e-mail address
"""

import logging
import smspdu.easy
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def forward_sms(sms, email_account, email_passwd, email_to):
    logger = logging.getLogger(__name__)
    logger.info('Decoding and forwarding SMS')
    res = smspdu.easy.easy_sms(sms)
    logger.info(f"SMS details: sender: {res['sender']}, date: {res['date']}, content: {res['content']}"
                f", partial: {res['partial']}")

    message = MIMEMultipart("alternative")
    message["Subject"] = "New SMS received on 48608394953"
    message["From"] = email_account
    message["To"] = email_to
    message.attach(MIMEText(f"From: {res['sender']}\nDate: {res['date']}\n\n{res['content']}","plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(email_account, email_passwd)
        server.sendmail(email_account, email_to, message.as_string())
        # server.sendmail(email_account, email_to, f"Subject: New SMS received on 48608394953\n\nFrom: {res['sender']}\nDate: {res['date']}\n\n{res['content']}")

if __name__ == '__main__':
    logging.basicConfig(filename="smsforwarder.log", style='{',
                        format="{asctime} : {levelname:8} : {name:11} : {message}"
                        , level=logging.DEBUG)
    # sms1 = 'ABCD'
    sms1 = ('07918406026030F1040B911032546576F00000021071918322400441E19008')
    sms2 = ('07918406026030F14006D0CDE61400F502107191142340820B05040B8423F000031A02010006291F226170706C69636174696F6E2F'
            '766E642E7761702E6D6D732D6D657373616765008184AF848D01008C82983174696434383630383339343935335F30377967673834'
            '627068008D918918802B34383537323239323733362F545950453D504C4D4E00966E6F207375626A656374008A808E03')
    sms3 = ('07918406026030F14406D0CDE61400F5021071911423405D0B05040B8423F000031A020203067188048102A8BE83687474703A2F2F'
            '31302E37342E3138332E35352F6D6D732F776170656E633F6C6F636174696F6E3D34383630383339343935335F3037796767383462'
            '7068267269643D31333700')
    # sms2 & sms3 are two parts of mms (image)
    forward_sms(sms1)
    forward_sms(sms2)
    forward_sms(sms3)