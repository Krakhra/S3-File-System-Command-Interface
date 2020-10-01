import boto3
from botocore.config import Config
from configparser import ConfigParser
from botocore.exceptions import ClientError

key = ""
secret_key = ""
client = ""
region = ""
session = None
session_tok = ""
s3 = None

def login():
  global key, secret_key, client, region, session, session_tok, s3
  config = ConfigParser()
  config.read('config.ini')
  # print(config['DEFAULT']['AccessKey'])
  key = config['DEFAULT']['AccessKey']
  secret_key = config['DEFAULT']['SecretKey']
  region = config['DEFAULT']['Region']
  session_tok = config['DEFAULT']['aws_session_token']
  
  try:
    session = boto3.Session(
      aws_access_key_id=key,
      aws_secret_access_key=secret_key,
      aws_session_token=session_tok
    )
  except ClientError as error:
    raise error
  
  print("Creating Session....")

  try:
    s3 = session.resource('s3')
  except ClientError as error:
    raise error
  
def mkbucket():
  scan = input("$ Enter name for Bucket: ")
  print("Creating Bucket....")
  try:
    bucket = s3.create_bucket(
      Bucket = scan,
    )
  except ClientError as error:
    raise error
  

def run_shell():
  while True:
    command = input("$ ")
    if command == "exit":
      break
    elif(command == "login"):
      login()
    elif(command == "mkbucket"):
      mkbucket()
    else:
       print(command)


run_shell()

