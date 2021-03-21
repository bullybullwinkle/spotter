
USERSFILE = 'userdata'
DELORMEFILE = 'delormedata'

def find( number ):
    f = open( USERSFILE, 'r')

    #print 'searching for ',number
    for line in f:
        if len(line) < 10:
            break
        userfields = line.split(',')
        usercall = userfields[0]
        usernumber = userfields[1].strip()
        extras = 0
        if len(userfields) > 2:
            if userfields[2].find('H') != -1:
                extras = 1
            if userfields[2].find('W') != -1:
                extras |= 2

        #print ('checking ' + usercall + ' ' + usernumber + ' for : ' + number)
        if usernumber == number:
            #print (usercall, usernumber, "matches ", number)
            spottercall = usercall
            return usercall.upper(), extras

    return '', 0
    
def delormefind( ident ):
    f = open( DELORMEFILE, 'r')

    #print 'searching for ',number
    for line in f:
        if len(line) < 10:
            break
        userfields = line.split(',')
        usercall = userfields[0]
        userident = userfields[1].strip()
        extras = 0
        if len(userfields) > 2:
            if userfields[2].find('H') != -1:
                extras = 1
            if userfields[2].find('W') != -1:
                extras |= 2

        #print 'checking ', usercall, usernumber, 'for : ', number
        if userident == ident:
            #print usercall, usernumber, "matches ", number
            spottercall = usercall
            return usercall.upper(), extras

    return '', 0
