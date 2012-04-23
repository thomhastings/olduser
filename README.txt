As an admin for a Rocks cluster I wrote a script to help clean out old users.
I wrote this script in Python 2.4, tested on Rocks 5.4.3 and 5.2.

I have been given permission to release this script under a BSD license.
Grab it here: https://github.com/thomhastings/olduser/blob/master/olduser.py

Example usage:

[hastint@rocks64 ~]$ python olduser.py -h
Old User Program v1.0
(c) Thom Hastings 2012 BSD License
designed for Rocks 5.4.3 - 5.2

usage:  olduser.py [#ofDaysAgo]		displays users who haven't
					logged in in X days and asks
					if you want to disable them
        olduser.py [-? -h --help]       displays this help message

The script disables users via usermod, 
simply changing their login shell to /bin/nologin, 
so they can easily be re-enabled.

About me:
http://turing.slu.edu/~hastint/