import imaplib
import email
import re
import configparser
from unicodedata import normalize
from email.header import decode_header
from email.header import make_header
 

def connect_to_gmail(username, password):
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    imap.login(username, password)
    imap.select("inbox")
    return imap


def get_subject(email):
    h = decode_header(email.get('subject'))
    return unicode(make_header(h)).encode('utf-8')


# Email 설정정보 불러오기
config = configparser.ConfigParser()
config.read('config.ini')

# 연결
imap = connect_to_gmail(config['Gmail']['ID'], config['Gmail']['Password'])
result, mails_data = imap.search(None, "Category:Primary")

mails_ids = mails_data[0]
mails_id_list = mails_ids.split()

mail_count = 40
for i in reversed(mails_id_list):

    result, mail_data = imap.fetch(i, "(RFC822)")
    raw_email = mail_data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)
    print(email_message['Sender'])

    mail_count -= 1
    if mail_count < 1:
        break

imap.close()
imap.logout()
 
# # Email 설정정보 불러오기
# config = configparser.ConfigParser()
# config.read('config.ini')

# # 로그인

# session.login(config['Gmail']['ID'], config['Gmail']['Password'])
 
# # 받은편지함
# session.select('Inbox')
 
# # 받은 편지함 내 모든 메일 검색
# result, data = session.uid('search', 'SINCE 1-Jun-2020 X-GM-RAW "Category:Primary"')
 
# # result, data = session.uid('search', 'category:promotions')

# # 여러 메일 읽기
# all_email = data[0].split()
 
# for mail in all_email:
#     result, data = session.fetch(mail, '(RFC822)')
#     raw_email = data[0][1]
#     raw_email_string = raw_email.decode('utf-8')
#     email_message = email.message_from_string(raw_email_string)
    
#     # 메일 정보
#     # print('From: ', email_message['From'])
#     # print('Sender: ', email_message['Sender'])
#     # print('To: ', email_message['To'])
#     # print('Date: ', email_message['Date'])
 
#     # subject, encode = find_encoding_info(email_message['Subject'])
#     print('Subject', email_message['Subject'])
#     print('Sender: ', email_message['Sender'])

#     # message = ''
 
#     # print('[Message]')
#     # #메일 본문 확인
#     # if email_message.is_multipart():
#     #     for part in email_message.get_payload():
#     #         if part.get_content_type() == 'text/plain':
#     #             bytes = part.get_payload(decode=True)
#     #             encode = part.get_content_charset()
#     #             message = message + str(bytes, encode)
#     # else:
#     #     if email_message.get_content_type() == 'text/plain':
#     #         bytes = email_message.get_payload(decode=True)
#     #         encode = email_message.get_content_charset()
#     #         message = str(bytes, encode)
#     # print(message)
    
#     #첨부파일 존재 시 다운로드
#     # for part in email_message.walk():
#     #     if part.get_content_maintype() == 'multipart':
#     #         continue
#     #     if part.get('Content-Disposition') is None:
#     #         continue
#     #     file_name = part.get_filename()
 
#     #     if bool(file_name):
#     #         file_path = os.path.join('C:/downloads/', file_name)
#     #         if not os.path.isfile(file_path):
#     #             fp = open(file_path, 'wb')
#     #             fp.write(part.get_payload(decode=True))
#     #             fp.close()
#     # else:
#     #     continue
 
# session.close()
# session.logout()