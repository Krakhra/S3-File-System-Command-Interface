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
stack.append("hrakhra")
stack.append("test1")
client = None

def parse_path(path):
  tokens = path.split('/')
  bucket = tokens[1]
  path_from_bucket = ""

  for i in range(2,len(tokens)):
    if(len(tokens[i]) > 0):
      path_from_bucket = path_from_bucket + tokens[i] + "/"
  obj = {
    "path": path_from_bucket,
    "bucket": bucket
  }
  return obj
    

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
    response = client.list_objects(Bucket="hrakhra",Prefix="test1/plswork/")
    for items in response['Contents']:
      print(items['Key'].rsplit('/',1))


  # bucket = s3.Bucket('hrakhra')
  # for items in bucket.objects.all():
  #   print(items)

def pwd():
  print(*stack, sep="/")

def cd(command):
  global stack
  if(command == "cd~"):
    stack = ["s3:"]

def upload(command):
  global stack
  s3_path = ""
  
  tokens = command.split(' ')
  if(len(tokens) == 1):
    print("Invalid arguments, expected file name")
    return
  #check if filename is correct
  if "." not in tokens[1]:
    print("Invalid file name(include extension and order: filename then s3 object name)")
    return 

  elif(len(tokens) == 2):
    #create path string
    if(len(stack) > 2):
      for i in range(2,len(stack)):
        s3_path = s3_path + stack[i] + "/"

    try:
      s3.Bucket(stack[1]).upload_file(tokens[1],s3_path+tokens[1])
    except ClientError as error:
      raise error
      return

    print("File Uploaded :))")

  else:
    #parse path
    path_toks = tokens[2].split('/')
    bucket = path_toks[0]
  
    if(len(path_toks) == 2):
      s3_path = path_toks[1] + "/"
    elif(len(path_toks) > 2):
      for i in range(1,len(path_toks)):
        if(len(path_toks[i]) > 0):
          s3_path = s3_path +path_toks[i]+ "/"

    try:
      s3.Bucket(bucket).upload_file(tokens[1],s3_path+tokens[1])
    except ClientError as error:
      raise error
      return
    print("File Uploaded :))")

def mkdir(command):
  global stack, client
  if(len(stack) == 1):
    print("No bucket found")
    return

  path = ""
  tokens = command.split(" ")
  if(len(tokens) != 2):
    print("invalid arguments: for mkdir: mkdir <directory name>")
    return
  name = tokens[1]
  
  for i in range(2,len(stack)):
    path = path + stack[i] + "/"

  try:
    client.put_object(Bucket = stack[1], Key=(path+name+"/"))
  except ClientError as error:
      raise error
      return

def rmdir(command):
  global stack
  path = ""

  if(len(stack) == 1):
    print("Cannot remove at bucket level")
    return
  
  tokens = command.split(" ")
  if(len(tokens) == 1):
    print("Invalid Argument")

  name = tokens[1]
  
  for i in range(2,len(stack)):
    path = path + stack[i] + "/"

  bucket = s3.Bucket(stack[1])
  bucket.objects.filter(Prefix=(path+name+"/")).delete()
  
def download(command):
  global stack

  tokens = command.split(' ')
  if(len(tokens) == 1 or len(tokens) > 3):
    print("Invalid Arguments")
    return

  name = ""
  path = ""
  bucket = ""
  
  if(len(tokens) == 3):
    path = tokens[1]
    name = tokens[2]
  else:
    name = tokens[1]
    for i in range(0,len(stack)):
      path = path + stack[i] + "/"
  
  parsed_obj = parse_path(path)
  print(parsed_obj)
  

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
    elif(command == "pwd"):
      pwd()
    elif(command[:2] == "cd"):
      cd(command)
    elif(command[:6] == "upload"):
      upload(command)
    elif(command[:5] == "mkdir"):
      mkdir(command)
    elif(command[:5] == "rmdir"):
      rmdir(command)
    elif(command[:8] == "download"):
      download(command)
    else:
       print(command)



run_shell()

