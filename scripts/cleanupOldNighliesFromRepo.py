import os
import re
import shutil
from distutils.dir_util import copy_tree
from datetime import datetime, timedelta
from collections import defaultdict

#author: Daniel Davison
#this script cleans up the old nightly dev builds and retains only the most recent version
#configure the below root_dir and new_dir to point to the location of your repository

#the directory to scan
root_dir = "C:\\dev\\repository"

#where to copy the repo
new_dir = "C:\\dev\\newRepository"

#dir_count = len([i for i, j, k in os.walk(root_dir)])-1
dir_count = 252799 #to give a progress estimate

#matches our naming scheme for dev builds: e.g. 0.2.7-dev123
re_dev = re.compile(r"((?:\d+\.)+\d+)-dev(\d+)$")

#matches anything else as long as it contains at least a dot (e.g. 0.1 or a.b.rc1)
#this captures all of our release builds and most of the external libs
re_release = re.compile(r"((?:.+\.)+.+)$")

#for occasionally giving a status update of where we are in our processing
processed_count = 0
print_interval = timedelta(seconds = 1)
start_time = datetime.now()
next_print = start_time

#keep track of the release builds and the max dev build number we have encountered for each module
dev_builds = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
release_builds = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
other_files = defaultdict(lambda: defaultdict(lambda: defaultdict(string)))

print("Starting to search for builds in %s" % (root_dir))
for subdir, dirs, files in os.walk(root_dir):
    for dir in dirs:
        processed_count += 1
        
        #the module dir we are in (last part of the subdir)
        mod_dir = os.path.basename(os.path.normpath(subdir))
        
        #check if there is an xml file in this dir that describes the version 
        #-> this tells us that we are at the correct path depth level where we would expect a dev or release to be stored
        #note that this file is not always there, apparently!!
        xml_file = os.path.join(subdir,dir,mod_dir+"-"+dir+".xml")
        
        #check if we're at a dev-build or a regular release build
        dev_dir = re_dev.match(dir)
        release_dir = re_release.match(dir)
        if dev_dir:
            curr_version = dev_dir.group(1)
            curr_devbuild = dev_dir.group(2)
            
            #is this the highest buildnr we've encountered so far??
            if int(curr_devbuild) > int(dev_builds[subdir][curr_version]['devbuild']):
                dev_builds[subdir][curr_version]['devbuild'] = curr_devbuild
                dev_builds[subdir][curr_version]['dir'] = dir

        #check if we're at a path that matches a release build or a different external lib
        elif os.path.isfile(xml_file) or release_dir:
            release_builds[subdir][dir]['dir'] = dir
            #print("Found a non-dev release: %s" % (os.path.join(subdir,dir)))
            
    #check if there are any other files (like licenses for external repos) that we should keep
    #ignore zip, jar and xml files as these are already captured in the dirs gathered above
    for file in files:
        if not file.endswith(".jar") and not file.endswith(".xml") and not file.endswith(".zip"):
            print("Found file: %s" % (os.path.join(subdir, file)))
            other_files[subdir][file] = file
        
    #print some periodic status info
    now = datetime.now()
    if now >= next_print:
        next_print = now + print_interval
        print("Scanning is %.1f%% complete" % (processed_count/dir_count*100), flush=True)
            
print("Finished scanning for dev builds! Processed %s dirs in %s seconds" % (processed_count, (datetime.now() - start_time).total_seconds()))

#construct the list of dirs to copy
movelist = []

for abspath, versions in release_builds.items():
    relpath = abspath[len(root_dir)+1:]
    for version in versions:
        movelist.append(os.path.join(relpath,versions[version]['dir']))
        
for abspath, versions in dev_builds.items():
    relpath = abspath[len(root_dir)+1:]
    for version in versions:
        movelist.append(os.path.join(relpath,versions[version]['dir']))
        
#do the actual copying
for dir in movelist:
    oldDir = os.path.join(root_dir,dir)
    newDir = os.path.join(new_dir, dir)
    print("Copying dir to: %s" % (newDir))
    copy_tree(oldDir, newDir, preserve_mode = 1, preserve_times = 1)

#copy the other remaining files (e.g. licence files)
for abspath, files in other_files.items():
    relpath = abspath[len(root_dir)+1:]
    for file in files:
        oldFile = os.path.join(root_dir,relpath,file)
        newFile = os.path.join(new_dir,relpath,file)
        print("Copying file to: %s" % (newFile))
        if not os.path.exists(os.path.join(new_dir,relpath)):
            os.makedirs(os.path.join(new_dir,relpath))
        shutil.copy2(oldFile,newFile)
