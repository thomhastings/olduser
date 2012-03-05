#!/usr/bin/env python
import os
import sys
import time
import datetime

print "Old User Program v1.0"
print "(c) Thom Hastings 2012 BSD License"
print "designed for Rocks 5.4.3 - 5.2"

# Print usage if system argument is --help or -h or -?
try:
    if str(sys.argv[1]) == '--help' or str(sys.argv[1]) == '-h' or str(sys.argv[1]) == '-?':
        print "\nusage:\t" + str(sys.argv[0]) + " [#ofDaysAgo]\t\tdisplays users who haven't\n\t\t\t\t\tlogged in in X days and asks\n\t\t\t\t\tif you want to disable them"
        print "\t" + str(sys.argv[0]) + " [-? -h --help]\tdisplays this help message"
        sys.exit()
except IndexError:
    pass

# Take #ofDaysAgo from system argument or input
#try:
try:
    daysago = int(sys.argv[1])
except IndexError:
    print "\nusage: " + str(sys.argv[0]) + " [#ofDaysAgo]"
    print
    print "No system argument detected..."
    while True:
        try:
            daysago = int(raw_input("How many days ago? [int]: "))
            break
        except ValueError:
            print "Must enter an integer"
#except KeyboardInterrupt:
#    print "\nGoodbye!"
#    sys.exit()

# Clean up from last time just in case
try:    # Stifle output if possible
    os.system("rm .users.txt >/dev/null 2>&1")
except OSError:
    pass

# Create a (hidden) text file containing users, last logins from 'finger', UIDs, and info from lastlog
os.system("whoami >> .users.txt")
os.system("echo 'Users:' >> .users.txt")
os.system("finger `sort /etc/passwd | cut -f1 -d':'` | egrep -i 'log|on since' | sed '/Directory/d' | awk '{gsub(/Login: /,\"\")}; 1' | awk '{gsub(/Name: .*/,\"\")}; 1' | sed 's/[ \t]*$//' >> .users.txt")
os.system("echo >> .users.txt")
os.system("echo 'UIDs:' >> .users.txt")
os.system("cat /etc/passwd | sort | awk -F ':' '{print $3}' >> .users.txt")
os.system("echo >> .users.txt")
os.system("echo 'Lastlog:' >> .users.txt")
os.system("lastlog | sed '/Username/d' | tr -s ' ' | sort >> .users.txt")
os.system("echo >> .users.txt")
os.system("echo 'Shells:' >> .users.txt")
os.system("finger `sort /etc/passwd | cut -f1 -d':'` | egrep -i 'shell' | awk '{gsub(/Directory: [A-Za-z -()]*/,\"\")}; 1' | tr -d '\t' | awk '{gsub(/Shell: /,\"\")}; 1' >> .users.txt")
os.system("echo >> .users.txt")

# Declare some lists we'll need later
users = []
times = []
uids = []
lastlog = []
shells = []
disabled = []
usertimes = []
currentusers = []
oldusers = []
disabledusers = []

# Parse text file into lists
usersfile = open(".users.txt", "r")
line = usersfile.readline()
currentuser = line.strip('\n')
while line:
    if line == "Users:\n":
        line = usersfile.readline().strip('\n')
        user = True
        while line:
            if user:
                users.append(line)
            line = usersfile.readline().strip('\n')
            if line:
                user = ((line.split()[0] != "On") and (line.split()[0] != "Last") and (line.split()[0] != "Never"))
            if not user:
                times.append(line)
                while line and not user:
                    line = usersfile.readline().strip('\n')
                    if line:
                        user = ((line.split()[0] != "On") and (line.split()[0] != "Last") and (line.split()[0] != "Never"))
    if line == "UIDs:\n":
        line = usersfile.readline().strip('\n')
        while line:
            uids.append(line)
            line = usersfile.readline().strip('\n')
    if line == "Lastlog:\n":
        line = usersfile.readline().strip('\n')
        while line:
            lastlog.append(line)
            line = usersfile.readline().strip('\n')
    if line == "Shells:\n":
        line = usersfile.readline().strip('\n')
        while line:
            shells.append(line)
            line = usersfile.readline().strip('\n')
    line = usersfile.readline()

### CLUSTER ONLY ### user nfsnobody shows up in /etc/passwd but not lastlog, must reconcile:
try:
    del uids[users.index('nfsnobody')]
    del times[users.index('nfsnobody')]
    del shells[users.index('nfsnobody')]
    users.remove('nfsnobody')
except:
    pass

for shell in shells:    # Make simpler list of bools disabled[] from shells[]
    if shell.split()[len(shell.split())-1] == '/sbin/nologin' or shell == '/bin/false' or shell == '/dev/null':
        disabled.append(True)
    else:
        disabled.append(False)

current_day = datetime.datetime.today().day
current_time = datetime.datetime.today()
print "\nCurrent Time:\t" + str(current_time) + "\tCurrent Day:\t" + str(current_day)

target_day = current_day - daysago
target_time = current_time - datetime.timedelta(daysago)
print "Target Time:\t" + str(target_time) + "\tTarget Day:\t" + str(target_day)

target_time_delta = datetime.timedelta(daysago)
print "\t\t\t\t\t\tTime Delta:\t" + str(target_time_delta)

# Creates a list of datetime objects corresponding to all users
i = 0
while i < len(times):
    if len(times[i].split()) > 0:
        if times[i].split()[0] == "On" or users[i] == currentuser:
            times[i] = 'Currently logged in.'
            usertimes.append(datetime.datetime.now())
            usertimes[i] = usertimes[i].replace(microsecond=0)
        elif times[i].split()[0] == "Last":
            usertimes.append(datetime.datetime(*time.strptime(' '.join(times[i].split()[2:6]), "%a %b %d %H:%M")[0:6]))
            try:
                if len(lastlog[i].split()) > 8:   #If length > 8, then lastlog has IPs
                    usertimes[i] = usertimes[i].replace(year=int(lastlog[i].split()[8]))    #We are on cluster
                else:   #We are not on cluster
                    usertimes[i] = usertimes[i].replace(year=int(lastlog[i].split()[7]))
            except IndexError:
                pass
        elif times[i].split()[0] == "Never":
            usertimes.append(datetime.datetime(1900,1,1))   #If user has never logged in, they are from 1900
    i = i+1

# Creates two lists of old and current users, disregarding system users
i = 0
while i < len(users):
    try:
        time_delta = current_time - usertimes[i]
        if time_delta >= target_time_delta:
            if int(uids[i]) >= 500 and int(uids[i]) <= 65535 and users[i] != 'nobody':
                if disabled[i] == False:
                    oldusers.append(users[i])
                else:
                    disabledusers.append(users[i])
        else:
            if int(uids[i]) >= 500 and int(uids[i]) <= 65535 and users[i] != 'nobody':
                if disabled[i] == False:
                    currentusers.append(users[i])
                else:
                    disabledusers.append(users[i])
    except ValueError:
        if int(uids[i]) >= 500 and int(uids[i]) <= 65535 and users[i] != 'nobody':
            if disabled[i] == False:
                oldusers.append(users[i])
            else:
                disabledusers.append(users[i])
    except IndexError:
        pass
    i = i+1

showdisabled = True
print
#try:
while True:
    try:
        ask = raw_input("Show disabled users? [y/n]: ")
        if ask == 'n' or ask == "N" or ask == "no":
            showdisabled = False
            break
        elif ask == 'y' or ask == "Y" or ask == "yes":
            showdisabled = True
            break
        else:
            raise TypeError("Must enter (y/n)")
    except TypeError:
        print "Must enter (y/n)"
#except KeyboardInterrupt:
#    print "\nGoodbye!"
#    sys.exit()

# Some useful output
if showdisabled == True:
    print "\nUsers:\t\tUIDs:\tDisabled:\tParsed datetime:\tLast login:"
    i = 0
    while i < len(users):
        try:
            if int(uids[i]) >= 500 and int(uids[i]) <= 65535 and users[i] != 'nobody':
                print users[i].ljust(12) + "\t" + uids[i] + "\t" + str(disabled[i]) + "\t\t" + str(usertimes[i]) + "\t" + times[i] + " " + str(usertimes[i].year)
        except IndexError:
            pass
        i = i+1
else:
    print "\nUsers:\t\tUIDs:\tParsed datetime:\tLast login:"
    i = 0
    while i < len(users):
        try:
            if int(uids[i]) >= 500 and int(uids[i]) <= 65535 and users[i] != 'nobody' and disabled[i] == False:
                print users[i].ljust(12) + "\t" + uids[i] + "\t" + str(usertimes[i]) + "\t" + times[i] + " " + str(usertimes[i].year)
        except IndexError:
            pass
        i = i+1

print "\nCurrent Users:"
i = 0
while i < len(currentusers):
    print currentusers[i]
    i = i+1

print "\nOld Users:"
i = 0
while i < len(oldusers):
    print oldusers[i]
    i = i+1

print
#try:
while True:
    try:
        ask = raw_input("Do you want to disable old users? (requires root) [y/n]: ")
        if ask == 'n' or ask == "N" or ask == "no":
            pass
            break
        elif ask == 'y' or ask == "Y" or ask == "yes":
            for olduser in oldusers:
                ask = raw_input("Disable account \'" + olduser + "\'? [y/n]: ")
                if ask == 'y' or ask == "Y" or ask == "yes":
                    print "Disabling account (" + olduser + ")..."
                    os.system("su -c '/usr/sbin/usermod -s /sbin/nologin " + olduser + "'")
                elif ask == 'n' or ask == "N" or ask == "no":
                    pass
                    break
                else:
                    raise TypeError("Must enter (y/n)")
            print "To re-enable a user, use \"su -c '/usr/sbin/usermod -s /bin/bash USERNAME'\"."
            break
        else:
            raise TypeError("Must enter (y/n)")
    except TypeError:
        print "Must enter (y/n)"
#except KeyboardInterrupt:
#    print "\nGoodbye!"
#    sys.exit()

#Clean up ### COMMENT OUT THE FOLLOWING LINE FOR DEBUG INFO ###
os.system("rm .users.txt")

print "\nDONE"
