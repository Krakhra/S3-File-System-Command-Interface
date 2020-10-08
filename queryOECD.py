import boto3
from prettytable import PrettyTable
from boto3.dynamodb.conditions import Key,Attr,And
from botocore.exceptions import ClientError

# Function for doing the analysis
def analysis(com):
  # if invalid input
  if(len(com) == 0):
    print("Invalid Commodity")
    return
  if(" " in com):
    print("Please enter proper code for commodity")
    return
  
  # Initialize Boto3
  try:
    dynamodb = boto3.resource('dynamodb')
  except ClientError as e:
    print("Unable to initialize boto3.resource. "+e)

  # Checks if there is any table missing 
  all_table = dynamodb.meta.client.list_tables()['TableNames']
  if('encodings' not in all_table or 'canada' not in all_table or 'northamerica' not in all_table or 'usa' not in all_table or 'mexico' not in all_table):
    print("A table is missing. Please make sure all tables are created: encodings, canada, northamerica, usa, mexico")
    return
  
  # init tables and counters
  table = dynamodb.Table('encodings')
  canada_table = dynamodb.Table('canada')
  na_table = dynamodb.Table('northamerica')
  usa_table = dynamodb.Table('usa')
  mexico_table = dynamodb.Table('mexico')
  t_ca_us = 0
  t_neither = 0
  t_ca_us_me = 0

  # get all variable names
  variables = table.scan(
    FilterExpression=Attr('type').eq('variable')
  )
  # get the description of the commodity
  commodity_desc = table.scan(
    FilterExpression=Attr('value').eq(com)
  )
  # Checks for commodity 
  if(len(commodity_desc['Items']) == 0):
    print("Specified commodity does not exist")
    return
  
  # Loops over variables
  for i in variables['Items']:
    # gets response, which is filtered 
    canada_response = canada_table.scan(
      FilterExpression=Attr('commodity').eq(com) & Attr('variable').eq(i['value'])
    )
    na_response = na_table.scan(
      FilterExpression=Attr('commodity').eq(com) & Attr('variable').eq(i['value'])
    )
    usa_response = usa_table.scan(
      FilterExpression=Attr('commodity').eq(com) & Attr('variable').eq(i['value'])
    )
    mexico_response = mexico_table.scan(
      FilterExpression=Attr('commodity').eq(com) & Attr('variable').eq(i['value'])
    )
    # if items are not empty loop over response
    if(len(na_response['Items']) > 0):
      ca_us = 0
      neither = 0
      ca_us_me = 0
      print("Variable: " + i['description'])
      t = PrettyTable(['Year','North America','Canada','USA','Mexico','CAN+USA','CAN+USA+MEX',"NA Defn"])
      for i in range(0,len(na_response['Items'])):
        na_val = float(na_response['Items'][i]['value'])
        # multiply values by their factors
        if(na_response['Items'][i]['mfactor'] == '3'):
          na_val = na_val * 1000
        elif(na_response['Items'][i]['mfactor'] == '6'):
          na_val = na_val * 1000000

        canada_val = float(canada_response['Items'][i]['value'])
        # multiply values by their factors
        if(na_response['Items'][i]['mfactor'] == '3'):
          canada_val = canada_val * 1000
        elif(na_response['Items'][i]['mfactor'] == '6'):
          canada_val = canada_val * 1000000

        usa_val = float(usa_response['Items'][i]['value'])
        # multiply values by their factors
        if(na_response['Items'][i]['mfactor'] == '3'):
          usa_val = usa_val * 1000
        elif(na_response['Items'][i]['mfactor'] == '6'):
          usa_val = usa_val * 1000000

        mexico_val = float(usa_response['Items'][i]['value'])
        # multiply values by their factors
        if(na_response['Items'][i]['mfactor'] == '3'):
          mexico_val = mexico_val * 1000
        elif(na_response['Items'][i]['mfactor'] == '6'):
          mexico_val = mexico_val * 1000000
        
        nadef=""
        # increment counters
        if((canada_val + usa_val) == na_val):
          nadef = "CAN+USA"
          ca_us += 1
          t_ca_us += 1
        elif((canada_val+usa_val+mexico_val) == na_val):
          nadef = "CAN+USA+MEX"
          ca_us_me += 1
          t_ca_us_me += 1
        else:
          nadef = "Neither"
          neither += 1
          t_neither += 1
          # add to table
        t.add_row([na_response['Items'][i]['year'], str(round(na_val,2)), str(round(canada_val,2)), str(round(usa_val,2)), str(round(mexico_val,2)), str(round(canada_val+usa_val,2)), str(round(canada_val + usa_val + mexico_val,2)), nadef])
      
      print(t)
      print("North America Definition Results:\t"+ str(ca_us) +" "+ "CAN+USA,\t" + str(ca_us_me)+" "+ "CAN+USA+MEX,\t"+str(neither)+ " " +"Neither")
      s_conc = ""
      if(ca_us > ca_us_me and ca_us > neither):
        s_conc = "CAN+USA"
      elif(ca_us_me > ca_us and ca_us_me > neither):
        s_conc = "CAN+USA+MEX"
      else:
        s_conc = "Neither"
      print("Therefore we conclude North America = "+s_conc)
  o_conc = ""
  if(t_ca_us > t_ca_us_me and t_ca_us > t_neither):
    o_conc = "CAN+USA"
  elif(t_ca_us_me > t_ca_us and t_ca_us_me > t_neither):
    o_conc = "CAN+USA+MEX"
  else:
    o_conc = "Neither"
  print("Overall North America Definition Results:\t"+ str(t_ca_us) +" "+ "CAN+USA,\t" + str(t_ca_us_me)+" "+ "CAN+USA+MEX,\t"+str(t_neither)+ " " +"Neither")
  print("Conclusion for all "+ commodity_desc['Items'][0]['description']+" variables, North America = "+o_conc)

# Function for getting commodity from cmd line
def get_commodity():
  commodity = input("Please enter a commodity code, example: WT.: ")
  return commodity

com = get_commodity()
analysis(com)