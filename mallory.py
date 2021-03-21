# Trying SSL with bottle
# ie combo of http://www.piware.de/2011/01/creating-an-https-server-in-python/
# and http://dgtool.blogspot.com/2011/12/ssl-encryption-in-python-bottle.html
# without cherrypy?
# requires ssl

# to create a server certificate, run eg
# openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# DON'T distribute this combined private/public key to clients!
# (see http://www.piware.de/2011/01/creating-an-https-server-in-python/#comment-11380)
from bottle import Bottle, ServerAdapter, route, request, response, template, run, get, post, HTTPResponse


import requests as req
import python_jwt as jwt
import jwcrypto.jwk as jwk
import json

Claims = {}
Claims['iss'] = 'https://sso.sota.org.uk/auth/realms/SOTA'
Claims['typ'] = 'Bearer'
Claims['userID'] = [ 3714, 5156, 11330, 12740, 10245, 5584 ]
Claims['callsign'] = ['G3PYU', 'IZ3GME', 'OE5JFE', 'LU1MAW', 'CT7AOV', 'ON6ZQ']
Claims['realm_access'] =   {'roles': ['sms-remote']}
Claims['azp'] = 'smsremote'


# SOTA keycloak public key
keycloak_pubkey=  b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqiqgMLH8lRVaTep3O0EPbV7NgcmRZYGinOBpVul0VIl56cGPbfVrzVbTongz0SYbliyMkwtc9Lwc03yhtElzaSR1Sck5DevDbUTUva9hw9C9Uz0UaeKzdVBcunpHLT3AQgeFXgA51O+8gcyfok0Cb7NFF6X8Gzx4sdFNNMFdmcaY9G+ByD6SajQ6rfN51kldrmxH/oWLpNFw1XApzJBqLzhwZWmRu7F7L9L6+h42b4MT04mYfnhgG9oAt2iqTWtqq2YVqWuwU+uqYJ2PoLKFeIoyYoA6D+2T5jpj6yGFKwjH+fZxt7HBbwG3M5iKh4PgOJEFZcAvCgYMPUwFn0dyzwIDAQAB\n-----END PUBLIC KEY-----\n'

# make a key from the PEM data
pub_key = jwk.JWK.from_pem(keycloak_pubkey)


# copied from bottle. Only changes are to import ssl and wrap the socket
class SSLWSGIRefServer(ServerAdapter):
    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        import ssl
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
                
            self.options['handler_class'] = QuietHandler

        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket ( srv.socket, certfile='server.pem', server_side=True)
        
        srv.serve_forever()


@get("/spotme")
def spotme():
    print ("\nincoming spot request")
    doit("SPOT")
    
@get('/testme')
def testme():
    print ("\nincoming test request")
    doit()

    
def doit(actionmode = "NOSPOT"):    
    #print("received headers:\n")

    # set up some useful stuff
    auth = False
    headers = {}
    headers_id = {}
    claims = {}
    claims_id ={}
    code = 0
    code_id = 0

    # find the keycloak headers in what we received
    for k, v in request.headers.items():
        #print("key k = ", k)
        #print("val v = ", v)

        if k == 'Authorization':
            # split out the 'Bearer ' from the header, we don't need it
            values= v.split(' ')
            # verify the access_token has wholesomeness
            code, headers, claims = verify_header(values[1], pub_key)

        # we don't use values in the id_token currently but
        # we can check it has wholesomeness anyeay
        if k == 'Id-Token':
            code_id, headersid, claims_id = verify_header(v, pub_key)

    # nothing found
    if code == 0:
        raise HTTPResponse(status=200, body="Quoi?")
    
    # the token is expired
    if code == 401:
        raise HTTPResponse(status=401,
                           body=json.dumps(  { "error": "invalid_token", "error_description": "The access token expired" }),
                           headers={'Content-type': 'application/json', 'WWW-Authenticate': 'Bearer error="invalid_token"  error_description="The access token expired"'} )

    # the token didn't veirfy, missing data or signing wrong
    if code == 400:
        raise HTTPResponse(status=400,
                           body=json.dumps(  { "error": "invalid_token", "error_description": "The access token is malformed or data is wrong" }),
                           headers={'Content-type': 'application/json', 'WWW-Authenticate': 'Bearer error="invalid_token"  error_description="The access token is malformed or data is wrong"'} )

    # the headers are wholesome
    if code == 200:
        # check the user has the right permissions for this access
        if not validate_user(Claims, claims):
            # user is not valid
            raise HTTPResponse(status=400, body="Bad user request")
        
        # here we have valid headers, a permitted user and good stuff
        # get the urlencode data into json 
        d = request.query
        body = {}
        for k, v in d.items():
            #rint(k, v)
            body[k] = v


        # are we spotting or just checking
        body['callsign'] = claims['callsign']
        body['userID'] = claims['userID']
        jbody=json.dumps(body)

        print("request elements:")
        for k,v in body.items():
            print(k,v)

        print("request json:", jbody)
        
        if actionmode == 'SPOT':
            # call the spotter
            apiresp = req.get("http://127.0.0.1:8140/spotmessl", params= body )

            # did it work ok?
            if apiresp.status_code == 200:
                raise HTTPResponse(status=200,  body="spot ok" )
            else:
                raise HTTPResponse(status=400, body=json.dumps( { "error": "spotting error", "error-description": "the spot was rejected" } ) )
        else:
            raise HTTPResponse(status=200, headers={'Content-type': 'application/json'}, body=jbody )
                                

        
def verify_header(header_value, pub_key):

    headers = {}
    claims = {}

    try:
        headers, claims = jwt.verify_jwt(header_value, pub_key, ['RS256'] )
        
        #print("header= ", headers)
        #print("claims= ", claims)
        status = 200
            
    except Exception as e:
        print("DEBUG error type: ", type(e).__name__, "args: ", e.args)
        status = 400
        if type(e).__name__ == '_JWTError':
            print("the error: ", e)
            
            if 'expired' in e.args:
                status = 401
            else:
                status = 400
                

    return status, headers, claims

    
def validate_user(Validclaim, userclaim):

    if Validclaim['iss'] != userclaim['iss']:
        return False
    
    if Validclaim['typ'] != userclaim['typ']:
        return False

    if userclaim['userID'] not in Validclaim['userID']:
        return False
    
    if userclaim['callsign'] not in Validclaim['callsign']:
        return False

    # we may not have a realm_access if it's an odd user
    # trap this and return False if not found
    
    try:
        uc = userclaim['realm_access']
        Vc = Validclaim['realm_access']
    except:
        return False

    #print (set(uc['roles']).intersection( Vc['roles'] ))

    #print ( type( set(uc['roles']).intersection( Vc['roles'] )))
    
    if set(uc['roles']).intersection( Vc['roles'] ) ==set():
        return False
    
    if Validclaim['azp'] != userclaim['azp']:
        return False

    return True

    

srv = SSLWSGIRefServer(host="0.0.0.0", port=8150)
run(server=srv)

 
