#!/usr/bin/env python
# coding: utf-8

'''
POP Eraser

Delete only old emails in the spool file of the POP3 server.

Copyright 2013, Miyoshi Lab. Kochi Univ.
Licensed under the MIT license.
'''

__author__ = 'Yasuo Miyoshi'
__copyright__ = 'Copyright 2013, Miyoshi Lab., Kochi Univ.'
__credits__ = ['Yasuo Miyoshi']
__license__ = 'MIT'
__version__ = '0.0.1'

import sys
import poplib
import datetime
import dateutil.parser
import pytz
import re
from optparse import OptionParser, OptionGroup
import getpass

def receivedDates(messageLines):
    '''Get received datetimes from the email header.
    
    Keyword arguments:
    messageLines -- array of the message lines of the email
    
    Returns: array of datetime objects
    '''
    dates = []
    line = ''
    for m in messageLines:
        if re.match('Received:', m):
            line = m
            continue
        if line:
            if re.search('\s', m[0]):
                line += m
            else:
                result = re.search(';\s*(.*)', line)
                if result:
                    date = dateutil.parser.parse(result.group(1))
                    if not date.tzinfo:
                        date = pytz.utc.localize(date)
                    date = date.astimezone(pytz.utc)
                    dates.append(date)
                line = ''
    return dates

def latestDate(dates, verbose=False):
    '''Return the latest datetime from the array of datetime values.
    
    Keyword arguments:
    dates -- array of datetime objects
    verbose -- if True, shows all datetimes
               if False (default), shows nothing
    
    Returns: datetime objects
    '''
    if verbose:
        print '----------------'
        print dates
    
    n = len(dates)
    if n < 1: return None
    latest = dates[0]
    for i in range(n-1):
        if latest < dates[i+1]:
            latest = dates[i+1]
    return latest

def popErase(days, user, pw, host, ssl=True, port=None, verbose=False, force=False, noexec=False):
    '''Delete old emails in the spool file of the POP3 server.
    
    Keyword arguments:
    days -- how many days to save the emails which arrived by
    user -- POP3 username
    pw -- user's POP3 password
    host -- POP3 server's hostname or IP address
    ssl -- if True (default), use SSL connection
           if False, not use SSL connection
    port -- POP3 server's port number
            if None (default), the standard port is used
    verbose -- if True, shows more detail
               if False (default), shows only warning message
    force -- if True, deletes forcibly email that received time is unknown
             if False (default), saves email that received time is unknown
    noexec -- if True, prevents actually deleting email (for test)
              if False (default), deletes email actually
    '''
    if ssl:
        if port: p = poplib.POP3_SSL(host, port)
        else: p = poplib.POP3_SSL(host)
    else:
        if port: p = poplib.POP3(host, port)
        else: p = poplib.POP3(host)
    p.user(user)
    p.pass_(pw)
    
    now = pytz.utc.localize(datetime.datetime.utcnow())
    expire = now - datetime.timedelta(days=days)
    num = len(p.list()[1])
    if verbose:
        print 'Present Time:', now
        print 'Expire Time:', expire
        if num < 1: print 'Your email is not found in the spool.'
        else:
            s = 's were' if num > 1 else ' was'
            print '%d email%s found in the spool.' % (num, s)
    for i in range(num):
        dates = receivedDates(p.top(i+1, 1)[1])
        latest = latestDate(dates, verbose)
        if latest:
            if verbose: print ' Received at', latest
            if latest < expire:
                if not noexec: p.dele(i+1)
                if verbose: print '  - delete'
            elif verbose: print '  - save'
        else:
            print ' [Warning] unknown received time'
            if force:
                if not noexec: p.dele(i+1)
                print '  - force delete'
            else:
                print '  - save (use -f option if you want to delete it)'
    p.quit()

if __name__ == '__main__':
    opt = OptionParser(version=__version__)
    opt.add_option('--host', help='POP3 server\'s hostname or IP address (default: localhost)')
    opt.add_option('--port', type='int', help='POP3 server\'s port number (default: None)')
    opt.add_option('-s', '--ssl', action='store_true', default=False, help='use SSL connection')
    opt.add_option('-u', '--user', help='POP3 user name (default: %s)' % (getpass.getuser(),))
    opt.add_option('-p', '--pass', dest='password',
        help='user\'s POP3 password (if not specified, prompt you for the password)')
    opt.add_option('-d', '--days', type='int',
        help='set how many days to save the emails which arrived by (default: 14)')
    opt.add_option('-f', '--force', action='store_true',
        help='this option deletes forcibly email that received time is unknown')
    opt.add_option('-n', '--noexec', action='store_true',
        help='this option is for test, and prevents actually deleting email')
    opt.add_option('-v', '--verbose', action='store_true', help='set verbose mode')
#     opt.add_option('-v', action='store_true', dest='verbose',
#         help='set verbose mode (this option is also available in debugging test examples by doctest)')
#     group = OptionGroup(opt, "Debug Options")
#     group.add_option('-t', '--doctest', action='store_true',
#         help='test examples in docstrings by doctest')
#     opt.add_option_group(group)
    
    (opts, args) = opt.parse_args()
    
#     if opts.doctest:
#         import doctest
#         doctest.testmod()
#         sys.exit(0)
    
    settings = {}
    
    if opts.host: settings.setdefault('host', opts.host)
    if opts.port: settings.setdefault('port', opts.port)
    if opts.ssl: settings.setdefault('ssl', opts.ssl)
    if opts.user: settings.setdefault('user', opts.user)
    if opts.password: settings.setdefault('pass', opts.password)
    else: settings.setdefault('pass', getpass.getpass())
    if opts.days >= 0: settings.setdefault('days', opts.days)
    if opts.verbose: settings.setdefault('verbose', opts.verbose)
    if opts.force: settings.setdefault('force', opts.force)
    if opts.noexec: settings.setdefault('noexec', opts.noexec)
    
    popErase(
        settings.get('days', 14),
        settings.get('user', getpass.getuser()),
        settings.get('pass', ''),
        settings.get('host', 'localhost'),
        settings.get('ssl', False),
        settings.get('port', None),
        settings.get('verbose', False),
        settings.get('force', False),
        settings.get('noexec', False)
    )
    sys.exit(0)

