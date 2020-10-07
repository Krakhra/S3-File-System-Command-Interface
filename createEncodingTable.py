import boto3
import csv

dynamodb = boto3.resource('dynamodb')

def create_table():
  global dynamodb

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
print("Waiting for table creation...")
table.meta.client.get_waiter('table_exists').wait(TableName="encodings")
print("Table created loading file...")
load_table()