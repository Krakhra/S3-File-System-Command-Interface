import boto3
import csv

file_name = ""
table_name = ""

def create_table(dynamodb=None):
  global file_name, table_name

  if not dynamodb:
    dynamodb = boto3.resource('dynamodb')

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
        'AttributeName':'variable',
        'AttributeType':'S'
      },
      {
        'AttributeName':'year',
        'AttributeType':'S'
      },
      {
        'AttributeName':'variableyear',
        'AttributeType':'S'
      },
      {
        'AttributeName':'units',
        'AttributeType':'S'
      },
      {
        'AttributeName':'mfactor',
        'AttributeType':'S'
      },
      {
        'AttributeName':'value',
        'AttributeType':'N'
      }
    ]
  )
  
def get_name():
  global file_name, table_name
  file_name = input("Enter File Name:")
  table_name = input("Enter Table Name: ")
  
get_name()
if(len(file_name) == 0 or len(table_name) == 0):
  print("Invalid File Name")
  return

create_table()


