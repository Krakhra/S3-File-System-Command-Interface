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
stack = []
stack.append("s3:")
stack.append("test1")
client = None

def login():
  global key, secret_key, client, region, session, session_tok, s3, client
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
  try:
    client = session.client('s3')
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
  
def ls():
  #case 1 only root buckets
  if(len(stack) == 1):
    for buckets in s3.buckets.all():
      print("-dir-\t" + buckets.name)
  else:
    result = client.list_objects(Bucket="hrakhra",Prefix="test1/plswork",Delimiter="/")
    for items in result.get('CommonPrefixes'):
      print('sub folder: ', items.get('Prefix'))

  # bucket = s3.Bucket('hrakhra')
  # for items in bucket.objects.all():
  #   print(items)

def run_shell():
  while True:
    command = input("$ ")
    if command == "exit":
      break
    elif(command == "login"):
      login()
    elif(command == "mkbucket"):
      mkbucket()
    elif(command == "ls" or command == "ls -l"):
      ls()
    else:
       print(command)


run_shell()

