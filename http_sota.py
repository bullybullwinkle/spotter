import http.client, urllib.request, urllib.parse, urllib.error
import smslog


###############################################################################
#
# post a spot to the lovely Spotlite system
#
###############################################################################    
        
def postspotlite( param, spot, nopost, spotter):

    # dont post if the nopost flag is set
    if nopost == True:
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}        
        partial_spotdata = urllib.parse.urlencode( param )
        print('**NOT** Posting a spot with: ')
        print(partial_spotdata)
        smslog.log(partial_spotdata)
        smslog.log( 'SPOTLITE: posting disabled with nospot')
        retval = 303
        return retval
    
    if spot == True:        
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}        
        partial_spotdata = urllib.parse.urlencode( param )
        print('Posting a spot with: ')
        print(partial_spotdata)
        smslog.log(partial_spotdata)

        if spotter == 'VK': #'SMS_AUS':
            param[ 'callsign' ] = 'SMS_AUS'
            param[ 'password' ] = '113$4Xp'
        elif spotter == 'GB': #'SMS':
            param[ 'callsign' ] = 'SMS'
            param[ 'password' ] = '025748'
        elif spotter == 'SAT': #'Iridium':
            param[ 'callsign' ] = 'Iridium'
            param[ 'password' ] = 'sbd9602'
        elif spotter == 'NA': #'SMS_NA':
            param[ 'callsign' ] = 'SMS_NA'
            param[ 'password' ] = '078259'
        elif spotter == 'OE': #'SMS_OE':
            param[ 'callsign' ] = 'SMS_OE'
            param[ 'password' ] = 'XL5$Joe90'

        param[ 'submit' ] = 'SPOT!'
        spotdata = urllib.parse.urlencode( param )

        retval = 200
        try:
#            conn = http.client.HTTPConnection("www.sota.org.uk:80")
            conn = http.client.HTTPConnection("old.sota.org.uk:80")
            conn.request("POST", "/Spotlite/postSpot", spotdata, headers)
            response = conn.getresponse()                 
            data = response.read()
            conn.close()    
            #smslog.log( 'SPOTLITE: '+str(response.status) + '\n' + data)
            smslog.log( 'SPOTLITE: {0:d}\n{1}'.format(response.status, data.decode('utf-8')))
            retval = response.status

        except IOError:
#            print('HTTP IOError exception with www.sota.org.uk:80\n')
            print('HTTP IOError exception with old.sota.org.uk:80\n')
            smslog.log( 'SPOTLITE: IOError, spot deleted')
            
    # not a spot, it's an alert and we support them yet
    else:
        print('Alerting with: ' + 'NOT YET')

    return retval
    
