import sys
import os
import jprops
import re
from xml.etree import ElementTree
from xml.dom import minidom
import argparse

from eclipseutils import *

def getJarFileSet(dir):
  files = set()
  if os.path.isdir(dir):
    files = set(os.listdir(dir))
    files = filter(lambda x: x.endswith('.jar'),files)
  return files

def getLibraries():
  """ get all .jar files in lib and test/lib
  """
  files = set(getJarFileSet(BASE_DIR+'/lib'))
  testfiles = set(getJarFileSet(BASE_DIR+'/test/lib'))
  testfiles -= files;
  files = map(lambda x: 'lib/'+x,files)
  testfiles = map(lambda x: 'test/lib/'+x,testfiles)
  return files+testfiles

def getDependencies():
  with open(BASE_DIR+'/build.properties') as fp:
    properties = jprops.load_properties(fp)
    dependencies = ""
    depprojectnames = set()
    if properties.has_key('rebuild.list'):
      dependencies = properties['rebuild.list']
      dependencies = dependencies.split(',');  
      dependencies = map(lambda x: x.strip(), dependencies)
      dependencies = filter(lambda x: len(x)>0, dependencies)
      
      for dep in dependencies:
        depprojectnames.add(getProjectNameFromDir(SHARED_PATH+"/"+dep))
    return depprojectnames
    
def getResources():
  with open(BASE_DIR+'/build.properties') as fp:
    properties = jprops.load_properties(fp)
    resources = ""
    if properties.has_key('resource.path'):
      resources = properties['resource.path']
    if properties.has_key('test.resource.path'):
      resources = resources+';'+properties['test.resource.path']
    resources = resources.split(';');    
    resources = map(lambda x: x.replace('${shared.resources}',SHARED_RES), resources)
    resources = map(lambda x: x.replace('${asap.resources}',ASAPSHARED_RES), resources)
    resources = map(lambda x: x.replace('${shared.project.root}',SHARED_PATH), resources)
    resources = map(lambda x: x.strip(), resources)
    resources = filter(lambda x: len(x)>0, resources)
    resources = set(resources)
    return resources

def getProjectNameFromDir(dir):
   tree = ElementTree.parse(dir+'/build.xml')
   projectElem = tree.getroot()
   return projectElem.attrib['name']

def getProjectName():
    return getProjectNameFromDir(BASE_DIR)

def writeDotProject():
  with open(BASE_DIR+'/build.properties') as fp:
    properties = jprops.load_properties(fp)
    if properties.has_key('build_target') and properties['build_target'] == 'android':
      projectFile = 'defaultandroidproject'
    else:
      projectFile = 'defaultproject'
    fdefaultProject = open(SHARED_PATH+'/hmibuild/eclipse/'+projectFile,'r')
    content = fdefaultProject.read();
    content = content.replace("$name$", getProjectName());
    fproject = open(BASE_DIR+'/.project', 'w')
    fproject.write(content)
    fproject.close()

def writeClassPath():
  with open(BASE_DIR+'/build.properties') as fp:
    root = ElementTree.Element("classpath")
    properties = jprops.load_properties(fp)
    if properties.has_key('build_target') and properties['build_target'] == 'android':
      cpEntry = ElementTree.SubElement(root,"classpathentry")
      cpEntry.attrib["exported"]="true"
      cpEntry.attrib["kind"]="con"
      cpEntry.attrib["path"]="com.android.ide.eclipse.adt.ANDROID_FRAMEWORK"
      
      cpEntry = ElementTree.SubElement(root,"classpathentry")
      cpEntry.attrib["exported"]="true"
      cpEntry.attrib["kind"]="con"
      cpEntry.attrib["path"]="com.android.ide.eclipse.adt.LIBRARIES"
      
      cpEntry = ElementTree.SubElement(root,"classpathentry")
      cpEntry.attrib["exported"]="true"
      cpEntry.attrib["kind"]="con"
      cpEntry.attrib["path"]="com.android.ide.eclipse.adt.DEPENDENCIES"
        
    if os.path.isdir(BASE_DIR+'/src'):
      cpEntry = ElementTree.SubElement(root,"classpathentry")
      cpEntry.attrib["kind"]="src"
      cpEntry.attrib["path"]="src"

    if os.path.isdir(BASE_DIR+'/generatedsrc'):
      cpEntry = ElementTree.SubElement(root,"classpathentry")
      cpEntry.attrib["kind"]="src"
      cpEntry.attrib["path"]="generatedsrc"
    
    if os.path.isdir(BASE_DIR+'/gen'):
      cpEntry = ElementTree.SubElement(root,"classpathentry")
      cpEntry.attrib["kind"]="src"
      cpEntry.attrib["path"]="gen"
  
    if os.path.isdir(BASE_DIR+'/test/src'):
      cpEntry = ElementTree.SubElement(root,"classpathentry")
      cpEntry.attrib["kind"]="src"
      cpEntry.attrib["path"]="test/src"
  
    cpEntry = ElementTree.SubElement(root,"classpathentry")
    cpEntry.attrib["kind"]="con"
    cpEntry.attrib["path"]="org.eclipse.jdt.launching.JRE_CONTAINER"
  
    cpEntry = ElementTree.SubElement(root,"classpathentry")
    cpEntry.attrib["kind"]="output"
    cpEntry.attrib["path"]="build/classes"
    
    if os.path.isdir(BASE_DIR+'/resource'):
      cpEntry = ElementTree.SubElement(root,"classpathentry")
      cpEntry.attrib["kind"]="lib"
      cpEntry.attrib["path"]="resource"
  
    if os.path.isdir(BASE_DIR+'/test/resource'):
      cpEntry = ElementTree.SubElement(root,"classpathentry")
      cpEntry.attrib["kind"]="lib"
      cpEntry.attrib["path"]="test/resource"

    if SOURCE_SETUP:
      dependencies = getDependencies()

    for library in getLibraries():
      if not SOURCE_SETUP or not(reduce(lambda x, y: x|library.startswith('lib/'+y+'-'), dependencies, False)):
        cpEntry = ElementTree.SubElement(root,"classpathentry")
        if properties.has_key('build_target') and properties['build_target'] == 'android':
          cpEntry.attrib["exported"]="true"
        cpEntry.attrib["kind"]="lib"
        cpEntry.attrib["path"]=library
    for resource in getResources():
      cpEntry = ElementTree.SubElement(root,"classpathentry")
      cpEntry.attrib["kind"]="lib"
      cpEntry.attrib["path"]=resource
    if SOURCE_SETUP:
      for dependency in dependencies:
        cpEntry = ElementTree.SubElement(root,"classpathentry")
        cpEntry.attrib["kind"]="src"
        cpEntry.attrib["combineaccessrules"]="false"
        cpEntry.attrib["path"]='/'+dependency

    fclasspath = open(BASE_DIR+'/.classpath','w')
    fclasspath.write(prettify(root))
    fclasspath.close()

def writeLaunchConfig(main):
  if len(main)==0:
    return
  print("writing launch config for "+main)
  shortName = main.split('.')[-1]
  dir = BASE_DIR+'/.settings'
  if not os.path.exists(dir):
    os.makedirs(dir)   

  jvmargs =""
  with open(BASE_DIR+'/build.properties') as fp:
    root = ElementTree.Element("classpath")
    properties = jprops.load_properties(fp)
    if properties.has_key('run.jvmargs'):
      jvmargs = properties['run.jvmargs']
      
  root = ElementTree.Element("launchConfiguration")
  root.attrib["type"]="org.eclipse.jdt.launching.localJavaApplication"
  listAttribute = ElementTree.SubElement(root,"listAttribute")
  listAttribute.attrib["key"]="org.eclipse.debug.core.MAPPED_RESOURCE_PATHS"
  listEntry = ElementTree.SubElement(listAttribute,"listEntry")
  listEntry.attrib["value"]='/'+getProjectName()+'/src/'+main.replace('.','/')+'.java'

  listAttribute = ElementTree.SubElement(root,"listAttribute")
  listAttribute.attrib["key"]="org.eclipse.debug.core.MAPPED_RESOURCE_TYPES"
  listEntry = ElementTree.SubElement(listAttribute,"listEntry")
  listEntry.attrib["value"]="1"
  stringAttribute=ElementTree.SubElement(root,"stringAttribute")
  stringAttribute.attrib["key"]="org.eclipse.jdt.launching.MAIN_TYPE"
  stringAttribute.attrib["value"]=main
  stringAttribute=ElementTree.SubElement(root,"stringAttribute")
  stringAttribute.attrib["key"]="org.eclipse.jdt.launching.PROJECT_ATTR"
  stringAttribute.attrib["value"]=getProjectName()
  stringAttribute=ElementTree.SubElement(root,"stringAttribute")
  stringAttribute.attrib["key"]="org.eclipse.jdt.launching.VM_ARGUMENTS"
  stringAttribute.attrib["value"]=jvmargs+' -Djava.library.path=lib'
  
  with open(dir+'/'+shortName+'.launch','w') as fp:
    fp.write(prettify(root))    

def writeLaunchConfigs():
  for main in MAINS.split(','):
    writeLaunchConfig(main)

#def main():    
parser = argparse.ArgumentParser(description='Create eclipse project files from a HMI project.')
parser.add_argument('--sourcesetup', action="store_true", default=False)
parser.add_argument('--sharedroot', action="store", required=True)
parser.add_argument('--basedir', action="store", required=False, default='.')
parser.add_argument('--sharedresource', action="store", required=True)
parser.add_argument('--asapsharedresource', action="store", required=True)
parser.add_argument('--language', action="store", required=False)
parser.add_argument('--mains', action="store", required=False)
args = parser.parse_args()
SHARED_PATH = args.sharedroot
SOURCE_SETUP = args.sourcesetup
SHARED_RES = args.sharedresource
ASAPSHARED_RES = args.asapsharedresource
BASE_DIR = args.basedir
MAINS = args.mains
writeDotProject()
writeClassPath()
writeLaunchConfigs()
#if __name__ == "__main__":
#    main()
