import boto3
import csv
import sys

dynamodb = boto3.resource('dynamodb')

# function for creating table
def create_table():
  global dynamodb

  all_table = dynamodb.list_tables()['TableNames']
  if('encodings' in all_table):
    print("Table Already Exists")
    return False

  table = dynamodb.create_table(
    TableName = "encodings",
    KeySchema = [
      {
        'AttributeName': 'value',
        'KeyType':'HASH'
      }
    ],
    AttributeDefinitions=[
      {
        'AttributeName':'value',
        'AttributeType':'S'
      },
    ],
    ProvisionedThroughput={
      'ReadCapacityUnits': 10,
      'WriteCapacityUnits': 10
    }
  )
  return table

# Function for loading table
def load_table():
  with open("encodings.csv") as csvfile:
    reader = csv.reader(csvfile,delimiter=',')
    for row in reader:
      table.put_item(
        Item = {
          'value':row[0],
          'description':row[1],
          'type':row[2]
        }
      )
  
table = create_table()
if(table == false):
  sys.exit()
  
print("Waiting for table creation...")
table.meta.client.get_waiter('table_exists').wait(TableName="encodings")
print("Table created loading file...")
load_table()