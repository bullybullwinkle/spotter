
import smslog
import usercheck
import parsemsg
import api_sota



def processloop( sender, msg, nospot, spotsource, sotapi2):

    #isAPI2 = False
    isAPI2 = True
    
    callsign, features = usercheck.find( sender )
      
    if len(msg) ==0:
        print('Bad format, no data!')
        smslog.log( 'Bad message format, no data' )
        
        return
        
    fstr = 'SOTA'
    if callsign != '':
        # yes, the user is registered
        print('Found: ', callsign)
        if features & 1:
            fstr += '+Hump'
        if features & 2:
            fstr += '+WOTA'
        print('Features:', fstr)
        print('Message: ', msg)


    else:

        index1 = msg.find('dlor.me/')
        index2 = msg.find('inr.ch')
        index3 = msg.find('garmin.com')

        # not Delorme Inreach
        if index1  == -1 and index2 == -1 and index3 == -1:
            # unknown sender
            smslog.log( 'Unknown sender: '+sender )
            # skip the processing
            return
        

        # we have a Delorme Inreach message, find the user
        delorme = 1
        if index1 != -1:
            delorme = index1
        if index2 != -1:
            delorme = index2
        if index3 != -1:
            delorme = index3


        # we have a Delorme Inreach message, find the user
        delormemsg = msg[delorme:]
        if delormemsg.find(' - ') == -1:
            # delorme message looks buggered
            smslog.log( 'Delorme InReach message looks corrupt\n')
            smslog.log( msg )
            # skip further processing
            return

        delormefields = delormemsg.split(' - ')
        sender = delormefields[1].strip()
        callsign, features = usercheck.find( sender )
        if callsign == '':
            # unknown delorme user
            smslog.log( 'Unknown Delorme InReach sender: '+sender)
            # skip further processing
            return
        else:
            # trim Delorme trash off our spot message
            msg = msg[:delorme]
            # check extra features support
            if features & 1:
                fstr += '+Hump'
            if features & 2:
                fstr += '+WOTA'
            print('(Delorme) Found: '+ callsign)
            print('(Delorme) Features:', fstr)
            print('(Delorme) Message: ', msg)
            # overide default spotsource as all Delorme message are from Iridium
            spotsource = 'Iridium'

    # by now we have a valid SMS or Delorm user identified 
                

    formatvalid = False
        
    print("processing message: ")

    status, httpspot, eraseme = parsemsg.parse_SOTA_spot( msg, callsign, isAPI2, spotsource )                
                                            
    # check we got some data
    if status == False:
        # log bum data and do next
        smslog.log( 'Invalid message: ' + msg )
                    
    # data seems good                
    else:
        # handle spots

        if isAPI2==False and eraseme == False:
            # post spot, log results
            httpresp = http_sota.postspotlite( httpspot, True, nospot, spotsource )
            # log badness if spot failed
            if httpresp == 200:
                smslog.log( 'Spotlite does not like the message' )

        else:
            if eraseme == True:
                # post spot using API2
                status, httpresp = api_sota.deletespot( httpspot, nospot, sotapi2, callsign )
            else:
                # post spot using API2
                status, httpresp = api_sota.postspot( httpspot, nospot, sotapi2, callsign )

            # log badness if spot failed
            if status == False:
                smslog.log('Posting/deleting the spot failed, api fail')
                
            else:
                smslog.log( 'api2 likes the message' )
                
                    
            
    return

    
def isspot( message ):
    if message[0] == '!' or message[0] == '%':
        return True
    return False
    
