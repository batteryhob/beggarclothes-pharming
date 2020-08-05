import imaplib
import email
import re
import configparser
from unicodedata import normalize
from email.header import decode_header
from email.header import make_header

import pymysql

# Gmail 연결
def connect_to_gmail(username, password):
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    imap.login(username, password)
    imap.select("inbox")
    return imap


# 문자열의 인코딩 정보추출 후, 문자열, 인코딩 얻기
def findEncodingInfo(txt):
    infoobj = email.header.decode_header(txt)
    s, encoding = infoobj[0]
    if encoding is None:
        encoding = 'utf-8'
    return s, encoding


# Nas Insert
def write_to_rds(**kwargs):
    config = configparser.ConfigParser()
    config.read('config.ini')

    con = pymysql.connect(host=config['Nas']['HOST'], port=3307, user=config['Nas']['USER'], passwd=config['Nas']['PASSWORD'], db=config['Nas']['NAME'], charset='utf8')
    cur = con.cursor()
    cur.execute(
        query='''
            INSERT INTO `tbl_saleinfo`
            ( `from`, `subject`, `content`, `saleflag`, `view`, `like`, `regdate`)
            VALUES
            ( %(fromstore)s, %(subject)s, %(content)s, %(sale)s, 0, 0, NOW());
        ''',
        args=kwargs)
    cur.close()
    con.commit()
    con.close()


# Email 설정정보 불러오기
config = configparser.ConfigParser()
config.read('config.ini')


# 연결
imap = connect_to_gmail(config['Gmail']['ID'], config['Gmail']['Password'])
result, mails_data = imap.uid('search', 'SINCE 20-Jul-2020 X-GM-RAW "Category:Promotions"', "UNSEEN")

mails_ids = mails_data[0]
mails_id_list = mails_ids.split()

mail_count = 40
for i in reversed(mails_id_list):

    result, mail_data = imap.uid('fetch', i , '(RFC822)')    
    raw_email = mail_data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)

    fromstore = ''
    if type(decode_header(email_message['From'])[0][0]) is bytes:
        print('From: ', decode_header(email_message['From'])[0][0].decode("utf-8"))
        fromstore = decode_header(email_message['From'])[0][0].decode("utf-8")
    else:
        print('From: ', decode_header(email_message['From'])[0][0])
        fromstore = decode_header(email_message['From'])[0][0]
    
    # print('To: ', email_message['To'])
    print('Date: ', email_message['Date'])

    b, encode = findEncodingInfo(email_message['Subject'])

    subject = ''    
    try:
        print('SUBJECT:', str(b, encode))
        subject = str(b, encode)
    except TypeError:
        print('SUBJECT:', email_message['Subject'])
        subject = email_message['Subject']
    
    #세일체크
    sale = 0
    if "SALE" in  subject.upper():
        sale = 1
    elif "UP TO" in  subject.upper():
        sale = 1
    elif "%" in  subject.upper():
        sale = 1
    else:
        sale = 0

    #이메일 본문 내용 확인
    print('CONTENT START:')
    content = ''
    if email_message.is_multipart():
        for part in email_message.get_payload():        
            bytes = part.get_payload(decode = True)    
            encode = part.get_content_charset()        
            content += str(bytes, encode)
    print('CONTENT END:')

     #이메일 등록
    write_to_rds(
        fromstore=fromstore,
        subject=subject,
        content=content,
        sale=sale
    )

    mail_count -= 1
    if mail_count < 1:
        break

imap.close()
imap.logout()