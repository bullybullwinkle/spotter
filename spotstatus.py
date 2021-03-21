
import pickle
import time, datetime

from bottle import route, run

def getTime():
    if time.localtime().tm_isdst == 1:
        delta = datetime.timedelta(hours=1 )
    else:
        delta = datetime.timedelta(hours=0)

    return datetime.datetime.now() - delta

@route('/spotstatus/:name')
def spotstatus(name):

    uname = name.title()
    uname = uname.upper()
    mytime = getTime()

    page = '<font face="Arial, Garamond">'
    page = page + '<h1>Spots status for %s at ' % uname
    page = page + mytime.strftime('%a %b %d %H:%M:%S %Y') + ' UTC'
    page = page + '</h1><br><br>'

    page = page + '<table border="1">'
    page = page + '<tr>'
    page = page + '<th> &nbsp;Date / Time&nbsp;</th>'
    page = page + '<th> &nbsp;Callsign&nbsp;</th>'
    page = page + '<th> &nbsp;Ref&nbsp;</th>'
    page = page + '<th> &nbsp;Frequency MHz&nbsp;</th>'
    page = page + '<th> &nbsp;Mode&nbsp;</th>'
    page = page + '<th> &nbsp;Comments&nbsp;</th>'
    page = page + '</tr>'



    if tlock != None:
        tlock.acquire()
    database = {}
    try:
        myfile = open("/home/andy/sms-devel/SPOTS.PCK", 'r')
        database = pickle.load(myfile)
        myfile.close()
    except:
        page = page + '<br><br><br>done.'
        if tlock != None:
            tlock.release()        
        return page


    for k,v in database.items():
#        print k,v

        comments = v[6]
        mode = v[5]
        freq = v[4]
        summit = v[3]
        assoc = v[2]
        call = v[1]
        time = v[0]
        if call.find(uname) != -1 or uname == "ALL":
            page = page + '<tr>' + \
                '<td>&nbsp;' + time.strftime('%a %b %d %H:%M:%S %Y') + '</td>' + \
                '<td>&nbsp;' + call + '</td>' + \
                '<td>&nbsp;' + assoc + '/' + summit + '</td>' + \
                '<td>&nbsp;' + freq + '</td>' + \
                '<td>&nbsp;' + mode + '</td>' + \
                '<td>&nbsp;' + comments + '</td>'
            page = page + '</tr>'

        else:
            pass

    page = page + '</table>'
    page = page + '<br><br><br>done.'
    if tlock != None:
        tlock.release()                    
    return page

def statusServer( mylock, myhost, myport):
   
    global tlock
    tlock = mylock
    run( host='10.1.0.4', port=8000)


if __name__ == '__main__':
    statusServer( None, '10.1.0.4', 8000 )

