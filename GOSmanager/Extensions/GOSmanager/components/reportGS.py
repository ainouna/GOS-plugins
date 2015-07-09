import ftplib
import os
import sys
import traceback
import base64

print "Files:", sys.argv[1:]

print "Logging in..."
#http://www.base64encode.org/

#ftp = ftplib.FTP(base64.b64decode("ftp.drivehq.com"), base64.b64decode("hybridpli") , base64.b64decode("GOSmgr112014")) #ftp.drivehq.com hybridpli GOSmgr112014
ftp = ftplib.FTP(base64.b64decode("ZnRwLmRyaXZlaHEuY29t"), base64.b64decode("aHlicmlkcGxp") , base64.b64decode("R09TbWdyMTEyMDE0")) #ftp.drivehq.com hybridpli GOSmgr112014
#print ftp.getwelcome()
try:
    try:
        #print "Currently in:", ftp.pwd()
        ftp.cwd(base64.b64decode("R09TLUdT")) #GOS-GS 
        # move to the desired upload directory
        #print "Currently in:", ftp.pwd()

        print "Uploading...",
        fullname = sys.argv[1]
        name = os.path.split(fullname)[1]
        f = open(fullname, "rb")
        ftp.storbinary('STOR ' + name, f)
        f.close()
        print "OK"
        os.remove(fullname)
    finally:
        print "Quitting..."
        ftp.quit()
except:
    traceback.print_exc()
#raw_input("Press Enter...")