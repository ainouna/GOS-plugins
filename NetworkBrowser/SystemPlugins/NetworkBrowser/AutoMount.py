# -*- coding: utf-8 -*-
# for localized messages
from Components.LanguageGOS import gosgettext as _
import os
import re
from enigma import eTimer
from Components.Console import Console
from Components.Harddisk import harddiskmanager #global harddiskmanager

XML_FSTAB = "/etc/auto.network"

def rm_rf(d): # only for removing the ipkg stuff from /media/hdd subdirs
    try:
        for path in (os.path.join(d,f) for f in os.listdir(d)):
            if os.path.isdir(path):
                rm_rf(path)
            else:
                os.unlink(path)
        os.rmdir(d)
    except Exception, ex:
        print "AutoMount failed to remove", d, "Error:", ex

class AutoMount():
    """Manages Mounts declared in a XML-Document."""
    def __init__(self):
        self.automounts = {}
        self.activeMountsCounter = 0
        # Initialize Timer
        self.callback = None

        self.getAutoMountPoints()

    def getAutoMountPoints(self, callback = None):
        # Initialize mounts to empty list
        automounts = []
        self.automounts = {}
        self.activeMountsCounter = 0

        if not os.path.exists(XML_FSTAB):
            return
        tree = open(XML_FSTAB, "r").read()

        def getValue(definitions, default):
            # Initialize Output
            ret = ""
            # How many definitions are present
            Len = len(definitions)
            return Len > 0 and definitions[Len-1].text or default
        
        # Config is stored in "mountmanager" element
        for line in tree.split("\n"):
            line = re.sub(' +','\t',line)
            print "LINE", line
            # Read out NFS Mounts
            if "-fstype=nfs" in line or "-fstype=cifs" in line:
                data = { 'isMounted': False, 'active': False, 'ip': False, 'sharename': False, 'sharedir': False, 'username': False, \
                            'password': False, 'mounttype' : False, 'options' : False, 'hdd_replacement' : False }
                try:
                    if "-fstype=nfs" in line:
                        data['mounttype'] = 'nfs'.encode("UTF-8")
                    elif "-fstype=cifs" in line:
                        data['mounttype'] = 'cifs'.encode("UTF-8")
                    if line[0] == "#":
                        line = line[1:]
                        data['active'] = 'False'.encode("UTF-8")
                    else:
                        data['active'] = 'True'.encode("UTF-8")
                    
                    if data["active"] == 'True':
                        self.activeMountsCounter +=1
                    
                    fields = line.split("\t")
                    data['sharename'] = fields[0].encode("UTF-8")
                    
                    data['username'] = 'guest'.encode("UTF-8")
                    data['password'] = ''.encode("UTF-8")
                    data['options'] = ""
                    for option in fields[1].split(","):
                        if option.startswith("-fstype"):
                            continue
                        elif option.startswith("user="):
                            data['username'] = option[5:].encode("UTF-8")
                        elif option.startswith("username="):
                            data['username'] = option[9:].encode("UTF-8")
                        elif option.startswith("pass="):
                            data['password'] = option[5:].encode("UTF-8")
                        elif option.startswith("password="):
                            data['password'] = option[9:].encode("UTF-8")
                        else:
                            data['options'] += option + ","
                    if len(data['options']) > 1:
                        data['options'] = data['options'][:-1]
                    data['options'] = data['options'].encode("UTF-8")
                    
                    
                    if fields[2][:3] == "://": #cifs
                        ip = fields[2][3:].split("/", 1)
                    else:
                        ip = fields[2].split(":/", 1)
                    data['ip'] = ip[0].encode("UTF-8")
                    data['sharedir'] = ip[1].encode("UTF-8")
                    if len(fields) > 3 and fields[3][1:] == "HDD_REPLACEMENT":
                        data['hdd_replacement'] = 'True'.encode("UTF-8")
                    else:
                        data['hdd_replacement'] = 'False'.encode("UTF-8")
                    
                    self.automounts[data['sharename']] = data
                except Exception, e:
                    print "[MountManager] Error reading Mounts:", e

        self.checkList = self.automounts.keys()
        if not self.checkList:
            print "[AutoMount.py] self.automounts without mounts",self.automounts
        else:
            self.CheckMountPoint(self.checkList.pop(), callback)
        
        if callback is not None:
            callback(True)

    def sanitizeOptions(self, origOptions, cifs=False):
        options = origOptions.strip()
        if not options:
            options = 'rsize=8192,wsize=8192'
            if not cifs:
                options += ',tcp'
        else:
            if 'rsize' not in options:
                options += ',rsize=8192'
            if 'wsize' not in options:
                options += ',wsize=8192'
            if not cifs and 'tcp' not in options and 'udp' not in options:
                options += ',tcp'
        return options

    def CheckMountPoint(self, item, callback):
        data = self.automounts[item]
        self.CheckMountPointFinished(None,None, [data, callback])

    def CheckMountPointFinished(self, result, retval, extra_args):
        print "[AutoMount.py] CheckMountPointFinished",result,retval
        (data, callback ) = extra_args
        path = os.path.join('/media/net', data['sharename'])
        if self.automounts.has_key(data['sharename']):
            self.automounts[data['sharename']]['isMounted'] = True
            desc = data['sharename']
            if self.automounts[data['sharename']]['hdd_replacement'] == 'True': #hdd replacement hack
                self.makeHDDlink(path)
            harddiskmanager.addMountedPartition(path, desc)
        if self.checkList:
            # Go to next item in list...
            self.CheckMountPoint(self.checkList.pop(), callback)

    def makeHDDlink(self, path):
        hdd_dir = '/media/hdd'
        print "[AutoMount.py] symlink %s %s" % (path, hdd_dir)
        if os.path.islink(hdd_dir):
            if os.readlink(hdd_dir) != path:
                os.remove(hdd_dir)
                os.symlink(path, hdd_dir)
        elif os.path.ismount(hdd_dir) is False:
            if os.path.isdir(hdd_dir):
                rm_rf(hdd_dir)
        try:
            os.symlink(path, hdd_dir)
        except OSError, ex:
            print "[AutoMount.py] add symlink fails!", ex
        movie = os.path.join(hdd_dir, 'movie')
        if not os.path.exists(movie):
            try:
                os.mkdir(movie)
            except Exception, ex:
                print "[AutoMount.py] Failed to create ", movie, "Error:", ex

    def getMountsList(self):
        return self.automounts

    def getMountsAttribute(self, mountpoint, attribute):
        if self.automounts.has_key(mountpoint):
            if self.automounts[mountpoint].has_key(attribute):
                return self.automounts[mountpoint][attribute]
        return None

    def setMountsAttribute(self, mountpoint, attribute, value):
        if self.automounts.has_key(mountpoint):
            self.automounts[mountpoint][attribute] = value

    def writeMountsConfig(self):
        # Generate List in RAM
        list = ['# automatically generated by enigma 2\n']
        for sharename, sharedata in self.automounts.items():
            print "SHARE", sharedata
            if sharedata['active'] is False:
                list.append('#')
            list.append(sharedata['sharename'])
            list.append('\t')
            list.append('-fstype=' + sharedata['mounttype'])
            list.append("," + sharedata['options'])
            if sharedata['mounttype'] == 'cifs':
                list.append(",username=" + sharedata['username'])
                list.append(",password=" + sharedata['password'])
            list.append('\t')
            if sharedata['mounttype'] == 'cifs':
                list.append("://")
            list.append(sharedata['ip'])
            if sharedata['mounttype'] == 'nfs':
                list.append(":/")
            elif sharedata['mounttype'] == 'cifs':
                list.append("/")
            list.append(sharedata['sharedir'])
            if sharedata['hdd_replacement']:
                list.append('\t#HDD_REPLACEMENT')
            list.append('\n')
        
        # Try Saving to Flash
        try:
            open(XML_FSTAB, "w").writelines(list)
        except Exception, e:
            print "[AutoMount.py] Error Saving Mounts List:", e

    def removeMount(self, mountpoint, callback = None):
        print "[AutoMount.py] removing mount: ",mountpoint
        self.newautomounts = {}
        for sharename, sharedata in self.automounts.items():
            if sharename is not mountpoint.strip():
                print "[AutoMount.py]",sharedata
                self.newautomounts[sharename] = sharedata
        self.automounts.clear()
        self.automounts = self.newautomounts
        print "[AutoMount.py] removeMount done"

iAutoMount = AutoMount()
