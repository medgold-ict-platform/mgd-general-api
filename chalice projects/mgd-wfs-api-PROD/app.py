from chalice import Chalice, Cron
from chalice import Response
from chalice import BadRequestError
import boto3
from warrant import Cognito, exceptions, AWSSRP
import os
import base64
import botocore
import datetime
import zipfile
import json
from botocore.exceptions import ClientError
from chalice import CognitoUserPoolAuthorizer
from boto3.dynamodb.conditions import Attr 


##BOTO##
s3 = boto3.resource("s3")
s3Client = boto3.client('s3')

##BUCKET S3##
BUCKET_NAME= os.environ['BUCKET_NAME']
bucket = s3.Bucket(BUCKET_NAME)
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

##CHALICE##
app = Chalice(app_name="demoapp"+os.environ['stage'])
app.debug= True

available_months = [x for x in range(1,13)]


##APP##
list_of_variables = ['totprec', 'tmax2m', 'tmin2m']
download_path = os.environ['download_path']
upload_path = os.environ['upload_path']
vars='{"totprec": "total precipitation","tmin2m": "minimum_2m_temperature_in_the_last_24_hours","10u": "10m_u_component_of_wind","10v": "10m_v_component_of_wind","2d": "2m_dewpoint_temperature","ssrd": "surface_solar_radiation_downwards","tmax2m": "maximum_2m_temperature_in_the_last_24_hours"}'
bounding_box = [52, -13, 29, 38]
##DYNAMO##
table = dynamodb.Table(os.environ['requests_table'])
table_wf = dynamodb.Table(os.environ['workflow_table'])
table_ds = dynamodb.Table(os.environ['datasetinfo_table'])

##SQS##
queue_url = os.environ['queue_url']
queue_pbdm = os.environ['queue_pbdm']

##COGNITO##
authorizer = CognitoUserPoolAuthorizer(
    'dev-med-gold',
    header='Authorization',
    provider_arns=[os.environ['cognito_arns']])
pool_id = os.environ['pool_id']
pool_region = os.environ['pool_region']
client_id = os.environ['client_id']
stepfunclient = boto3.client('stepfunctions')

##HORTA FO-RA-JESI##

@app.route('/horta', content_types=['application/json'],authorizer=authorizer, cors = True)
def get_all_file_for_coordinates():
  latitude = app.current_request.query_params.get('lat')
  longitude = app.current_request.query_params.get('lng')
  variables = app.current_request.query_params.get('vars')

  if not variables:
    variables = list_of_variables
    zip_file_name = str(latitude) +'-'+ str(longitude) + '_all.zip'
  else:
    variables = variables.split(',')
    zip_file_name = str(latitude) +'-'+ str(longitude) + ''.join(variables)+'.zip'
  
  try:
    s3.Object(BUCKET_NAME, upload_path+zip_file_name).load()
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
      try:
        get_file_from_s3Bucket(variables, latitude, longitude, zip_file_name)
      except Exception as e:
        raise BadRequestError('The files required does not exist. Please, check the coordinates or variables name.')
    else:
        raise
  
  url ='{}/{}/{}'.format(s3Client.meta.endpoint_url, BUCKET_NAME, upload_path+zip_file_name)


  return Response(
        status_code=301,
        body='',
        headers={'Location': url})

##HORTA FO-RA-JESI##
def get_file_from_s3Bucket(variables, latitude, longitude, zip_file_name, authorizer=authorizer):
  bucket_prefix="Locations/" + str(latitude) +'-'+ str(longitude) + '/'

  try:
    for variable in variables:
      objs = bucket.objects.filter(Delimiter = '/', Prefix = bucket_prefix+variable+'/')
      for obj in objs:
        name_of_file = obj.key.split('/')[-1]
        #download the file
        if 'csv' in name_of_file:
          bucket.download_file(obj.key, download_path+name_of_file)
          f = open(download_path+name_of_file, 'r') 
          with zipfile.ZipFile(download_path+zip_file_name, 'a') as myzip:
            myzip.write(download_path+name_of_file, variable+'/'+name_of_file)
    
    bucket.upload_file(download_path+zip_file_name, upload_path + zip_file_name)
    object = s3.Bucket(BUCKET_NAME).Object(upload_path + zip_file_name)
    object.Acl().put(ACL='public-read')
  except botocore.exceptions.ClientError as e:
    raise


##_ECMWF WF_##
@app.route('/dataset/{id}/workflow/{wf}', content_types=['application/json'], cors = True, authorizer=authorizer)
def index(wf, id):
  query_params = app.current_request.query_params
  if wf == 'horta' and id == 'ecmwf':
    latitude = query_params.get('lat')
    longitude = query_params.get('lng')
    years = query_params.get('years')
    months = query_params.get('months')
    variables = query_params.get('vars')

    if variables is not None:
      variables = variables.split(',')
    else:
      raise BadRequestError('vars: one or more value are required')

    if months is not None:
      months = months.split(',')
    else:
      raise BadRequestError('months: one or more value are required')

    if years is not None:
      years = years.split(',')
    else:
      raise BadRequestError('years: one or more value are required')
  
    err_message = variables_check(latitude, longitude, variables, years, months)
    
    if 'no_error' in err_message:
      reqId =app.current_request.context.get('requestId')
      response = stepfunclient.start_execution(
        stateMachineArn=os.environ['state_machine_arn'],
        name = reqId,
        input= json.dumps({"apirequest":{"info" :{"state":"pending","data": "","id":reqId, "count": 0}, "input": {"lat": latitude, "lng": longitude, "vars": variables, "years": years, "months": months}}})
      )
      s = '{"MessageId" : "'+ reqId + '"}'
      return json.loads(s)
    else:
      raise BadRequestError(err_message)
  elif wf == 'pbdm' and id == 'agmerra':
      sdate = query_params.get('sdate')
      edate = query_params.get('edate')
      country = query_params.get('country')
      dataset = query_params.get('dataset')
      model = query_params.get('model')
      out_time_int = query_params.get('output_time_interval')

      err_message = pbdm_var_check(sdate, edate, country, dataset, model, out_time_int)
    
      if 'no_error' in err_message:
        #Send message to SQS queue
        response_sqs = sqs.send_message(
            QueueUrl=queue_pbdm,
            MessageAttributes={
                'country': {
                    'DataType': 'String',
                    'StringValue': country
                },
                'start_date': {
                    'DataType': 'String',
                    'StringValue': sdate
                },
                'end_date': {
                    'DataType': 'String',
                    'StringValue': edate
                },
                'model': {
                    'DataType': 'String',
                    'StringValue': model
                },
                'dataset': {
                    'DataType': 'String',
                    'StringValue': dataset
                },
                'output_time_interval': {
                    'DataType': 'String',
                    'StringValue': out_time_int
                }
            },
            MessageBody=(
                'API Request'
            )
        )
      else:
        raise BadRequestError(err_message)
      
    

  response = table.put_item(
    Item={
          'MessageId': response_sqs['MessageId'],
          'State': 'pending',
          'Data': ' '
      }
  )

  messageId = str(response_sqs['MessageId'])
  s = '{"MessageId" : "'+ messageId + '"}'
  return json.loads(s)

##_LIST OF DATASETS_##
@app.route('/datasets', content_types=['application/json'], cors = True, authorizer=authorizer)
def get_all_datasets_info():
  try:
    response = table_ds.scan()
  except ClientError as e:
      raise

  items = response['Items']
  
  new_data = [{"dataset": i} for i in items]
  json_data = json.dumps(new_data)

  return json_data

##_DATASET INFO_##
@app.route('/dataset/{id}/info', content_types=['application/json'],cors = True, authorizer=authorizer)
def get_info(id):
  try:
    response = table_ds.scan(
      FilterExpression = Attr('id').eq(id)
    )
    item = response['Items']
    print("GetItem succeeded:")
  except ClientError as e:
    raise

  if len(item) == 0:
    raise BadRequestError('dataset id not found!')

  return item[0]

##_DATASET WORKFLOWS_##
@app.route('/dataset/{id}/wfs', content_types=['application/json'],cors = True, authorizer=authorizer)
def get_workflows(id):

  try:
    response = table_wf.scan(
      FilterExpression = Attr('dataset').eq(id)
    )

  except ClientError as e:
      raise

  items = response['Items']

  if len(items) == 0:
    raise BadRequestError('dataset id not found!')

  return json.dumps(items)

##_STATE REQUEST_##
def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

##_STATE REQUEST_##
@app.route('/request', content_types=['application/json'],cors = True, authorizer=authorizer)
def get_request_state():
  
  id = app.current_request.query_params.get('id')
  
  item = ''
  try:
    response = table.get_item(
        Key={
            'MessageId': id
        }
    )
    item = response['Item']
    print("GetItem succeeded:")
    print(item)
    return json.dumps(item,default=default)

  except KeyError as e:
    try:
      response = stepfunclient.describe_execution(
        executionArn=os.environ['state_machine_execution'] + id
      )
      print('RESPONSE')
      print(response)
      response = json.loads(response['output'])
      return json.dumps(response,default=default)
    except KeyError as e:
      response = json.loads(response['input'])
      return json.dumps(response,default=default)
    except Exception as e:
      print(e)
      raise BadRequestError('Request Id not found!')

  response = json.loads(response['output'])
  return json.dumps(response,default=default)

def pbdm_var_check(sdate, edate, country, dataset, model, out_time_int):
  if sdate is None:
    return 'sdate value is required'

  if edate is None:
    return 'edate value is required'

  sdate = sdate.split('/')
  edate = edate.split('/')
  try:
    newDate = datetime.date(int(sdate[0]), int(sdate[1]), int(sdate[2]))
    newDate2 = datetime.date(int(edate[0]), int(edate[1]), int(edate[2]))
  except Exception:
    return 'Invalid date! Correct date format is YYYY/MM/DD'

  if int(sdate[0]) < 1980 or int(edate[0]) > 2010 or sdate > edate:
    return 'interval date not valid!'

  if model is None or model != 'olive':
    return 'model value not valid'

  if country is None or country != 'ESP-POR':
    return 'country value not valid!'

  if dataset is None or dataset != 'agmerra':
    return 'dataset value not valid!'

  if out_time_int is None:
    return 'output_time_interval value not valid!'

  return 'no_error'


def variables_check(latitude, longitude, variables, years, months):
  if latitude is None:
    return 'latitude value is required'

  if longitude is None:
    return 'longitude value is required'

  for var in variables:
      if var not in vars:
        return 'vars values not valid'

  r = (str(x) for x in range(1982,2020))
  for y in years:
    if y not in r:
      return 'years values not valid'

  r = (str(x) for x in range(1,13))

  for m in months:
    if m not in r:
      return 'months values not valid'

  r = (str(x) for x in available_months)

  for m in months:
    if m not in r:
      return 'data not avaiable for selected months'
    for year in years:
      if year == '2017' and m != '11':
        return 'data not avaiable for selected year'

  return 'no_error'

@app.route('/security/{service}', content_types=['application/json'], cors = True)
def security_services(service):
  if service == 'token':
    username = app.current_request.query_params.get('username')
    password = app.current_request.query_params.get('password')
    print(username)
    print(password)
    if username == None or password == None:
      return 'Incorrect username or password'
    
    awssrp = AWSSRP(username, password, pool_id, pool_region=pool_region,client_id=client_id)

    try:
        response=awssrp.authenticate_user(password)
    except exceptions.ForceChangePasswordException:
        awssrp = AWSSRP(username, password, pool_id, pool_region=pool_region,client_id=client_id)
        awssrp.set_new_password_challenge(new_password=password)
        response = awssrp.authenticate_user(password)     
    except Exception:
        return 'Incorrect username or password'
    
    return 'token = ' + response["AuthenticationResult"]["IdToken"]
  else:
    return service + ' not available'