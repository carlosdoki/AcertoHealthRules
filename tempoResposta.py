# -*- coding: utf-8 -*-
'''
Acerto do Tempo de resposta para 95 percentil e Deafult BaseLine for an AppDynamics application

Usage: python tempoResposta.py [options]

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
        opts, args = getopt.getopt(
            argv, "hc:n:p:a:", ["help", "controllerURL=", "userName=", "userPassword="])
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
    resp = requests.get(controllerURL + '/controller/rest/applications?output=JSON',
                        auth=(userName, userPassword), verify=True, timeout=60)
    if (resp.ok):
        appList = json.loads(resp.content)
        for app in appList:
            print(app['name'])
            if ("Colaborar_AVA" in app['name']):
                url = '{}/controller/alerting/rest/v1/applications/{}/schedules'.format(
                    controllerURL, app['id'])
                headers = {
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Accept': 'application/json,text/plain,*/*',
                    'X-CSRF-TOKEN': token
                }
                resp2 = requests.get(url, headers=headers, cookies=cookies)

                if (resp2.ok):
                    scheduleList = json.loads(resp2.content)

                    url = '{}/controller/restui/policy2/policies/{}'.format(
                        controllerURL, app['id'])
                    headers = {
                        'Content-Type': 'application/json;charset=UTF-8',
                        'Accept': 'application/json,text/plain,*/*',
                        'X-CSRF-TOKEN': token
                    }
                    resp3 = requests.get(url, headers=headers, cookies=cookies)
                    if (resp3.ok):
                        policeList = json.loads(resp3.content)

                        for police in policeList:
                            # if("Tempo de resposta do normal" in police['name']):
                            if("Tempo de resposta do normal" in police['name']):
                                print(police['name'])
                                original = '{"id":27964,"version":7,"name":"Corretor Veloz Forum - Tempo de resposta do normal","nameUnique":true,"applicationId":2674,"affectedEntityDefinitionRule":{"id":1062450,"version":1,"aemcType":"BT_AFFECTED_EMC","componentIds":[],"missingEntities":null,"type":"SPECIFIC","businessTransactionIds":[684982],"nameMatch":null},"type":"BUSINESS_TRANSACTION","description":"Average Response Time (ms) is > 2 : 3 standard deviation of the default baseline and CALLS_PER_MINUTE is > 50 per minute for the last 30 minutes","enabled":true,"critical":{"id":136246,"version":0,"condition":{"id":241426,"version":0,"type":"POLICY_LEAF_CONDITION","metricExpression":{"type":"LEAF_METRIC_EXPRESSION","literalValueExpression":false,"literalValue":0,"metricDefinition":{"type":"LOGICAL_METRIC","logicalMetricName":"95th Percentile Response Time (ms)","scope":null,"metricId":0},"functionType":"VALUE","displayName":"null","inputMetricText":false,"inputMetricPath":"Root||Business Transaction Performance||95th Percentile Response Time (ms)","value":0},"operator":"GREATER_THAN","value":3,"valueUnitType":"BASELINE_STANDARD_DEVIATION","useActiveBaseline":true,"baselineId":0,"conditionExpression":null,"conditionDisplayName":"Average Response Time (ms) > 5000","shortName":"A","conditionValueFunction":null,"entityDefs":[],"metrics":[],"triggerOnNoData":false,"enableTriggers":true,"minTriggers":5},"entityAggregationScope":{"type":"AGGREGATE","value":0},"conditionAggregationType":"ALL","conditionExpression":null},"warning":{"id":136247,"version":0,"condition":{"id":241427,"version":0,"type":"POLICY_LEAF_CONDITION","metricExpression":{"type":"LEAF_METRIC_EXPRESSION","literalValueExpression":false,"literalValue":0,"metricDefinition":{"type":"LOGICAL_METRIC","logicalMetricName":"95th Percentile Response Time (ms)","scope":null,"metricId":0},"functionType":"VALUE","displayName":"null","inputMetricText":false,"inputMetricPath":"Root||Business Transaction Performance||95th Percentile Response Time (ms)","value":0},"operator":"GREATER_THAN","value":2,"valueUnitType":"BASELINE_STANDARD_DEVIATION","useActiveBaseline":true,"baselineId":0,"conditionExpression":null,"conditionDisplayName":"Average Response Time (ms) > 5000","shortName":"A","conditionValueFunction":null,"entityDefs":[],"metrics":[],"triggerOnNoData":false,"enableTriggers":true,"minTriggers":5},"entityAggregationScope":{"type":"AGGREGATE","value":0},"conditionAggregationType":"ALL","conditionExpression":null},"durationInMinutes":10,"waitTimeInMinutes":10,"schedule":39716,"alwaysEnabled":false,"defaultPolicy":true,"createdBy":{"id":2041,"type":"USER","mappedEntityId":"2079","name":"carlos.doki"},"modifiedBy":{"id":2041,"type":"USER","mappedEntityId":"2079","name":"carlos.doki"},"createdOn":null,"modifiedOn":null}'
                                originalJson = json.loads(original)
                                originalJson['id'] = police['id']
                                originalJson['name'] = police['name']
                                originalJson['affectedEntityDefinitionRule']['businessTransactionIds'] = police[
                                    'affectedEntityDefinitionRule']['businessTransactionIds']
                                originalJson['critical']['id'] = police['critical']['id']
                                originalJson['critical']['condition']['id'] = police['critical']['condition']['id']
                                originalJson['warning']['id'] = police['warning']['id']
                                originalJson['warning']['condition']['id'] = police['warning']['condition']['id']

                                data = json.dumps(originalJson)
                                url = '{}/controller/restui/healthRules/update'.format(
                                    controllerURL)
                                headers = {
                                    'Content-Type': 'application/json;charset=UTF-8',
                                    'Accept': 'application/json,text/plain,*/*',
                                    'X-CSRF-TOKEN': token
                                }
                                resp4 = requests.post(
                                    url, headers=headers, data=data, cookies=cookies)

                                if (resp4.ok):
                                    print('HealthRule updated')
                                else:
                                    print(resp4.raise_for_status())
                    else:
                        print(resp3.raise_for_status())
                else:
                    print(resp2.raise_for_status())

    else:
        print(resp.raise_for_status())


if __name__ == "__main__":
    main(sys.argv[1:])
