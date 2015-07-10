import argparse
from xml.etree import ElementTree
from xml.dom import minidom

from eclipseutils import *
  
def getProjectName():
  tree = ElementTree.parse(BASE_DIR+'/build.xml')
  projectElem = tree.getroot()
  return projectElem.attrib['name']+'_python'
    
def writePyDevProject():
  root = ElementTree.Element("pydev_project")
  sourcePath = ElementTree.SubElement(root,"pydev_pathproperty")
  sourcePath.attrib["name"]="org.python.pydev.PROJECT_SOURCE_PATH"
  
  spElem = ElementTree.SubElement(sourcePath,"path")
  spElem.text='/'+getProjectName()+'/src'
  
  spElem = ElementTree.SubElement(sourcePath,"path")
  spElem.text='/'+getProjectName()+'/lib'
  
  if os.path.isdir(BASE_DIR+'/generatedsrc'):
    spElem = ElementTree.SubElement(sourcePath,"path")
    spElem.text='/'+getProjectName()+'/generatedsrc'

  if os.path.isdir(BASE_DIR+'/test/src'):
    spElem = ElementTree.SubElement(sourcePath,"path")
    spElem.text='/'+getProjectName()+'/test/src'    
    
  if os.path.isdir(BASE_DIR+'/test/lib'):
    spElem = ElementTree.SubElement(sourcePath,"path")
    spElem.text='/'+getProjectName()+'/test/lib'        
    
  #<pydev_property name="org.python.pydev.PYTHON_PROJECT_VERSION">python 2.7</pydev_property>
  pythonVersion = ElementTree.SubElement(root, "pydev_property")
  pythonVersion.attrib["name"]="org.python.pydev.PYTHON_PROJECT_VERSION"
  pythonVersion.text = "python 2.7"
  
  #<pydev_property name="org.python.pydev.PYTHON_PROJECT_INTERPRETER">Default</pydev_property>
  pythonInterpreter = ElementTree.SubElement(root, "pydev_property")
  pythonInterpreter.attrib["name"]="org.python.pydev.PYTHON_PROJECT_INTERPRETER"
  pythonInterpreter.text = "Default"
  
  pyproject = open(BASE_DIR+'/.pydevproject','w')
  pyproject.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<?eclipse-pydev version="1.0"?>\n'+ElementTree.tostring(root, 'utf-8').replace('<?xml version="1.0" ?>',''))
  pyproject.close()

def writeDotProject():
  tree = ElementTree.parse(BASE_DIR+'/build.xml')
  projectElem = tree.getroot()
  fdefaultProject = open(SHARED_PATH+'/hmibuild/eclipse/defaultpythonproject','r')
  content = fdefaultProject.read();
  content = content.replace("$name$",getProjectName());
  fproject = open(BASE_DIR+'/.project', 'w')
  fproject.write(content)
  fproject.close()


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
writeDotProject()
writePyDevProject()
