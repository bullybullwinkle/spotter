
import time
import requests as req
import requests.auth as reqauth
import json

#from requests.auth import HTTPBasicAuth

import copy

class SSO_Auth(object):
    def __init__(self,  URL_token, theID):
        self.state = 0
        self.URL_token = URL_token
        self.client_id = theID['client_id']
        self.client_secret = theID['client_secret']
        self.username = theID['username']
        self.password = theID['password']
        self.anonread = theID['anonread']
        self.anonwrite = theID['anonwrite']
        
        self.auth_header = {}
        self.tokens = {}
        self.refreshexpirestime = 0.0
        self.accessexpirestime = 0.0

        self.logstuff = True

        if self.logstuff:
            self.authfile = open('TRACEauth.TXT', 'w')

    '''
    Login to SSO and get the magic tokens needed for API access
    '''
    
    def getkeycloaktokens(self):

        self.tokens = {}
        
        grantdata = {'username': self.username,
                     'password': self.password,
                     'grant_type': 'password',
                     'scope': 'openid'}
        customheader = {'Accept': 'application/json'}
        authdata = reqauth.HTTPBasicAuth(self.client_id, self.client_secret)

        try:
            resp = req.post( self.URL_token,
                             auth=authdata,
                             data=grantdata,
                             headers=customheader,
                             timeout = 10.0)

            self.tokens = resp.json()

            self.auth_header = { 'Content-Type': 'application/json',
                                 'Authorization': 'bearer ' + self.tokens['access_token'],
                                 'id_token': self.tokens['id_token'] }
            

            self.refreshexpirestime = float(self.tokens['refresh_expires_in']) + time.time()
            self.accessexpirestime = float(self.tokens['expires_in']) + time.time()

            self.state = 1
            status = True
        except Exception as ex:
            self.state = 0
            status = False
            self.refreshexpirestime = 0.0
            self.accessexpirestime = 0.0
            template = "getkeycloaktokens: an exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            
            
        return status        


    '''
    Use tokens to refresh expired access token
    '''

    def refreshkeycloaktokens(self):
        grantdata = {'grant_type': 'refresh_token',
                     'client_id': self.client_id,
                     'client_secret': self.client_secret,
                     'refresh_token':  self.tokens['refresh_token']}                     
        
        customheader = {'Accept': 'application/json'}
        authdata = reqauth.HTTPBasicAuth(self.client_id, self.client_secret)
        
        try:
            resp = req.post( self.URL_token,
                             data=grantdata,
                             headers=customheader,
                             auth=authdata,
                             timeout = 10.0)

            self.tokens = resp.json()

            self.auth_header = { 'Content-Type': 'application/json',
                                 'Authorization': 'bearer ' + self.tokens['access_token'],
                                 'id_token': self.tokens['id_token'] }
            
            self.refreshexpirestime = float(self.tokens['refresh_expires_in']) + time.time()
            self.accessexpirestime = float(self.tokens['expires_in']) + time.time()

            status = True
            self.state = 1
        except Exception as ex:
            self.state = 0
            self.refreshexpirestime = 0.0
            self.accessexpirestime = 0.0
            template = "refreshkeycloaktoens: an exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            status = False

        
        return status
    

    '''
    Handle Keycloak authorisation for get and post request
    self.state records whether we have valid tokens or no
    Get tokens from clean or reauthorise depending on expiry time
    '''

    def doauthorise(self):

        msg = str(time.asctime()) + ' AUTHORISING: '
        status = False

      
        # do we have any tokens, if not then get some
        if self.state == 0:
            msg = msg + " clean fetch"
            # authorise yourself
            status = self.getkeycloaktokens()
            if status == False:
                # request failed
                msg = msg + " failed\n"
            else:
                # request succeede
                self.state = 1
                msg = msg + " succeeded\n"

        # we have tokens, has time passed the expire time for the access
        # but not passed the expire time for the refresh
        elif time.time() > self.accessexpirestime and time.time() < self.refreshexpirestime:

            
            self.state = 0
            msg = msg + " stale token refresh"
            # refresh yourself
            status = self.refreshkeycloaktokens()
            if status == False:
                # request failed
                msg = msg + " failed\n"
                self.accessexpirestime = 0
                self.refreshexpirestime = 0
            else:
                # request succeede
                msg = msg + " succeeded\n"
                self.state = 1
            """
            status = True
            print(" testing expired token")
            """
            
            
        # time has passed refresh expiry
        elif time.time() > self.refreshexpirestime:
            self.state = 0
            msg = msg + " refetch token"
            # refresh yourself
            status = self.getkeycloaktokens()
            if status == False:
                # request failed
                msg = msg + " failed\n"
                self.accessexpirestime = 0
                self.refreshexpirestime = 0

            else:
                # request succeede
                msg = msg + " succeeded\n"
                self.state = 1

        # the taccess token is still valid, nothing to do
        elif self.state == 1:
            msg = msg + " still valid\n"
            status = True
        
        #print(msg)
        if self.logstuff:
            self.authfile.write(msg);
            self.authfile.flush()

        return status

    '''
    A wrapper to requests.get that handles Keycloak authorisation
    '''
    
    def authorisedget(self, *args, **kwargs):

        resp ={}
        # anonymous read OK?
        # if not we need to authorise ourselves
        if self.anonread == False:
            status = self.doauthorise()
            if status == False:
                return False, resp 
     

        try:
            resp = req.get(*args, **kwargs, headers = self.auth_header)
            if resp.status_code == 200:
                status = True
            else:
                status = False
            
        except Exception as e:
            status = False
            msg = "Exception authorisedget: "
            print(msg, e)
            if self.logstuff:
                self.authfile.write(msg);
                self.authfile.flush()
            
        return status, resp

    '''
    A wrapper to requests.post that handles Keycloak authorisation
    '''
    

    def authorisedpost(self, *args, **kwargs):
   
        resp ={}
        # anonymous read OK?
        if self.anonwrite == False:
            status = self.doauthorise()
            if status == False:
                return False, resp 
     

        try:
            
            resp = req.post(*args, **kwargs, headers = self.auth_header)
            if resp.status_code == 200:
                status = True
            else:
                status = False

            
        except Exception as e:
            status = False
            msg = "exception authorisedpost: "
            print(msg, e)
            if self.logstuff:
                self.authfile.write(msg);
                self.authfile.flush()
            
        return status, resp

