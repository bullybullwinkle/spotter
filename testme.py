import ssoapi

import time

TOKEN_URL = 'https://sso.sota.org.uk/auth/realms/SOTA/protocol/openid-connect/token'
API_GETSPOTS_URL = 'http://api2.sota.org.uk/api/spots/10/all'
API_POSTSPOT_URL = 'http://api2.sota.org.uk/api/spots'
#API_POSTSPOT_URL = 'http://elgur.crabdance.com/api/spots:8140'

#MyAPI = ssoapi.SOTA_api(TOKEN_URL,
#                        API_GETSPOTS_URL,
#                        API_POSTSPOT_URL)







myID = {}
myID['client_id'] = 'sms'
myID['client_secret'] = 'daa79960-1119-4849-bbdf-ceb67a03de58'
#myID['username'] = 'mm0fmf'
#myID['password'] = 'price8smart'
myID['username'] = 'SMS'
myID['password'] = '023416CRvt'


MyAPI = ssoapi.SOTA_API(TOKEN_URL, API_GETSPOTS_URL, API_POSTSPOT_URL, myID)

myspotdata = {
    'associationCode': 'GM',
    'summitCode': 'WS-001',
    'activatorCallsign': 'TESTCALL',
    'frequency': '14.0625',
    'mode': 'cw',
    'comments': 'test-ignore',
}

postreply = '''
{"statusCode":"0000","result":{"id":264501,"timeStamp":"2019-01-09T21:32:09.6152538+00:00","summitId":2463.0,"associationCode":"GM","summitCode":"WS-001","callsign":"mm0fmf","activatorCallsign":"GS3PYU","activatorName":"","frequency":"14.0625","mode":"cw","summitDetails":"Ben Nevis, 1344m, 10 Point(s)","comments":"test-ignore","freqDecimal":14.0625},"response":none,"mode":none}
'''


testreply = '''
{"statusCode":"0000","result":{"id":264787,"timeStamp":"2019-01-11T19:38:43.632401+00:00","summitId":2463.0,"associationCode":"GM","summitCode":"WS-001","callsign":"sms","activatorCallsign":"TESTCALL","activatorName":null,"frequency":"14.0625","mode":"cw","summitDetails":"Ben Nevis, 1344m, 10 Point(s)","comments":"test-ignore","freqDecimal":14.0625},"response":null,"mode":null}
'''

import json

if __name__ == '__main__':


    '''
    data = json.loads(testreply) #, sort_keys=True, indent=4)
    print (type (data))
    print (data)

    #print("\n\n\n")
    #datadict = dict(data)
    #print (type(datadict))
    #print (datadict)
    

    ok = False
    for p_id, p_info in data.items(): #postreply.items():
        #print (p_id)
        #print (p_info)        

        if p_id == 'statusCode':
            print("statuscode = " + p_info)
            if p_info == 0:
                ok = True
                
        elif p_id == 'result':
            print ("result = ")
            print ("id = " + str(p_info['id']))
            print ("activator = " + p_info['activatorCallsign'])
            print ("association = " + p_info['associationCode'])
            print ("summit = " + p_info['summitCode'])
            print ("frequency = " + p_info['frequency'])
            print ("mode = " + p_info['mode'])
            print ("comments = " + p_info['comments'])
            
    '''
                
    
    
    # post a test spot
    status, reply = MyAPI.postspot(myspotdata)

    if status == True:
        # call worked, was the spot good?
        print ("spot data returns\n")
        print (reply)
        
        
        
    else:
        print("spot failed\n");
        
    
    print("\n\n\nlet's delete the fucker....\n")

    status, reply = MyAPI.deletespot( reply['id'] )
    #status, reply = MyAPI.deletespot( 12345678 )

    print ("delete status + " + str(status) )
    print ("reply data\n")
    print (reply)
    
    '''
    count = 2
    #while (count < 3):
    while (True):
        database = {}
        status = MyAPI.getspots(False, database)
        if status == True:
            print (database)
            print("\n\n\n\n")
            for item in MyAPI.newspots:
                print (item)
                print()

                MyAPI.newspots =[]
            
        else:
            print("failure\n\n")

        time.sleep(5)
        count = count + 1

        status = MyAPI.refreshtokens()
        print("refresh status")
        print(status)

    database = {}
    print ("try again....\n\n\n")
    status = MyAPI.getspots(False, database)
    print (status)
    for item in MyAPI.newspots:
        print (item)
        print()

    MyAPI.newspots =[]

    
#    status = MyAPI.postspot(myspotdata)
#    print (status)

    
    '''
