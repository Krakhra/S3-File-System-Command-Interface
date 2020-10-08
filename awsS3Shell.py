# Imports
import boto3
from botocore.config import Config
from configparser import ConfigParser
from botocore.exceptions import ClientError
import os

# Globals
key = ""
secret_key = ""
client = ""
region = ""
session = None
session_tok = ""
s3 = None
stack = []
stack.append("s3:")
client = None

# Function for parsing paths and returning objects with bucket, path, filename
def parse_cp(path):
  # Var declarations
  global stack
  tokens = path.split('/')
  file_name = ""
  new_path = ""
  bucket = ""
  
  # if path is just s3 
  if(len(tokens)==1):
    if(len(stack)== 1):
      print("Unexpected Error")
      return
    # if theres a file, make path current path
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
  # create return object
  obj = {
    'bucket':bucket,
    'path':new_path,
    'file':file_name
  }
  return obj

# Function for logging into session
def login(cmd):
  global key, secret_key, client, region, session, session_tok, s3, client
  is_user = False
  user = ""
  # If username is supplied, parse command
  if(" " in cmd):
    is_user = True
    tokens = cmd.split(" ")
    if(len(tokens) != 2):
      print("Invalid Arguments")
      return
    user = tokens[1]
  
  config = ConfigParser()
  config.read('config.ini')
  # Parse config file
  if(is_user == False):
    key = config['DEFAULT']['AccessKey']
    secret_key = config['DEFAULT']['SecretKey']
    region = config['DEFAULT']['Region']
    session_tok = config['DEFAULT']['aws_session_token']
  else:
    key = config[user]['AccessKey']
    secret_key = config[user]['SecretKey']
    region = config[user]['Region']
  
  # For development if not supplied with session token then create normal session
  if(len(session_tok) == 0):
    try:
      session = boto3.Session(
        aws_access_key_id=key,
        aws_secret_access_key=secret_key,
        region_name=region
      )
    except ClientError as error:
      print(error)
      return
  # If supplied with session tokens then create temp session
  else:
    try:
      session = boto3.Session(
        aws_access_key_id=key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_tok,
        region_name=region
      )
    except ClientError as error:
      print(error)
      return

  try:
    s3 = session.resource('s3')
  except ClientError as error:
    print(error)
  try:
    client = session.client('s3')
  except ClientError as error:
    print(error)
  
# Function for creating bucket at root level
def mkbucket(cmd):
  toks = cmd.split(" ")
  if(len(toks) != 2):
    print("Invalid Number of Arguments")
    return
  if(len(toks[1]) == 0):
    print("Invalid bucket name")
    return
  
  if s3.Bucket(toks[1]) in s3.buckets.all():
    print("Bucket Already Exists")
    return
  try:
    bucket = s3.create_bucket(
      Bucket = toks[1],
    )
  except ClientError as error:
    print(error)
  
def ls(command):
  path = ""
  contains={}
  is_long_form = False

  if("-l" in command):
    is_long_form = True

  #case 1 only root buckets
  if(len(stack) == 1):
    for buckets in s3.buckets.all():
      print("-dir-\t" + buckets.name)
  else:
    for i in stack:
      path = path + i + "/"
    obj = parse_cp(path)
    response = client.list_objects(Bucket=obj['bucket'],Prefix=obj['path'],Delimiter=obj['path'])

    duplicates = []
    # Parsing response from list objects to be printed in normal or long form
    if('Contents' in response):
      for items in response['Contents']:
        # Inside bucket 1 level
        if(len(stack) == 2):
          item_tok = items['Key'].split("/")
          if item_tok[0] not in duplicates:
            duplicates.append(item_tok[0])
            if("." in item_tok[0]):
              print("\t"+item_tok[0])
            else:
              print("-dir-\t" + item_tok[0])
        else:
          current_folder = stack[len(stack)-1] + "/"
          item_tok = items['Key'].split(current_folder)
          first_level = item_tok[1].split("/")
          if first_level[0] not in duplicates:  
            duplicates.append(first_level[0])
            # if object is a file
            if("." in first_level[0]):
              if(is_long_form == True):
                file_extension_tok = first_level[0].split(".")
                print(file_extension_tok[1] + "\t" + str(items['Size']) + "\t" + str(items['LastModified']) + "\t" + file_extension_tok[0]+"."+file_extension_tok[1])
              else:
                print("\t"+first_level[0])
            # if object is folder
            elif(len(first_level[0]) > 0):
              if(is_long_form == True):
                print("Folder" + "\t" + str(items['Size']) + "\t" + str(items['LastModified']) + "\t" + first_level[0] + "/")
              else:
                print("-dir-\t" +first_level[0])

# Function for displaying present working directory
def pwd():
  path = ""
  for i in stack:
    path = path + i + "/"
  print(path)

# Function for changing directory
def cd(command):
  global stack
  path = ""
  tokens = command.split(' ')
  found = False
  new_path = ""

  if(len(tokens) == 1 or len(tokens) > 2):
    print("Invalid Arguments")
    return
  # go to root dir
  if(tokens[1] == "~"):
    stack = []
    stack.append("s3:")
  # go back 1 dir which deletes last item in path stack
  elif(".." in command):
    if(len(stack) > 1):
      del stack[-1]
  # Go to a dir if it exists
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

# Function for uploading files
def upload(command):
  global stack
  path = ""
  tokens = command.split(' ')
  # checks how many parameters are given and then create path
  if(len(tokens) == 3):
    path = tokens[2]
  elif(len(tokens) == 2):
    for i in stack:
      path = path + i + "/"
    path = path + tokens[1]
  else:
    print("Invalid Arguments")
    return
  
  obj = parse_cp(path)
  
  try:
    s3.meta.client.upload_file(tokens[1],obj['bucket'],obj['path']+tokens[1])
  except ClientError as error:
    print(error)
    return

# Function for making dir
def mkdir(command):
  global stack, client

  if(len(stack) == 1):
    print("Directory cannot be made here")
    return

  path = ""
  tokens = command.split(" ")
  if(len(tokens) != 2):
    print("invalid argument for mkdir: mkdir <directory name>")
    return

  name = tokens[1]
  
  for i in range(2,len(stack)):
    path = path + stack[i] + "/"

  try:
    client.put_object(Bucket = stack[1], Key=(path+name+"/"))
  except ClientError as error:
      print(error)
      return

# Function for removing dir
def rmdir(command):
  global stack
  path = ""

  if(len(stack) == 1):
    print("Cannot remove directory here")
    return
  
  tokens = command.split(" ")
  if(len(tokens) == 1):
    print("Invalid Arguments rmdir <dir name>")

  name = tokens[1]
  
  for i in range(2,len(stack)):
    path = path + stack[i] + "/"

  bucket = s3.Bucket(stack[1])
  bucket.objects.filter(Prefix=(path+name+"/")).delete()
  
# Function for downloading a file
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
          print(e)

# Function for copying file to different locations
def cp(command):
  tokens = command.split(' ')
  path1=""
  path2=""
  file_name = 0 #1 means first arg contains file 2 mean second arg contains file

  if(len(tokens) == 1):
    print("Invalid Args")
    return
  first = parse_cp(tokens[1])
  second = parse_cp(tokens[2])
  
  # create src object
  src = {
    'Bucket':first['bucket'],
    'Key':first['path'] +first['file']
  }
  # copy from src to second bucket
  bucket = s3.Bucket(second['bucket'])
  if('s3:' not in tokens[2]):
    try:
      bucket.copy(src, second['path']+second['file']+'/'+first['file'])
    except ClientError as error:
      print(error)
  else:
    try:
      bucket.copy(src,second['path']+first['file'])
    except ClientError as error:
      print(error)
  
# Function for moving files 
def mv(command):
  tokens = command.split(' ')
  if(len(tokens) != 3):
    print("invalid Arguments")
    return

  first = parse_cp(tokens[1])
  second = parse_cp(tokens[2])

  # Create src obj
  src = {
    'Bucket':first['bucket'],
    'Key':first['path'] +first['file']
  }
  # Move src to dest
  bucket = s3.Bucket(second['bucket'])
  if('s3:' not in tokens[2]):
    try:
      bucket.copy(src, second['path']+second['file']+'/'+first['file'])
    except ClientError as error:
      print(error)
  else:
    bucket.copy(src,second['path']+first['file'])
  # delete src object
  src_obj = s3.Object(first['bucket'],first['path']+first['file'])
  src_obj.delete()

# Function for removing objects
def rm(command):
  tokens = command.split(' ')
  is_cur_dir = False
  path = ""

  if(len(tokens) != 2):
    print("Invalid Args")
    return
  if("/" not in tokens[1]):
    is_cur_dir = True

  # If file is in current directory
  if(is_cur_dir == True):
    # Make path
    for i in stack:
      path = path + i + "/"
    path = path + tokens[1]
    # if trying to remove bucket
    if(len(stack) == 1):
      try:
        bucket = s3.Bucket(tokens[1])
        for key in bucket.objects.all():
          key.delete()
        bucket.delete()
      except ClientError as error:
        print(error)
    # Removing normal object
    else:
      obj = parse_cp(path)
      src_obj = s3.Object(obj['bucket'],obj['path']+obj['file'])
      src_obj.delete()
      
  else:
    obj = parse_cp(tokens[1])
    if(len(obj['path'])== 0 and len(obj['file']) == 0):
      try:
        bucket = s3.Bucket(obj['bucket'])
        for key in bucket.objects.all():
          key.delete()
        bucket.delete()
      except ClientError as error:
        print(error)
    else:
      src_obj = s3.Object(obj['bucket'],obj['path']+obj['file'])
      src_obj.delete()
 
# Shell
def run_shell():
  logged = False
  while True:
    command = input("$ ")
    if(logged == False and "login" not in command):
      print("Please Login")
    elif (command == "exit" or command == "quit" or command == "logout"):
      break
    elif(command[:5] == "login"):
      if(logged == False):
        logged = True
        login(command)
    elif(command[:8] == "mkbucket"):
      mkbucket(command)
    elif(command[:2] == "ls"):
      ls(command)
    elif(command == "pwd"):
      pwd()
    elif(command[:2] == "cd"):
      cd(command)
    elif(command[:6] == "upload"):
      upload(command)
    elif(command[:5] == "mkdir" and command[2] != " "):
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
       print("Invalid Command")


run_shell()

