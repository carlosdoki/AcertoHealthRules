# -*- coding: utf-8 -*-
'''
Marks nodes as historical for an AppDynamics application

Usage: python marknodeshistorical.py [options]

Options:
  -h, --help                     show this help
  -c ..., --controllerURL=...    controller URL
  -n ..., --userName=...         user name
  -p ..., --userPassword=...     user password
'''
import getopt
import requests
import json
import sys
import base64

def usage():
    print(__doc__)

def get_auth(host, user, password):
    url = '{}/controller/auth'.format(host)
    data_string = user + ":" + password
    data_bytes = data_string.encode("utf-8")
    headerBasic = base64.b64encode(data_bytes).decode('utf-8')
    headers = {
        'Authorization': 'Basic ' + headerBasic
    }
    params = (
        ('action', 'login'),
    )
    
    response = requests.get(url, headers=headers, params=params)
    global token
    global cookies
    cookies = response.cookies 
    token = response.cookies.get("X-CSRF-TOKEN")
    return token

def main(argv):

    controllerURL = 'http://yourcontroller:8090'
    userName = 'youruser@customer1'
    userPassword = 'yourpassword'

    try:
        opts, args = getopt.getopt(argv, "hc:n:p:a:", ["help", "controllerURL=", "userName=", "userPassword="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--controllerURL"):
            controllerURL = arg
        elif opt in ("-n", "--userName"):
            userName = arg
        elif opt in ("-p", "--userPassword"):
            userPassword = arg
    if not (controllerURL and userName and userPassword):
        usage()
        sys.exit(2)
    token = get_auth(controllerURL, userName, userPassword)
    resp = requests.get(controllerURL + '/controller/rest/applications?output=JSON', auth=(userName, userPassword), verify=True, timeout=60)
    if (resp.ok):
        appList = json.loads(resp.content)
        for app in appList:
            print(app['name'])

            # url = '{}/controller/alerting/rest/v1/applications/{}/schedules'.format(controllerURL, app['id'])
            # headers = {
            #     'Content-Type': 'application/json;charset=UTF-8',
            #     'Accept': 'application/json,text/plain,*/*',
            #     'X-CSRF-TOKEN': token
            # }
            # data = '{"timezone":"America/Sao_Paulo","scheduleConfiguration":{"startTime":"05:00","endTime":"22:00","days":["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"],"scheduleFrequency":"WEEKLY"},"name":"HorarioComercial", "description":"Horario das 05:00 ate as 22:00 - Seg a Sex."}'
            # resp2 = requests.post(url, headers=headers, data=data, cookies=cookies)

            url = '{}/controller/alerting/rest/v1/applications/{}/schedules'.format(controllerURL, app['id'])
            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json,text/plain,*/*',
                'X-CSRF-TOKEN': token
            }
            resp2 = requests.get(url, headers=headers, cookies=cookies)
            if (resp2.ok):
                scheduleList = json.loads(resp2.content)
                scheduleid = 0
                for schedule in scheduleList:
                    if 'HorarioComercial' in schedule['name']:
                        scheduleid = schedule['id']
                
                if (scheduleid > 0):
                    url = '{}/controller/restui/policy2/policies/{}'.format(controllerURL, app['id'])
                    headers = {
                        'Content-Type': 'application/json;charset=UTF-8',
                        'Accept': 'application/json,text/plain,*/*',
                        'X-CSRF-TOKEN': token
                    }
                    resp3 = requests.get(url, headers=headers,cookies=cookies)
                    if (resp3.ok):
                        policeList = json.loads(resp3.content)
                        for police in policeList:
                            police['schedule'] = scheduleid
                            police['alwaysEnabled'] = False
                            data = json.dumps(police)
                            url = '{}/controller/restui/healthRules/update'.format(controllerURL)
                            headers = {
                                'Content-Type': 'application/json;charset=UTF-8',
                                'Accept': 'application/json,text/plain,*/*',
                                'X-CSRF-TOKEN': token
                            }

                            resp4 = requests.post(url, headers=headers, data=data, cookies=cookies)
                            if (!resp4.ok):
                                print(resp4.raise_for_status())
                    else:
                        print(resp3.raise_for_status())
            else:
                print(resp2.raise_for_status())

    else:
        print(resp.raise_for_status())

if __name__ == "__main__":
    main(sys.argv[1:])