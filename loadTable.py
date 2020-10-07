import boto3
import csv

file_name = ""
table_name = ""

def load_table(table):
  global file_name, table_name

  if("." not in file_name):
    print("Invalid File Name")
    return

  # dynamodb = boto3.resource('dynamodb')
  # table = dynamodb.Table(table_name)
  with open(file_name) as csvfile:
    reader = csv.reader(csvfile,delimiter=',')
  
    for row in reader:
      row.append(row[1]+"/"+row[2])
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

def create_table(dynamodb=None):
  global file_name, table_name
  if(len(file_name) == 0 or len(table_name) == 0):
    print("Invalid File Name")
    return

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
        'AttributeName':'variableyear',
        'AttributeType':'S'
      },
    ],
    ProvisionedThroughput={
      'ReadCapacityUnits': 10,
      'WriteCapacityUnits': 10
    }
  )
  return table
  
def get_name():
  global file_name, table_name
  file_name = input("Enter File Name:")
  table_name = input("Enter Table Name: ")  

get_name()
table = create_table()
print("Waiting for table creation...")
table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
print("Table created loading file...")
load_table(table)

