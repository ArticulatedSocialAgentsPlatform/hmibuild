import os
import re
from distutils.dir_util import copy_tree
from datetime import datetime, timedelta
from collections import defaultdict

#author: Daniel Davison
#this script updates all source files with a new open source license agreement blurb
#change root_dir below

#checks whether any of the given list of substrings occurs (at least once) in the given str
def contains_substrings(str, substrings):
    contains = False
    for entry in substrings:
        contains = contains or entry in str
    return contains
    
#opens the file at filepath and strips any existing license notice that may exist at the top of the file, then overwrites the old file
def strip_licenses(filepath, old_licenses):
    fh = open(filepath, "r", newline='')
    content = fh.read()
    fh.close()
    
    for license in old_licenses:
        if license.match(content):
            print("removing license from file %s" %(filepath))
            content = license.sub('', content).lstrip()
            fh = open(filepath, "w", newline='')
            fh.write(content)
            fh.close()
            
#adds the license blurb to the file
def add_license(filepath, licensepath):
    print("adding license to file %s" %(filepath))
    fh = open(filepath, "r", newline='')
    content = fh.read().lstrip()
    fh.close()
    
    fh = open(licensepath, "r", newline='')
    license = fh.read().rstrip()
    fh.close()
    
    content = license + os.linesep + content
    
    fh = open(filepath, "w", newline='')
    fh.write(content)
    fh.close()

#the directory to scan
root_dir = "C:\\dev\\tools\\Flipper-2.0"

#which files to update
#choose from:
# - java
# - xml (not tested yet)
file_type = "java"

#make some settings specific to a filetype
if file_type == "java":
    path_contains = ["\\src\\", "\\test\\"]
    path_excludes = ["\\src-delomboked\\","\\generatedsrc\\","\\HmiFlipper\\"]
    old_licenses = [re.compile(r"\A(/\*)(.|\n[^\*/])*?(Copyright)(.|\n[^\*/])*?(\*/)"),re.compile(r"\A(/\*+)\s*\n*\s*(\*+)/")]
    new_license = "java_license.txt"
elif file_type == "xml":
    path_contains = ["\\resource\\"]
    path_excludes = ["\\src-delomboked\\"]
    old_licenses = [re.compile(r"(<!--)(.|\n)*?(-->)")]
    new_license = "xml_license.txt"
    
processed_count = 0

print("Starting to search for files of type %s in dir %s" % (file_type, root_dir))
for subdir, dirs, files in os.walk(root_dir):
    for file in files:
        fpath = os.path.join(subdir,file)
        if contains_substrings(subdir, path_contains) and not contains_substrings(subdir, path_excludes) and file.endswith("."+file_type):
            processed_count += 1
            strip_licenses(fpath, old_licenses)
            add_license(fpath, new_license)
        
print("Finished scanning for source files of type %s! Processed %s files" % (file_type, processed_count))

