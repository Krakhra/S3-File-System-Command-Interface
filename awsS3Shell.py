import boto3
from botocore.config import Config
from configparser import ConfigParser
from botocore.exceptions import ClientError
import os

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
client = None

def parse_cp(path):
  global stack
  tokens = path.split('/')
  file_name = ""
  new_path = ""
  bucket = ""

  if(len(tokens)==1):
    if(len(stack)== 1):
      print("Cannot Copy File From Outside Bucket")
      return
    if(tokens[0] == "."):
      file_name = ""
      bucket = stack[1]
      for i in range(2,len(stack)):
        new_path = new_path + stack[i] +"/"
    else:
      file_name = tokens[0]
      bucket = stack[1]
      for i in range(2,len(stack)):
        new_path = new_path + stack[i] +"/"
  else:
    if "s3:" not in tokens[0]:
      print("Not supplied with total path, example:(s3:/bucket123/folder1/)")
      return
    else:
      bucket = tokens[1]
      for i in range(2,len(tokens)):
        if("." in tokens[i]):
          file_name = tokens[i]
        else:
          if(len(tokens[i]) > 0):
            new_path = new_path + tokens[i] + "/"
  
  obj = {
    'bucket':bucket,
    'path':new_path,
    'file':file_name
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
  path = ""
  tokens = command.split(' ')
  found = False
  new_path = ""

  if(len(tokens) == 1):
    print("Invalid Arguments")
    return
  if(tokens[1] == "~"):
    stack = []
    stack.append("s3:")
  else:
    if(len(stack) == 1):
      for bucket in s3.buckets.all():
        if(bucket.name == tokens[1]):
          stack.append(bucket.name)
    else:
      for i in stack:
        path = path + i + "/"
      obj = parse_cp(path)
      response = client.list_objects_v2(
        Bucket=obj['bucket'],
      )

      if(len(stack) == 2):
        new_path = tokens[1]+"/"
      else:
        new_path = stack[len(stack)-1] + "/" +tokens[1]
      for i in response['Contents']:
        if new_path in i['Key']:
          stack.append(tokens[1])
          break


def upload(command):
  global stack
  path = ""
  tokens = command.split(' ')

  if(len(tokens) == 3):
    if "s3:" not in tokens[2]:
      for i in stack:
        path = path + i + "/"
      path = path + tokens[2] #append the name of the file to upload (s3:/bucket/test/file.txt)
    else:
      path = tokens[2]
  else:
    print("Invalid Arguments")
    return
  
  obj = parse_cp(path)
  
  try:
    s3.meta.client.upload_file(tokens[1],obj['bucket'],obj['path']+tokens[1])
  except ClientError as error:
    raise error
    return

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
  path = ""
  tokens = command.split(' ')

  if(len(tokens) == 3):
    if "s3:" not in tokens[1]:
      for i in stack:
        path = path + i + "/"
      path = path + tokens[1] #append the name of the file to download (s3:/bucket/test/file.txt)
    else:
      path = tokens[1]
  else:
    print("Invalid Arguments")
    return
  
  obj = parse_cp(path)
  try:
    s3.Bucket(obj['bucket']).download_file(obj['path']+obj['file'], tokens[2])
  except ClientError as e:
      if e.response['Error']['Code'] == "404":
          print("The object does not exist.")
      else:
          raise

def cp(command):
  tokens = command.split(' ')
  path1=""
  path2=""
  file_name = 0 #1 means first arg contains file 2 mean second arg contains file

  if(len(tokens) == 1):
    print("Invalid Args")
  first = parse_cp(tokens[1])
  second = parse_cp(tokens[2])
  
  # print(first)
  # print(second)
  src = {
    'Bucket':first['bucket'],
    'Key':first['path'] +first['file']
  }
  bucket = s3.Bucket(second['bucket'])
  bucket.copy(src,second['path']+first['file'])
  
def mv(command):
  tokens = command.split(' ')
  first = parse_cp(tokens[1])
  second = parse_cp(tokens[2])

  print(first)
  print(second)

  src = {
    'Bucket':first['bucket'],
    'Key':first['path'] +first['file']
  }
  bucket = s3.Bucket(second['bucket'])
  bucket.copy(src,second['path']+first['file'])
  # delete src object
  src_obj = s3.Object(first['bucket'],first['path']+first['file'])
  src_obj.delete()

def rm(command):
  tokens = command.split(' ')
  if(len(tokens) != 2):
    print("Invalid Args")
    return

  obj = parse_cp(tokens[1])
  src_obj = s3.Object(obj['bucket'],obj['path']+obj['file'])
  src_obj.delete()
  
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
    elif(command[:2] == "cp"):
      cp(command)
    elif(command[:2] == "mv"):
      mv(command)
    elif(command[:2] == "rm"):
      rm(command)
    else:
       print(command)



run_shell()

