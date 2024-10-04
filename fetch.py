import imaplib
import email, email.utils
import ssl
import time
from xoauth2 import RefreshToken
from xoauth2 import GenerateOAuth2String

username = 'placeholder'
refresh = 'placeholder'
client_id = 'placeholder'
client_secret = 'placeholder'
token = RefreshToken(client_id, client_secret, refresh)['access_token']

# helper function to get either string or int input
def get_input(options = []):
  while True:
    user_input = input()
    if options.__len__() == 0:
      try:
        user_input = int(user_input)
        return user_input
      except:
        print('Invalid input')
        continue
    else:
      if user_input in options:
        return user_input
      else:
        print('Invalid input')
        continue

# connect to imap and authenticate using OAuth2
def connect():
  imap_conn = imaplib.IMAP4_SSL('imap.gmail.com', ssl_context=ssl.create_default_context())
  imap_conn.debug = 4
  imap_conn.authenticate('XOAUTH2', lambda x: GenerateOAuth2String(username=username, access_token=token, base64_encode=False))
  inbox = imap_conn.select('INBOX', readonly=True)
  amt = int(inbox[1][0])
  return imap_conn, amt

# clean emails either until certain amount checked, or checked email is older than given date
def clean(end_index = 10000, end_date = 0):
  
  # get total number of emails in inbox
  imap_conn, amt = connect()

  # needs fixing - create subscriptions label if not existing
  typ, data = imap_conn.list()
  if 'Subscriptions' not in data:
    imap_conn.create('Subscriptions')

  checked = []
  spam = []

  # loop through and check emails until given index or date reached
  for i in range(amt, amt - end_index, -1):
    if i < 1:
      break
    uid = str(i)

    # read message without marking as read
    imap_conn.select('Inbox', readonly=True)
    res, msg = imap_conn.fetch(uid, '(RFC822)')
    imap_conn.select('Inbox', readonly=False)

    if msg.__len__() > 1:
      # decode message
      response = msg[0]
      message = email.message_from_bytes(response[1])

      # check if end date reached
      if end_date != 0:
        date = message['Date']
        date = email.utils.parsedate_to_datetime(date)
        if date <= end_date:
          break
      
      # create output - remove?
      output = message['From'] + ' ' + message['Subject']
      subject = message['Subject']

      # decode message
      try:
        body = str(message.get_payload(0).get_payload(decode=True))
      except:
        body = str(response[1])

      # check if email is from a subscription
      if ('Unsubscribe' in body or 'unsubscribe' in body) and 'Important' not in subject and 'important' not in subject and 'IMPORTANT' not in subject:
        spam.append(uid)
      
      #output - remove?
      checked.append(output)

  # move emails marked as subscriptions to folder
  for uid in spam:
    imap_conn.store(uid, '+X-GM-LABELS', '(Subscriptions)')
    imap_conn.store(uid,'+FLAGS', '\\Deleted')

  # output - remove?
  for i in checked:
    print(i)

print('Enter option number:\n1. Clean recieved emails\n2. Continuously clean incoming emails')
user_input = get_input(['1', '2'])
if user_input == '1':
  print('How many emails would you like to check (starting from most recent)')
  amt = get_input()
  clean(end_index=amt)
else:
  imap_conn, amt = connect()
  res, msg = imap_conn.fetch(str(amt), '(RFC822)')
  response = msg[0]
  message = email.message_from_bytes(response[1])
  date = message['Date']
  date = email.utils.parsedate_to_datetime(date)

  while(True):
    clean(end_date=date)
    print('\nSleeping for 5 minutes\n')
    time.sleep(300)

