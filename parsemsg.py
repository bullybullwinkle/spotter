
import smslog

NUM_SOTA_FIELDS = 6
NUM_HUMP_FIELDS = 6
NUM_WOTA_FIELDS = 5


###############################################################################
#
# used to parse the incoming data payload into the components of a sota spot
#
# string message: the data payload from the SMS
# string spottercall: the callsign matched from the incoming SMS number
#
###############################################################################

sota_CALL = 0
sota_ASSOC = 1
sota_REF = 2
sota_FREQ = 3
sota_MODE = 4
sota_COMMENT = 5

def parse_SOTA_spot( message, spottercall, isAPI2, spotsource ):

    message.strip()

    pepperspot = message.find( '-DS09a)' )
    if pepperspot != -1:
        pepperspot = pepperspot * -1
        message = message[1:-pepperspot]

    pepperspot = message.find( '-DS1f)' )
    if pepperspot != -1:
        pepperspot = pepperspot * -1
        message = message[1:-pepperspot]

    if spottercall == 'MM0FMF':
        pepperspot = message.find( 'via DroidSpot' )
        if pepperspot != -1:
            pepperspot = pepperspot * -1
            message = message[0:-pepperspot]
            print ('DroidSpot removed:\n'+message)

        pepperspot = message.find( '#DroidSpot' )
        if pepperspot != -1:
            pepperspot = pepperspot * -1
            message = message[0:-pepperspot]
            print ('DroidSpot removed:\n'+message)

    fields = message.split(' ')
    # user may have entered multiple spaces, use list comprehension to remove any
    # null entries in the list of keywords after we split on space
    fields = [i for i in fields if i != '']

    # create dict with all bad entries
    spot = allbadspot()       
    
    # check we have at least 6 fields of data        
    # well we should have 6 fields but we dont need a comment field 
    # so we accept 5

    if len(fields) < NUM_SOTA_FIELDS-1:
        #tstr = 'Bad format: only '+str(len(fields))+' fields in message' 
        tstr = 'Bad format: only {0:d} fields in message'.format(len(fields))
        smslog.log( tstr )
        spot['actCallsign'] = spottercall
        smslog.badspot(spot, 'data')
        print(tstr)
        return None        
        
    # create some vars (because we are a C programmer at heart)
    callsign = ''
    assoc = ''
    summit = ''
    freq = ''
    mode = ''
    comment = ''
    isfullcall = False
    status = False

    
    # cleanup call, add /p etc.
    callsign, isfullcall, eraseme = proc_spot_callsign( fields[sota_CALL].upper(), spottercall )

    # extract association
    assoc = fields[sota_ASSOC].upper()
     
    if isfullcall == False:
        # uk regionalise the callsign
        callsign = uk_localise( callsign, assoc )
        
    # fill in dict with parsed data
    spot['actCallsign'] = callsign
    spot['assoc'] = assoc

    # extract summit and check is SOTA format
    summit = proc_spot_SOTA_summit( fields[sota_REF].upper() )

    if summit == None:
        # log it for status
        smslog.badspot( spot, 'summit')
        return False, None, False

    # fill in dict with parsed data
    spot['summit'] = summit

    # extract freq
    freq = proc_spot_freq( fields[sota_FREQ].upper() )

    # if freq is bogus, fail now
    if freq == None:
        smslog.badspot( spot, 'freq')
        return False, None, False

    # fill in dict with parsed data
    spot['freq'] = freq

    # extract mode and cleanup
    mode = proc_spot_mode( fields[sota_MODE].lower() )
    
    # build comment
    if isAPI2  == True:
        comment = proc_spot_api2comment( spottercall, fields, sota_COMMENT, spotsource )
    else:
        comment = proc_spot_comment( spottercall, fields, sota_COMMENT )


    # finally assemble all components into a spot string
#    spot = {}        
#    spot[ 'actCallsign' ] = callsign
#    spot[ 'assoc' ] = assoc
#    spot[ 'summit' ] = summit
#    spot[ 'freq' ] = freq
    spot[ 'mode' ] = mode
    spot[ 'comments' ] = comment
   
    return True, spot, eraseme

def allbadspot():
    spot = {}        
    spot[ 'actCallsign' ] = 'bad'
    spot[ 'assoc' ] = 'bad'
    spot[ 'summit' ] = 'bad'
    spot[ 'freq' ] = 'bad'
    spot[ 'mode' ] = 'bad'
    spot[ 'comments' ] = 'bad'
   
    return spot

###############################################################################
#
# make callsign from spottercall etc.
#
###############################################################################

def proc_spot_callsign ( callsign, spottercall ):



    callsign = callsign.lstrip()
    
    # if first char is 1 or % or $ then this is a spot
    # if first char is a # then this is a delete
    # else it's a given callsign and if if ends with . then dont append /p

    # delete spot
    delete = False
    if callsign[0] =='#' or callsign[0]=='@':
        callsign =callsign[1:]
        delete = True
                       
    noeditcall = False
    # are we using autocallsign completion with autoappend?
    if callsign[0]=='!' or callsign[0]=='%':
        # insert real call and append /p
        callsign = spottercall+'/P'
    # are we use autocallsign completion with no append?
    elif callsign[0]=='$':
        callsign = spottercall
    # are we using given callsign with no append
    elif callsign[-1:] == '.':
        callsign = callsign[:-1]
        noeditcall = True
        pass
    else:
        noeditcall = True
        # check if we have a /p at the end
        print("callsign ", callsign, "ends with ", callsign[-2:])
        if callsign[-2:] != '/P':
            callsign += '/P'

    return callsign, noeditcall, delete

###############################################################################
#
# check summit meets spec for SOTA summit (catch whummits here)
#
###############################################################################

def proc_spot_SOTA_summit( tsummit ):

    # only want 1st 2 chars for SOTA
    summit = tsummit[0:2]
    # if no - in the original then add one
    if tsummit[2:3] != '-':
        summit += '-'
        summit += tsummit[2:]
    else:
        summit = tsummit

    # check summit is right length        
    if len(summit) != 6:
        tstr = 'SOTA summit len not 6 '+summit+' '+tsummit
        smslog.log( tstr )
        print(tstr)
        return None

        
    return summit

###############################################################################
#
# check freq contains . : , and convert to . check only numbers either side
#
###############################################################################

def proc_spot_freq( freq ):
    # check we have a . or a : or a , in the string
    dotpos = freq.find('.')
    colpos = freq.find(':')
    commapos = freq.find(',')
    if dotpos == -1 and colpos == -1 and commapos == -1:
        tstr = 'no . or : or , in freq '+freq
        smslog.log( tstr )
        print(tstr)
        return None

    if colpos != -1:
        dotpos = colpos
        freq = freq.replace( ':', '.' )
        tstr = 'replaced : with .'
        smslog.log( tstr );
        print(tstr)
    
    if commapos != -1:
        dotpos = commapos
        freq = freq.replace( ',', '.' )
        tstr = 'replaced , with .'
        smslog.log( tstr );
        print(tstr)
       
    # check digits before .
    if freq[0:dotpos].isdigit() == False:
        tstr = 'before . is not digit '+freq
        print(tstr)
        smslog.log( tstr )
        return None

    #check digits after .
    if freq[dotpos+1:].isdigit() == False:
        tstr = 'after . is not digit '+freq
        print(tstr)
        smslog.log( tstr )
        return None
        
    # if here freq looks ok
    return freq

###############################################################################
#
# check mode is in valid list else replace with other
#
###############################################################################

def proc_spot_mode( inmode ):
    # valid modes
    modes = [ "am", "cw", "data", "dv", "fm", "psk", "rtty", "ssb", "other" ]
    valid = False

    mode = inmode.replace('\n', '')
    # check mode is valid string
    for validmode in range(len(modes)):
        if mode == modes[validmode]:
            valid = True
            break
    # mode is invalid, set it to other 
    if valid == False:
        tstr = 'mode not valid '+mode+' using other instead'
        print(tstr)
        smslog.log( tstr )
        mode = 'other'

    return mode

###############################################################################
#
# assemble comment string
#
###############################################################################

def proc_spot_comment( spottercall, fields, comment_field ):

    # build up comment with standard opening
    comment = 'Spot[' + spottercall+']: '
    
    # now add in all pish user provided
    for n in range ( len(fields) - comment_field ):
        comment += fields[n+comment_field]+' '
        
    return comment

def proc_spot_api2comment( spottercall, fields, comment_field, spotsource ):

    # build up comment with standard opening
    comment = '[' + spottercall+'{'+spotsource +'}]: '
    
    # now add in all pish user provided
    for n in range ( len(fields) - comment_field ):
        comment += fields[n+comment_field]+' '
        
    return comment


def uk_localise( callsign, assoc ):
    assocs = [ 'GM','GW','GI','GD','G' ]
    region = [ 'M',  'W', 'I', 'D', 'E' ]
    clubregion = [ 'S','C','N','T','X' ]
    bclub = False
    bgcall = False
    b2call = False

    # IL call?
    if callsign[0:1] == '2':
        b2call = True
    # G or M call?
    elif callsign[0:1] == 'G' or callsign[0:1] == 'M':
        bgcall = True
    else:
        # this is not a UK callsign
        return callsign

    for clubsecondary in clubregion:
        if clubsecondary == callsign[1:2]:
            bclub = True
            print('Club call')
            clubindex = clubregion.index(clubsecondary)
            break;
    # check if uk call in uk region
    for tassoc in assocs:
        if tassoc == assoc:
            # we are in a localisable region
            index = assocs.index(tassoc)
            # copy 1st char
            localised = callsign[0:1]

            if bclub == True:
                #print 'uk club callsign in ',tassoc
                # club call, 2nd char is clubregion
                localised += clubregion[index]
                # club call always has a secondary locator
                # so rest of call starts at 2: not 1:
                localised += callsign[2:]
            else:
                # england has no secondary locator
                if index == 4:
                    # IL call?
                    if b2call == True:
                        #print 'uk IL callsign in ',tassoc
                        # but england does have secondary if IL call
                        localised += region[index]
                        # IL call always has a secondary locator
                        # so rest of call starts at 2:
                        localised += callsign[2:]
                    else:
                        #print 'uk callsign in ',tassoc
                        # english call in england
                        if callsign[1:2].isdigit() == True:
                            # just copy whats left
                            localised += callsign[1:]
                        else:
                             # uk regional, number starts at 2:
                             localised += callsign[2:]
                else:
                    # in a region with secondary
                    localised += region[index]
                    # english call in england
                    if callsign[1:2].isdigit() == True:
                        # just copy whats left
                        localised += callsign[1:]
                    else:
                         # uk regional, number starts at 2:
                         localised += callsign[2:]

            break
        else:
            #print 'uk callsign but not in ',tassoc
            localised = callsign

    smslog.log( 'callsign: '+callsign+' assoc: '+assoc+' localised: '+localised)
    return localised
    

def detardcomment( fields, length ):

    # must have commas in comment, 'tard :-(
    length -= 7;
    tstr = fields[6]+','
    for xx in range(length-1):
        tstr += fields[7+xx]+','
        fields[7+xx] = ''

    return tstr




