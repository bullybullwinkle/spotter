
import requests as req

import json
import time

#TOKEN_URL = 'https://sso.sota.org.uk/auth/realms/SOTA/protocol/openid-connect/token'
#APIGETSPOTS_URL = 'http://api2.sota.org.uk/api/spots/10/all'
#APIPOSTSPOT_URL = 'http://api2.sota.org.uk/api/spots'

# 0 = uninit
# 1 = tokens fetch

import keycloak as AUTH

    
class SOTA_API(AUTH.SSO_Auth):
    def __init__(self,  URL_token, URL_getspots, URL_postspot, theID):
        AUTH.SSO_Auth.__init__(self, URL_token, theID)

       
        self.URL_getspots = URL_getspots
        self.URL_postspot = URL_postspot

        self.state = 0
        self.newspots = []
        self.filehandle = open('TRACEcall.TXT', 'w')



          

    def postspot(self, spotdata, spottingcall):
        self.filehandle.flush()

        
        finalurl = self.URL_postspot + spottingcall
        print("FINAL URL = " + finalurl)
        
        status, apiresp = self.authorisedpost(finalurl, data=json.dumps(spotdata))
        #print (apiresp.text)
        if (status == False):
            msg = str(time.asctime()) + " " + "API fail postspot"
            print(msg)
            self.filehandle.write(msg+"\n")
            self.filehandle.flush()
            return False, None
        
        if apiresp.status_code == 200:
            # have a valid response here
            msg = str(time.asctime()) + " " +"200 postspot"
            print(msg)
            self.filehandle.write(msg+"\n")
            self.filehandle.flush()

            # call worked, was the spot good?
            # get the response text into a dict
            data = json.loads(apiresp.text)

            postdata={}

            # api call worked and data was accepted
            postdata['id'] = data['id']
            postdata['activatorCallsign'] = data['activatorCallsign']
            postdata['associationCode'] = data['associationCode']
            postdata['summitCode'] = data['summitCode']
            postdata['frequency'] = data['frequency']
            postdata['mode'] = data['mode']
            postdata['comments'] =  data['comments']
                             
            return True, postdata        


        else:
            msg = str(time.asctime()) + '\n' + 'postspot response code: ' + str(apiresp.status_code) + '\npostspot response body: '+ apiresp.text + '\n'
            print( msg)
            self.filehandle.write(msg)
            self.filehandle.flush()
            return False, apiresp


    def apicall_getspots(self):
        self.filehandle.flush()
        resp = {}
        try:
            resp = req.get(self.URL_getspots, headers=self.auth_header, timeout=10.0 )
            status = True
        except:
            status = False
            
        return status, resp


    
    def getspots(self, database):

        # anonymous read OK?
        
        if self.anonread == False:
            # not authorised or refresh exipired
            '''
            if self.state == 0 or time.time() > self.accessexpirestime:
                status = self.doauthorise()
                if status == False:
                    return False

            '''
            status = True            
            if self.state == 0: 
                status = self.doauthorise()
                if status == False:
                    return False
                
            if time.time() > self.accessexpirestime:
                if time.time() > self.refreshexpirestime:
                    status = self.doauthorise()
                else:
                    status = self.refreshtokens()

            if status == False:
                return False
     

        status, apiresp = self.apicall_getspots()
        #print (apiresp.text)
        if status == False:
            msg = str(time.asctime()) + " " + "API failyre getspots"
            print(msg)
            self.filehandle.write(msg)
            return False
        
        if apiresp.status_code == 200:
            # have a valid response here
            self.filehandle.write('Calling json.loads\n')
            items = json.loads(apiresp.text)
            #print(items)
            self.filehandle.write('Calling parseandadditems\n')
            self.updated = self.parseandadditems(items, database)
            self.filehandle.write('fetched spots\n')
            self.filehandle.flush()
            return True        
        else:
            self.state = 0
            msg = 'getspots response code is: ' + str(apiresp.status_code) + '\n'
            print(msg)
            self.filehandle.write(msg+'\n')
            self.filehandle.flush()
            return False

        
    def cleanfreq(self, f):
        # make commas dots for our EU friends
        fmhz = f.replace( ',', '.')
        # fix dot fuckwittery
        fmhz = fmhz.replace('.', '*', 1)
        fmhz = fmhz.replace('.', '')
        fmhz = fmhz.replace('*', '.')
        try:
            fkhz = float(fmhz) * 1000.0
        except:
            fkhz = 0.0

        return(fkhz)
        
    def parseandadditems(self, items, database):
    
        db_updated = False
        for item in items:
            #print ("ITEM")
            #print (item)
            rssid = int(item['id'])


            # **************************
            #
            # code for handling API orphans
            #
            #        if rssid == 206155 or  rssid == 206169 or rssid == 206167 \
            #             or rssid == 206158:
            #            print("orphan in the feed!")
            #            continue
            #
            #************************

            if rssid not in database:
                c = item['activatorCallsign']
                fmhz = item['frequency']
                fkhz = self.cleanfreq(fmhz)
                    
                f = '{:.1f}'.format(fkhz)
                s = item['associationCode'] + '/' + item['summitCode']
                t = self.dxc_get_time(item['timeStamp'])
                p = item['callsign']
                database[ rssid ] = c + ' ' + f + ' ' + s + ' ' + t  + ' ' + p
                db_updated = True

                spot = ( rssid, c, f, s, t, p )
                
                self.newspots.append( spot )
                
                #print ("appending ", rssid)
                #print (database[rssid])
                #print()
                #print( spot )
                #print (self.newspots[rssid])

                    
                #if db_updated == True:
                #    if (queuemode == True):
                #        print("queueing", rssid, database[rssid])
                #        spot_queue(rssid, c, f, s, t, p )
        
        return db_updated

    def getnewspots(self):
        spots = self.newspots
        self.newspots = []
        return spots

    def dxc_get_time(self, item ):
        Tpos = item.find('T')
        Ttime = item[Tpos+1:Tpos+6]
        time_fields = Ttime.split( ':' )
        short_time = time_fields[0] + time_fields[1] + 'Z'
        return short_time



    def apicall_simple(self, URL):
        self.filehandle.flush()

        if self.anonread == False:
            # not authorised or refresh exipired
            '''
            if self.state == 0 or time.time() > self.accessexpirestime:
                status = self.doauthorise()
                if status == False:
                    return False
            '''
            if self.state == 0: 
                status = self.doauthorise()
                if status == False:
                    return False
                
            if time.time() > self.accessexpirestime:
                if time.time() > self.refreshexpirestime:
                    status = self.doauthorise()
                else:
                    status = self.refreshtokens()

            if status == False:
                return False
     
        try:
            resp = req.get(URL, headers=self.auth_header, timeout = 10.0)
            if resp.status_code == 200:
                return True, resp
            else:
                return False, resp
        except:
            return False, None

    
    def apicall_deletespot(self, idval):
        self.filehandle.flush()


        try:
            url = self.URL_postspot + '/' + str(idval)
            resp = req.delete(url, headers=self.auth_header, timeout = 10.0)
            if resp.status_code == 200:
                return True, resp
            else:
                return False, resp

            #print ('response code = ' + str(resp.status_code))
            #print (resp.text)
            if resp.status_code == 200:
                return True, resp
            else:
                return False, resp
        except:
            print("Delete spot api failed\n")
            return False, None
            
    def deletespot(self, spotid):
        if self.anonwrite == False:
            # not authorised or refresh exipired
            '''
            if self.state == 0 or time.time() > self.accessexpirestime:
                status = self.doauthorise()
                if status == False:
                    return False
            '''
            if self.state == 0: 
                status = self.doauthorise()
                if status == False:
                    return False
                
            if time.time() > self.accessexpirestime:
                if time.time() > self.refreshexpirestime:
                    status = self.doauthorise()
                else:
                    status = self.refreshtokens()

            if status == False:
                return False
     
            

        status, apiresp = self.apicall_deletespot(spotid)

        #print (apiresp.text)
        if (status == False):
            msg = str(time.asctime()) + " API fail deletespot"
            print(msg)
            self.filehandle.write(msg+"\n")
            return False, None
        
        if apiresp.status_code == 200:
            # have a valid response here
            msg = str(time.asctime()) + " " + "200 deletespot"
            print(msg)
            self.filehandle.write(msg+"\n")
            self.filehandle.flush()

            postdata = {}
            postdata['statusCode'] = 0
            return True, postdata        
                
        else:
            self.state = 0
            msg = str(time.asctime()) + " " + "deletespot response code is: " + str(apiresp.status_code) + "\n"
            print(msg)
            self.filehandle.write(msg)
            self.filehandle.flush()
            return False, apiresp

