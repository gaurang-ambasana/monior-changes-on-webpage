import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from apiclient import errors, discovery


def get_credentials():

    home_dir = os.path.expanduser('~')

    credential_dir = os.path.join(home_dir, '.credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    credential_path = os.path.join(credential_dir, 'creds.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        CLIENT_SECRET_FILE = 'credentials.json'
        APPLICATION_NAME = 'Gmail API Python Send Email'

        SCOPES = 'https://www.googleapis.com/auth/gmail.send'

        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME

        credentials = tools.run_flow(flow, store)

    return credentials


def create_message_and_send(sender, to, subject,  message_text_plain, message_text_html):
    credentials = get_credentials()

    http = httplib2.Http()

    http = credentials.authorize(http)

    service = discovery.build('gmail', 'v1', http=http)

    message_without_attachment = create_message_without_attachment(
        sender, to, subject, message_text_html, message_text_plain)

    send_message_without_attachment(
        service, "me", message_without_attachment, message_text_plain)


def create_message_without_attachment(sender, to, subject, message_text_html, message_text_plain):
    message = MIMEMultipart('alternative')

    message['Subject'] = subject
    message['From'] = sender
    message['To'] = to

    message.attach(MIMEText(message_text_plain, 'plain'))
    message.attach(MIMEText(message_text_html, 'html'))

    raw_message_no_attachment = base64.urlsafe_b64encode(message.as_bytes())
    raw_message_no_attachment = raw_message_no_attachment.decode()
    body = {'raw': raw_message_no_attachment}

    return body


def create_message_with_attachment(sender, to, subject, message_text_plain, message_text_html, attached_file):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    message.attach(MIMEText(message_text_html, 'html'))
    message.attach(MIMEText(message_text_plain, 'plain'))

    my_mimetype, encoding = mimetypes.guess_type(attached_file)

    if my_mimetype is None or encoding is not None:
        my_mimetype = 'application/octet-stream'

    main_type, sub_type = my_mimetype.split('/', 1)

    if main_type == 'text':
        print("text")

        temp = open(attached_file, 'r')
        attachment = MIMEText(temp.read(), _subtype=sub_type)

        temp.close()

    elif main_type == 'image':
        print("image")

        temp = open(attached_file, 'rb')
        attachment = MIMEImage(temp.read(), _subtype=sub_type)

        temp.close()

    elif main_type == 'audio':
        print("audio")

        temp = open(attached_file, 'rb')
        attachment = MIMEAudio(temp.read(), _subtype=sub_type)

        temp.close()

    elif main_type == 'application' and sub_type == 'pdf':
        temp = open(attached_file, 'rb')
        attachment = MIMEApplication(temp.read(), _subtype=sub_type)

        temp.close()

    else:
        attachment = MIMEBase(main_type, sub_type)

        temp = open(attached_file, 'rb')
        attachment.set_payload(temp.read())

        temp.close()

    filename = os.path.basename(attached_file)
    attachment.add_header('Content-Disposition',
                          'attachment', filename=filename)
    message.attach(attachment)

    message_as_bytes = message.as_bytes()
    message_as_base64 = base64.urlsafe_b64encode(message_as_bytes)

    raw = message_as_base64.decode()

    return {'raw': raw}


def send_message_without_attachment(service, user_id, body, message_text_plain):
    try:
        message_sent = (service.users().messages().send(
            userId=user_id, body=body).execute())
        message_id = message_sent['id']

        print(
            f'Message sent (without attachment) \n\n Message Id: {message_id}\n\n Message:\n\n {message_text_plain}')

    except errors.HttpError as error:
        print(f'An error occurred: {error}')


def send_message_with_attachment(service, user_id, message_with_attachment):
    try:
        message_sent = (service.users().messages().send(
            userId=user_id, body=message_with_attachment).execute())
        message_id = message_sent['id']
        return message_id

    except errors.HttpError as error:
        print(f'An error occurred: {error}')


def main_send_email(sender, to, subject, message_text_html, attached_file=''):
    message_text_plain = "HTML Not Supported!"

    if attached_file != '':
        credentials = get_credentials()

        http = httplib2.Http()
        http = credentials.authorize(http)

        service = discovery.build('gmail', 'v1', http=http)

        msg_with_attachment = create_message_with_attachment(
            sender, to, subject, message_text_plain, message_text_html, attached_file)

        send_message_with_attachment(service, "me", msg_with_attachment)
    else:
        create_message_and_send(sender, to, subject,
                                message_text_plain, message_text_html)
