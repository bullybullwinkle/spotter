
import time, os
import datetime
import pickle

debug = False

def dbg( message ):
    if debug == True:
        print(message)

def loginit( logfilename, debug ):
    print ("logging to " + logfilename)
    global logfile
    logfile = open( logfilename, 'a+' )
    if debug == True:
        log( "*~*~*~*~*~*~*~* DEBUG MODE *~*~*~*~*~*~*~*")
        log( "*~*~*~*~*~*~*~* DEBUG MODE *~*~*~*~*~*~*~*")
        log( "*~*~*~*~*~*~*~* DEBUG MODE *~*~*~*~*~*~*~*")
    return 
    
    

def log( msg ):
    dolog( msg, logfile )
    return
    
def dolog( msg, filehandle ):
    filehandle.write( time.asctime() + ": " )
    filehandle.write( msg +'\n' )
    #print msg
    return
    
def logflush():
    logfile.flush()
    os.fsync(logfile.fileno())
    return
    
def logclose():
    logfile.close()
    return
    

#
# used to limit age of items in database to something easily changed
#
def timelimit( database, timenow ):

    print("aging the data")
    # set the database age to 2 days
    timedelta = datetime.timedelta(days= 2)
    # uncomment this to test age values
    #use magictime to hold the time "now". You can add timedelta
    # onto this value for testing as it artificially ages all
    # values by timedelta

    #magictime = timenow + timedelta
    magictime = timenow

    # a blank database
    limited = {}
    # loop through existing database
    newkey = 0
    for k,v in database.items():
        #print magictime, v[0],magictime-v[0]

        # check if the record is too old
        if magictime - v[0] > timedelta:
            #print k,v
            #print (magictime-v[0])
            #print "timedelta exceeds max age allowed, deleting..."
            pass
        else:
            # copy record into new database
            #print k, v, newkey
            limited[newkey] = v
            newkey = newkey+1

    # return the new database
    return limited

PICKLE = 'SPOTS.PCK'

def badspot( spots, fail):
    print("badspot")
    print("badspot")
    print("badspot")
    print(spots)

    goodspot( spots, 302 )
    return

def goodspot( spots, success ):

    # start with something clean
    spotsDatabase = {}
    # unpickle

    # agelimit time
    if time.localtime().tm_isdst == 1:
        delta = datetime.timedelta(hours=1)
    else:
        delta = datetime.timedelta(hours=0)

    timenow = datetime.datetime.now() - delta

    #lock.acquire()
    try:
        myfile = open( PICKLE, 'rb')
        spotsDatabase = pickle.load(myfile)
        myfile.close()
        # delete all spots older than our limit
        spotsDatabase = timelimit (spotsDatabase, timenow)
        # resize the database
        last = len(spotsDatabase)

    except:
        last = 1

    # create a tuple of data
    # -datetime.timedelta(seconds=172740), \
    details = timenow, \
        spots['actCallsign'], \
        spots['assoc'], \
        spots['summit'], \
        spots['freq'], \
        spots['mode'], \
        spots['comments']
#, \
#        spots['success']

    # add it to the database
    spotsDatabase[last] = details
    # pickle it
    myfile = open(PICKLE, 'wb')
    pickle.dump( spotsDatabase, myfile)
    myfile.flush()
    os.fsync(myfile.fileno())
    myfile.close()
    #lock.release()
    return

