import http.client, urllib.request, urllib.parse, urllib.error
import smslog

###############################################################################
#
# post a spot to the PorridgeWaste spot server
#
###############################################################################

def posthumpspot( param, spot, nopost ):
    
    summitReference = ""
    summitReference = param[ 'assoc' ]
    summitReference = summitReference + '/'
    summitReference = summitReference + param[ 'summit' ] 
    summitReference = summitReference.upper()
    
    spotparams =  { 'submitSpotButton' : 'Submit spot' }
    spotparams [ 'activationCallsign' ] = param[ 'actCallsign']
    spotparams [ 'summitReference' ] = summitReference
    spotparams [ 'frequency' ] = param[ 'freq' ]
    spotparams [ 'mode' ] = param[ 'mode' ]
    spotparams [ 'comments' ] = param[ 'comments' ]    
    encspotparams = urllib.parse.urlencode( spotparams )
    
    httpheaders = { 
                    "Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain",
                   "User-Agent": "humps-spotter-mm0fmf/0.1"
                   }
    
    if nopost == True:
        print('**NOT** Posting a hump spot with: ')
        print(encspotparams)
        smslog.log(encspotparams)
        smslog.log('HUMPS: posting disabled with nohump')
        retval = 303
        return retval

        retval = 200
    try:        
        conn = http.client.HTTPConnection("www.summitswatch.org.uk")
        conn.request("GET", "/sb/login.php")
        r1 = conn.getresponse()
    
        #print r1.status, r1.reason
        if r1.status != 200:
            return 200
           
        headers = r1.getheaders()
        for header in headers:
            if header[0]=='set-cookie':
                cookie = header[1].split(';')
                #print cookie[0]
                
        httpheaders[ 'Cookie' ] = cookie[0]
    
        body = r1.read()    
        #print loginparams
        #print httpheaders
        
        loginparams = {  'submitted' : 'TRUE',
                    'submit' : 'Login',
                    } 
        loginparams [ 'email' ] = 'mm0fmf_sota@intermoose.com'
        loginparams [ 'pass' ] = 'qwe6787'
        
        encparams = urllib.parse.urlencode( loginparams ) 
    
        conn.request("POST", "/sb/login.php", encparams, httpheaders)
        r1 = conn.getresponse()
        body = r1.read()
        if r1.status != 302:
            conn.close()
            return 200
       
        print('posting a hump spot with:')
        print(encspotparams)
        smslog.log(encspotparams)
        conn.request("POST", "/sb/submitSpot.php", encspotparams, httpheaders)
        r1 = conn.getresponse()
        body = r1.read()
        #print r1.status, r1.reason
        #smslog.log( 'HUMPS: '+str(r1.status) )
        smslog.log( 'HUMPS: {0:d}'.format(r1.status) )


        if r1.status == 302:
            conn.close()
            return 303
    except IOError:
        print('HTTP exception with www.summitswatch.org.uk:80\n')
        smslog.log('HUMPS: IOError, spot deleted')
        return 200

