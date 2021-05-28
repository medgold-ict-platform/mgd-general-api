import time
import requests
import boto3
import os
import pytest
from requests import ConnectionError

endpoint = os.environ["endpoint"]
AuthorizationToken = os.environ["requestToken"]
dynamoTableInfo = os.environ["dynamoTableInfo"]
dynamoTableWF = os.environ["dynamoTableWF"]

### 
# TESTING SUCCESSFULL OF /datasets,  /request , /dataset/{id}/info, /dataset/{id}/wfs RESOURCES
###

def test_01():
    """
    Checks if datasets API returns all elements in dev-medgold-dataset_info table
    """
    dynamo = boto3.resource("dynamodb")
    table = dynamo.Table(dynamoTableInfo)
    table_response = table.scan()
    url = endpoint+"datasets"
    print(url)
    request = requests.request("GET", url=url, headers={"Authorization":AuthorizationToken})
    assert len(request.json()) == len(table_response["Items"])


def test_02():
    """
    Checks if dataset/{id}/info API returns all informations for all datesets presents in dynamo
    """
    dynamo = boto3.resource("dynamodb")
    table = dynamo.Table(dynamoTableInfo)
    table_response = table.scan()["Items"]
    for dataset in table_response:
        url = endpoint+"dataset/"+dataset["id"]+"/info"
        print(url)
        request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
        assert "id" in str(request.json())
        assert "area" in str(request.json())
        assert "description" in str(request.json())
        assert "end_date" in str(request.json())
        assert "name" in str(request.json())
        assert "start_date" in str(request.json())
        assert "vars" in str(request.json())

def test_03():
    """
    Check if /dataset/{id}/wfs returns workflow for every id
    """
    dynamo = boto3.resource("dynamodb")
    table = dynamo.Table(dynamoTableWF)
    table_response = table.scan()["Items"]
    for item in table_response:
        url = endpoint + "dataset/" + item["dataset"] + "/wfs"
        print(url)
        request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
        for resp in request.json():
            assert resp["id"] == item["id"]
            assert resp["dataset"] == item["dataset"]
'''
def test_04():
    """
    Check if /request returns 200
    """
    dynamo = boto3.resource("dynamodb")
    table = dynamo.Table(dynamoTableWF)
    table_response = table.scan()["Items"]

    for item in table_response:
        if item["dataset"] == 'ecmwf' and item["id"] == 'horta':
            url_1 = endpoint + "dataset/" + item["dataset"] + "/workflow/" + item["id"] + "?"
            params = {"lat": "38", "lng": "11", "vars": "totprec,tmax2m,10v,10u,2d,ssrd", "years": "2018", "months": "11"}
            for param in params:
                url_1 = url_1 + param + "=" + params[param] + "&"
            url_1 = url_1.strip("&")
            print(url_1)
            request_1 = requests.request("GET", url=url_1, headers={"Authorization": AuthorizationToken})
            m_id = request_1.json()["MessageId"]
            url = endpoint + "request?id="+m_id
            request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
            assert 200 == int(request.status_code)
'''
### 
# PARAMETER VALIDATION OF GENERAL RESOURCES
###

def test_pv_01_02():
    """
    Check if /dataset/{id}/info returns error for invalid id
    """
    url = endpoint+'dataset/ecmw/info'
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert 'BadRequestError: dataset id not found!' in str(request.json())
    assert 'BadRequestError' in str(request.json())

def test_pv_01_03():
    """
    Check if /dataset/{id}/wfs returns error for invalid id
    """
    url = endpoint+'dataset/ecmw/wfs'
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert 'BadRequestError: dataset id not found!' in str(request.json())
    assert 'BadRequestError' in str(request.json())

def test_pv_01_04():
    """
    Check if /request returns error for invalid id
    """
    url = endpoint+'request?'
    url = '{}&id={}'.format(url,'notvalidID')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert 'BadRequestError: Request Id not found!' in str(request.json())
    assert 'BadRequestError' in str(request.json())


### 
# TESTING CORRECT EXECUTION OF EACH WORKFLOW 
###

def test_wf_01():
    """
    Check if /horta API returns 200
    """
    places = {"RAVENNA": {"lat": "12.17", "lng": "44.48"}, "JESI": {"lat": "13.27", "lng": "43.53", "var": "totprec,tmax2m"}, "FOGGIA": {"lat": "15.56", "lng": "41.34"}}
    for place in places:
        url = endpoint + "horta?"
        for param in places[place]:
            url = url + param + "=" + places[place][param] + "&"
        url = url.strip("&")
        print(url)
        request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
        assert 200 == int(request.status_code)
'''
def test_wf_02():
    """
    Check if /dataset/ecmwf/workflow/horta returns a message id and if the workflow goes right
    """
    
    dataset = 'ecmwf'
    workflow = 'horta'

    url = endpoint + "dataset/" + dataset + "/workflow/" + workflow+"?"
    url = '{}&lat={}&lng={}&vars={}&years={}&months={}'.format(url,'38','11', 'totprec', '2018', '11')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "MessageId" in request.json()
    message_id = request.json()["MessageId"]
    print(message_id)
    url = endpoint+"request?id="+message_id
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert request.json()["State"] in ["pending", "working", "done"]
    while not request.json()["State"] == "done":
        time.sleep(10)
        request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
        print(request.json()["State"])
    s3 = boto3.resource("s3")
    key = request.json()["Data"][25:]

    try:
        s3.Object("data.med-gold.eu", key).load()
        assert True
    except Exception:
        assert False
'''
def test_wf_02_SF():
    """
    Check if /dataset/ecmwf/workflow/horta returns a message id and if the workflow goes right
    """
    
    dataset = 'ecmwf'
    workflow = 'horta'

    url = endpoint + "dataset/" + dataset + "/workflow/" + workflow+"?"
    url = '{}&lat={}&lng={}&vars={}&years={}&months={}'.format(url,'38','11', 'totprec', '2018', '11')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "MessageId" in request.json()
    message_id = request.json()["MessageId"]
    print(message_id)
    url = endpoint+"request?id="+message_id
    print(url)
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    print(request.json())
    while not request.json()["apirequest"]['info']['state'] == "done":
        time.sleep(10)
        request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
        print(request.json()["apirequest"]['info']['state'])
    s3 = boto3.resource("s3")
    key = request.json()["apirequest"]['info']["data"][25:]
    try:
        s3.Object("data.med-gold.eu", key).load()
        assert True
    except Exception:
        assert False
'''
def test_wf_03():
    """
    Check if /dataset/agmerra/workflow/pbdm returns a message id and if the workflow goes right
    """

    dataset = 'agmerra'
    workflow = 'pbdm'

    url = endpoint + "dataset/" + dataset + "/workflow/" + workflow+"?"
    url = '{}&country={}&sdate={}&edate={}&model={}&dataset={}&output_time_interval={}'.format(url,'ESP-POR','1994/01/01', '1997/12/31', 'olive',  'agmerra','365')

    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "MessageId" in request.json()
    message_id = request.json()["MessageId"]
    print(message_id)
    url = endpoint+"request?id="+message_id
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert request.json()["State"] in ["pending", "working", "done"]
    while not request.json()["State"] == "done":
        time.sleep(10)
        request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
        print(request.json()["State"])
    s3 = boto3.resource("s3")
    key = request.json()["data"][25:]

    try:
        s3.Object("data.med-gold.eu", key).load()
        assert True
    except Exception:
        assert False
'''

### 
# TESTING ERROR CASES (FOR MISSING PARAMETERS) OF EACH WORKFLOW 
###

def test_pv_01_wf_02():
    """
     Check if /dataset/ecmwf/workflow/horta returns error if one or more parameter are not given
    """

    dataset = 'ecmwf'
    workflow = 'horta'

    base_url = endpoint + "dataset/" + dataset + "/workflow/" + workflow+"?"
    url = '{}&lat={}&lng={}&vars={}&years={}'.format(base_url,'38','11', 'totprec', '2018')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: months: one or more value are required" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&lat={}&lng={}&vars={}&months={}'.format(base_url,'38','11', 'totprec', '11')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: years: one or more value are required" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&lat={}&lng={}&months={}&years={}'.format(base_url,'38','11', '11', '2018')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: vars: one or more value are required" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&months={}&lng={}&vars={}&years={}'.format(base_url,'11','38', 'totprec', '2018')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: latitude value is required" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&lat={}&months={}&vars={}&years={}'.format(base_url,'38','11', 'totprec', '2018')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: longitude value is required" in str(request.json())
    assert "BadRequestError" in str(request.json())

def test_pv_02_wf_02():
    """
     Check if /dataset/ecmwf/workflow/horta returns error if one or more parameter are not right
    """
    dataset = 'ecmwf'
    workflow = 'horta'

    base_url = endpoint + "dataset/" + dataset + "/workflow/" + workflow+"?"
    url = '{}&lat={}&lng={}&vars={}&years={}&months={}'.format(base_url,'38','11', 'toprec', '2018', '11')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: vars values not valid" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&lat={}&lng={}&vars={}&years={}&months={}'.format(base_url,'38','11', 'totprec', '2018', '12')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: data not avaiable for selected months" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&lat={}&lng={}&vars={}&years={}&months={}'.format(base_url,'38','11', 'totprec', '1979', '11')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: years values not valid" in str(request.json())
    assert "BadRequestError" in str(request.json())

def test_pv_01_wf_03():
    """
     Check if /dataset/agmerra/workflow/pbdm returns error if one or more parameter are not given
    """
    dataset = 'agmerra'
    workflow = 'pbdm'

    base_url = endpoint + "dataset/" + dataset + "/workflow/" + workflow+"?"
    url = '{}&country={}&sdate={}&edate={}&model={}&dataset={}'.format(base_url,'ESP-POR','1994/01/01', '1997/12/31', 'olive', 'agmerra')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: output_time_interval value not valid!" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&country={}&sdate={}&edate={}&model={}&output_time_interval={}'.format(base_url,'ESP-POR','1994/01/01', '1997/12/31', 'olive', '365')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: dataset value not valid!" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&country={}&sdate={}&edate={}&output_time_interval={}&dataset={}'.format(base_url,'ESP-POR','1994/01/01', '1997/12/31', '365', 'agmerra')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: model value not valid" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&country={}&sdate={}&output_time_interval={}&model={}&dataset={}'.format(base_url,'ESP-POR','1994/01/01', '365', 'olive', 'agmerra')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: edate value is required" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&country={}&output_time_interval={}&edate={}&model={}&dataset={}'.format(base_url,'ESP-POR','365', '1997/12/31', 'olive', 'agmerra')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: sdate value is required" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&output_time_interval={}&sdate={}&edate={}&model={}&dataset={}'.format(base_url,'365','1994/01/01', '1997/12/31', 'olive', 'agmerra')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: country value not valid!" in str(request.json())
    assert "BadRequestError" in str(request.json())

def test_pv_02_wf_03():
    """
     Check if /dataset/agmerra/workflow/pbdm returns error if one or more parameter are not right
    """
    dataset = 'agmerra'
    workflow = 'pbdm'

    base_url = endpoint + "dataset/" + dataset + "/workflow/" + workflow+"?"
    url = '{}&country={}&sdate={}&edate={}&model={}&dataset={}&output_time_interval={}'.format(base_url,'ESP-PO','1994/01/01', '1997/12/31', 'olive', 'agmerra', '365')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: country value not valid!" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&country={}&sdate={}&edate={}&model={}&dataset={}&output_time_interval={}'.format(base_url,'ESP-POR','1994/30/01', '1997/12/31', 'olive', 'agmerra', '365')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: Invalid date! Correct date format is YYYY/MM/DD" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&country={}&sdate={}&edate={}&model={}&dataset={}&output_time_interval={}'.format(base_url,'ESP-POR','1994/01/01', '1997/30/31', 'olive', 'agmerra', '365')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: Invalid date! Correct date format is YYYY/MM/DD" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&country={}&sdate={}&edate={}&model={}&dataset={}&output_time_interval={}'.format(base_url,'ESP-POR','1994/01/01', '1997/12/31', 'oliv', 'agmerra', '365')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: model value not valid" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&country={}&sdate={}&edate={}&model={}&dataset={}&output_time_interval={}'.format(base_url,'ESP-POR','1994/01/01', '1997/12/31', 'olive', 'agmerr', '365')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: dataset value not valid" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&country={}&sdate={}&edate={}&model={}&dataset={}&output_time_interval={}'.format(base_url,'ESP-POR','1970/01/01', '1997/12/31', 'olive', 'agmerra', '365')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: interval date not valid" in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}&country={}&sdate={}&edate={}&model={}&dataset={}&output_time_interval={}'.format(base_url,'ESP-POR','1996/01/01', '2015/12/31', 'olive', 'agmerra', '365')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "BadRequestError: interval date not valid" in str(request.json())
    assert "BadRequestError" in str(request.json())

def test_pv_01_wf_01():
    """
     Check if /horta returns error if one or more parameter are not given
    """
    url = '{}horta?lat={}'.format(endpoint,'44.48')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "The files required does not exist. Please, check the coordinates or variables name." in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}horta?lng={}'.format(endpoint,'12.17')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "The files required does not exist. Please, check the coordinates or variables name." in str(request.json())
    assert "BadRequestError" in str(request.json())

def test_pv_02_wf_01():
    """
     Check if /horta returns error if latitude or longitude value are not available
    """
    url = '{}horta?lat={}&lng={}'.format(endpoint,'44.48', '12.16')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "The files required does not exist. Please, check the coordinates or variables name." in str(request.json())
    assert "BadRequestError" in str(request.json())

    url = '{}horta?lat={}&lng={}'.format(endpoint,'44.47', '12.17')
    request = requests.request("GET", url=url, headers={"Authorization": AuthorizationToken})
    assert "The files required does not exist. Please, check the coordinates or variables name." in str(request.json())
    assert "BadRequestError" in str(request.json())

