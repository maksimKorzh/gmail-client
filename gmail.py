#############################################
#
#  Script to send & receive GMAIL mails
#           via SMTP with SSL
#
#############################################

# Packages
import os
import ssl
import email
import smtplib
import imaplib
from email import encoders
from getpass import getpass
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart

# Credentials
print('  -- LOGIN --\n')
EMAIL = input('Email: ')
PASSWORD = getpass('Password: ')

# Read email from 'Inbox'
def receive_mail(quantity):
  # Connect to the server and go to its inbox
  mail = imaplib.IMAP4_SSL('imap.gmail.com')
  mail.login(EMAIL, PASSWORD)
  mail.select('inbox')

  # Get list of EMAIL
  status, data = mail.search(None, 'ALL')

  # the list returned is a list of bytes separated
  mail_ids = []

  # Populate mail list
  for block in data: mail_ids += block.split()

  # Extract content
  try: quantity = int(quantity)
  except: quantity = len(mail_ids)
  for i in mail_ids[len(mail_ids)-quantity:len(mail_ids)]:
    status, data = mail.fetch(i, '(RFC822)')
    for response_part in data:
      if isinstance(response_part, tuple):
        message = email.message_from_bytes(response_part[1])
        sender = message['from']
        subject = message['subject']
        if message.is_multipart():
          content = ''
          for part in message.get_payload():
            if part.get_content_type() == 'text/plain':
              content += part.get_payload()
        else: 
          content = message.get_payload()

        # Print results
        print('From: ', sender)
        print('Subject: ', subject)
        print('Content:\n', content, sep='')

# Create message with attachment
def create_mail_attachment(recipient, subject, content, filename):
  # Create header
  mail = MIMEMultipart()
  mail['From'] = EMAIL
  mail['To'] = recipient
  mail['Subject'] = subject
  
  # Attach the mail body
  mail.attach(MIMEText(content, 'plain'))

  # Open the file in bynary
  with open(filename, 'rb') as attachment:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={filename}')
    mail.attach(part)

  # Return EMAIL object
  return mail

# Send message
def create_mail(recipient, subject, content):
  # Create header
  mail = EmailMessage()
  mail['From'] = EMAIL
  mail['To'] = recipient
  mail['Subject'] = subject

  # Attach mail to body
  mail.set_content(content)

  # Return EMAIL object
  return mail

# send message
def send(mail):
  # Create context
  context = ssl.create_default_context()

  # Login & send mail
  with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(EMAIL, PASSWORD)
    smtp.sendmail(mail['From'], mail['To'], mail.as_string())

# Write EMAIL on the fly
def write_mail():
  print('\nWrite EMAIL, enter empty line to stop:\n')
  lines = ""
  while True:
    line = input('> ')
    if line == '': break
    lines += line + '\n'
  return lines

# Read EMAIL from file
def read_mail(filename):
  content = ""
  with open(filename) as f:
    content = f.read()
  return content

# Main loop
while True:
  # Main menu
  print('\nGmail SMTP Client:\n')
  print(' 1. Send mail')
  print(' 2. Read mail')
  print(' 3. Exit\n')
  choice = input('Your choice: ')

  # Exit mail
  if choice == '3': break

  # Receive EMAIL
  elif choice == '2': receive_mail(input('How many emails to fetch? > '))

  # Write mail
  elif choice == '1':
    recipient = input('Recipient: ')
    subject = input('Subject: ')
    from_file = input('Read EMAIL from file? (y/n):')

    try: # try to add EMAIL body from file
      if from_file == 'y':
        filename = input('Filename: ')
        content = read_mail(filename)
      else: content = write_mail()
    except: # write EMAIL manually on failure
      print('Failed reading from file "' + filename + '"')
      content = write_mail()

    attach = input('Attach file? (y/n)')

    try: # try to attach file
      if attach == 'y':
        filename = input('Filename: ')
        mail = create_mail_attachment(recipient, subject, content, filename)
      else: mail = create_mail(recipient, subject, content)
    except: # do not attach anything on failure
      filename = 'N/A'
      mail = create_mail(recipient, subject, content)

    print('\nYou are about to send an EMAIL\n')
    print('To: ', recipient)
    print('Subject: ', subject)
    print('Email:\n', content, sep='')
    print('Attachment: ', filename if attach == 'y' else 'N/A')
    confirm = input('\nSend EMAIL? (y/n):')

    if confirm == 'y':
      try:
        send(mail)
        print('Mail sent successfully!')
      except: print('Failed to send mail!')
    else:
      continue