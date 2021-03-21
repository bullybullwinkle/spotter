import http.client, urllib.request, urllib.parse, urllib.error
import smslog


    


wotahttpheaders = { "Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain",
               "User-Agent": "wotarator-mm0fmf/0.1" }

wotaconn = http.client.HTTPConnection("www.wota.org.uk")

###############################################################################
#
# connect to the wummits server
#
###############################################################################

def wota_connect():
    wotaconn.request("GET", "/")
    r1 = wotaconn.getresponse()
    #print r1.status, r1.reason
    if r1.status != 200:
        return False
        
    headers = r1.getheaders()
    
    for header in headers:
        if header[0]=='set-cookie':
            cookie = header[1].split(';')
            #print cookie[0]
            
    wotahttpheaders[ 'Cookie' ] = cookie[0]
    
    #print loginparams
    #print wotahttpheaders
    return True
    
###############################################################################
#
# login to the wummits server
#
###############################################################################

def wota_login( name, password ):    

    params = {  'mact' : 'FrontEndUsers,m4,do_login,1',
                'm4returnid' : 19,
                'page' : 19,
                'm4submit' : 'Sign in' 
                } 

    params [ 'm4feu_input_username' ] = name
    params [ 'm4feu_input_password' ] = password
    
    encparams = urllib.parse.urlencode( params ) 

    wotaconn.request("POST", "/nm_login.html", encparams, wotahttpheaders)
    r1 = wotaconn.getresponse()
    if r1.status == 302:
        return True
    
    return False

    #print r1.status, r1.reason
    #headers = r1.getheaders()
    
    #for header in headers:
        #print header

#logged_by=g4zlp&date1=2011-06-13&date1_dp=1&date1_year_start=1981&date1_year_end=2041&date1_day=13&date1_month=06&date1_year=2011&call_used=test&summit=152&call=test+3+ignore+


###############################################################################
#
# post wummit spot (needs login, connect cookie pish)
#
###############################################################################

def postwotaspot( param, spot, nowota ):
    
    wotaparam ={}
    wotaparam[ 'posted_by' ] = 'mm0fmf'
    summit = param[ 'summit' ].split('-')
    if summit[0].find('LDW') != -1:
        wotaparam [ 'summit' ] = summit[1]
    else:
        wotaparam [ 'summit' ] = str( int(summit[1]) + 214 )
    
    wotaparam[ 'call' ] = param[ 'actCallsign' ]
    wotaparam[ 'freqmode' ] = param[ 'freq'] + '+' + param[ 'mode' ]
    wotaparam[ 'comment' ] = param[ 'comments' ]

    # dont post if the nopost flag is set
    if nowota == True:
        partial_spotdata = urllib.parse.urlencode( wotaparam )
        print('**NOT** Posting a spot with: ')
        print(partial_spotdata)
        smslog.log(partial_spotdata)
        smslog.log( 'WOTA: posting disabled with nowota')
        retval = 303
        return retval
    
    if spot == True:        
        spotdata = urllib.parse.urlencode( wotaparam )
        print('Posting a spot with: ')
        print(spotdata)
        smslog.log(spotdata)
        retval = 200
        try:
            smslog.log('WOTA: connect')
            if wota_connect() == False:
                tstr = "Cannot connect to wota.org.uk:80\n"
                print(tstr)
                smslog.log( 'WOTA: '+tstr )
                retval = 404
                return retval
            smslog.log('WOTA: login')
            if wota_login( "mm0fmf", "earlgrey100" ) == False:
                tstr = "Cannot login to wota.org.uk:80\n"
                print(tstr)
                smslog.log( 'WOTA: '+tstr )
                retval = 404
                return retval

            #print "wotaconn.request..."
#            wotaconn.request("POST", "/index.php?page=mm_home/mm_sendspot.html", spotdata, wotahttpheaders)
            wotaconn.request("POST", "/index.php?page=mm_home/mm_sendspotnoaprs.html", spotdata, wotahttpheaders)
            #print "wotaconn.getresponse..."
            r1 = wotaconn.getresponse()
            #print "wotaconn.close..."
            wotaconn.close()
            #print "done"
            #print r1.status, r1.reason
            if r1.status == 200:
                #smslog.log( 'WOTA: '+str(r1.status) + ' is good')
                smslog.log( 'WOTA: {0:d} is good'.format(r1.status) )
                return 200

        except IOError:
            print('HTTP IOError exception with www.wota.org.uk:80\n')
            smslog.log( 'WOTA: IOError, spot deleted')
            
    # not a spot, it's an alert and we support them yet
    else:
        print('Alerting with: ' + 'NOT YET')

    return retval
    
def postchase( chase, user ):
    params =  { 'date1_dp' : 1,
                'date1_year_start' : 1981,
                'date1_year_end' : 2041
                }

    params [ 'logged_by' ] = chase[1]
    params [ 'date1' ] = chase[2]
    date = chase[2].split('-')
    params [ 'date1_day' ] = date[2]
    params [ 'date1_month' ] = date[1]
    params [ 'date1_year' ] = date[0]
    params [ 'call_used' ] = chase[1]
    # pull number from summit
    summit = chase[0].split('-')
    # LDW-xxx use xxx
    if summit[0].find('LDW') != -1:
        params [ 'summit' ] = summit[1]
    else:
        params [ 'summit' ] = str( int(summit[1]) + 214 )
    params [ 'call' ] = chase[3]

    encparams = urllib.parse.urlencode( params )

#    print params
#    print encparams
#    return True

    wotaconn.request("POST", "/mm_home/mm_logcontact.html", encparams, wotahttpheaders)
    r1 = wotaconn.getresponse()
    print(r1.status, r1.reason)
    if r1.status == 200:
        return True

    return False

