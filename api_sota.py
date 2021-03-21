
import ssoapi
import json
import smslog
import random

posted_spots = {}

def spotlite2api2( oldspot):
    spot = {}        
    spot['activatorCallsign'] = oldspot[ 'actCallsign' ]
    spot['associationCode'] = oldspot[ 'assoc' ]
    spot['summitCode'] = oldspot[ 'summit' ]
    spot['frequency'] = oldspot[ 'freq' ] 
    spot['mode'] = oldspot[ 'mode' ]
    spot['comments'] = oldspot[ 'comments' ]

    return spot
    

def deletespot( param, nopost, api, spottingcall):

    spotdata = spotlite2api2( param )

    foundkey = False
    
    # dont post if the nopost flag is set

    if nopost == True:
        print('**NOT** Deleting a spot with: ')

        for key,value in posted_spots.items():
            oldspot = dict(value)
            if oldspot == spotdata:
                del posted_spots[key]
                print ("delete spot backtrace dictionary has " + str(len(posted_spots)) + " entries")
                message = ''.join("Deleted spot: " + str(key))
                print(message)
                print(spotdata)
                smslog.log(message)
                smslog.log(json.dumps(spotdata))
                foundkey=True
                break;

        if foundkey == False:
            message = "No matching spot found"
            print(message)
            smslog.log(message+"\n")
            
        thing = {}
        thing ['statusCode'] = 0
        return True, thing

    print('deleting a spot with: ')
    
    for key,value in posted_spots.items():
        oldspot = dict(value)
        if oldspot == spotdata:
            foundkey = True
            status, reply = api.deletespot(key)
            if status == False:
                print("api2 call failed")
                smslog.log("api2 call failed")
                return status, reply
            if reply['statusCode'] == 0:
                print("api2 liked the delete")
                smslog.log("api2 liked the delete")
                del posted_spots[key]
                print ("delete spot backtrace dictionary has " + str(len(posted_spots)) + " entries")
                message = ''.join("Deleted spot: " + str(key))
                print(message)
                print(spotdata)
                smslog.log(message)
                smslog.log(json.dumps(spotdata))                
                return status, reply
            else:
                print("api2 did not like the delete")
                smslog.log("api2 did not like the delete")
                return status, reply
                   
        if foundkey==False:
            message = "No matching spot found"
            print(message)
            smslog.log(message+"\n")
            return False, None

def postspot( param, nopost, api, spottingcall):

    spotdata = spotlite2api2( param )
    
    # dont post if the nopost flag is set
    if nopost == True:
        print('**NOT** Posting a spot with: ')
        print(spotdata)
        smslog.log(json.dumps(spotdata))
        smslog.log( 'SPOTLITE: posting disabled with nospot')
        thing = {}
        thing ['statusCode'] = 0
        posted_spots[random.randint(1, 9999999)] = spotdata
        print ("delete spot backtrace dictionary has " + str(len(posted_spots)) + " entries")
        print( posted_spots)
        return True, thing

    print('Posting a spot with: ')
    print(spotdata)
    smslog.log(json.dumps(spotdata))
    msg = "\nclient=sms&user="+spottingcall+"\n"
    smslog.log(msg)

    status, reply = api.postspot(spotdata, spottingcall)
    if status == False:
        msg = "api2 call failed"
        print(msg)
        smslog.log(msg+"\n")
        return status, reply

    
    
    posted_spots[reply['id']] = spotdata
    print ("delete spot backtrace dictionary has " + str(len(posted_spots)) + " entries")
    msg = "api2 liked the spot"
    print(msg)
    smslog.log(msg+"\n")
    return status, reply

