#requires winrandom+Crypto installation

import datetime
import argparse
import paramiko
import getpass
import os

def createXML(org, module, revision):
  today = datetime.datetime.now()
  f = open(module+"-"+revision+".xml", "w")
  f.write('<ivy-module version="2.0">\n')
  f.write('<info organisation="' + org + '" module="'+ module + '" revision="'+revision+'" status="release" publication="'+str(today.year)+str(today.month).zfill(2)
  +str(today.day).zfill(2)+str(today.hour).zfill(2)+str(today.minute).zfill(2)+str(today.second).zfill(2)+'"/>\n')  
  f.write('</ivy-module>\n')
  f.close()

def rexists(sftp, path):
    """os.path.exists for paramiko's SCP object
    """
    try:
        sftp.stat(path)
    except IOError, e:
        if e[0] == 2:
            return False
        raise
    else:
        return True

def mkdirifnotexists(sftp, path):
  if not rexists(sftp,path):
    sftp.mkdir(path)

def getFileName(path):
  splitpath = path.split('/')
  splitpath = splitpath[len(splitpath)-1].split('\\')
  return splitpath[len(splitpath)-1]
      
def publishAtScp(host, user, key, org, module, revision, jarfile):
  transport = paramiko.Transport((host,22))
  transport.connect(username=user, pkey=key)
  #transport.connect(username=user, password=passw)
  
  sftp = paramiko.SFTPClient.from_transport(transport)
  
  mkdirifnotexists(sftp,'/hmirepo/external/java/'+org)
  mkdirifnotexists(sftp,'/hmirepo/external/java/'+org+'/'+module)
  sftp.mkdir('/hmirepo/external/java/'+org+'/'+module+'/'+revision)
  sftp.mkdir('/hmirepo/external/java/'+org+'/'+module+'/'+revision+'/lib')
  sftp.put(module+"-"+revision+".xml",'/hmirepo/external/java/'+org+'/'+module+'/'+revision+'/'+module+"-"+revision+".xml")
  sftp.put(jarfile,'/hmirepo/external/java/'+org+'/'+module+'/'+revision+'/lib/'+getFileName(jarfile))
  sftp.close()
  transport.close()

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version")
parser.add_argument("-m", "--module")
parser.add_argument("-o", "--org")
parser.add_argument("--host")
parser.add_argument("--user")
parser.add_argument("jar")
args = parser.parse_args()
if args.host.find('@') >= 0:
  username, hostname = args.host.split('@')
else:
  hostname = args.host
  username = args.user
path = os.path.expanduser('~/.ssh/id_rsa')
key = paramiko.RSAKey.from_private_key_file(path)
#if not key:
#  password = getpass.getpass('Password for %s@%s: ' % (username, hostname))  

createXML(args.org, args.module, args.version)
publishAtScp(hostname, username, key, args.org, args.module, args.version, args.jar)
