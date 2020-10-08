# Imports
import boto3
import csv
from botocore.exceptions import ClientError
import sys

# Globals
file_name = ""
table_name = ""

# Function for loading the csv into the tables
def load_table(table):
  global file_name, table_name

  # if file name does not have extension 
  if("." not in file_name):
    print("Invalid File Name")
    return

  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table(table_name)
  # open csv
  with open(file_name) as csvfile:
    reader = csv.reader(csvfile,delimiter=',')
  
    for row in reader:
      # create a new field for sort key
      row.append(row[1]+"/"+row[2])
      try:
        table.put_item(
          Item = {
            'commodity':row[0],
            'variable':row[1],
            'year':row[2],
            'units':row[3],
            'mfactor':row[4],
            'value':row[5],
            'variableyear':row[6]
          }
        )
      except ClientError as e:
        print("Error while loading csv into table. "+e )
        return 

# Function for Creating the tables
def create_table(dynamodb=None):
  global file_name, table_name
  # if table name or file name are 
  if(len(file_name) == 0 or len(table_name) == 0):
    print("Invalid File Name or table name")
    return False

  # if dynamodb not initialized
  if not dynamodb:
    try:
      dynamodb = boto3.resource('dynamodb')
    except ClientError as e:
      print("Unable to initialize boto3.resource. "+ e)
      return False
  # Check if table exists already
  all_table = dynamodb.meta.client.list_tables()['TableNames']
  if(table_name in all_table):
    print("Table Already Exists")
    return False
  # Create table
  try:
    table = dynamodb.create_table(
      TableName = table_name,
      KeySchema = [
        {
          'AttributeName': 'commodity',
          'KeyType':'HASH'
        },
        {
          'AttributeName': 'variableyear',
          'KeyType':'RANGE'
        }
      ],
      AttributeDefinitions=[
        {
          'AttributeName':'commodity',
          'AttributeType':'S'
        },
        {
          'AttributeName':'variableyear',
          'AttributeType':'S'
        },
      ],
      ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
      }
    )
  except ClientError as e:
    print("Unable to create table. "+ e)
  return table
  
# Function for getting table name
def get_name():
  global file_name, table_name
  file_name = input("Enter File Name:")
  table_name = input("Enter Table Name: ")  

get_name()
table = create_table()
if(table == False):
  sys.exit()

print("Waiting for table creation...")
table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
print("Table created loading file...")
load_table(table)

