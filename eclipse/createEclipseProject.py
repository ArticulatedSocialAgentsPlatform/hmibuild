import argparse

#def main():    
parser = argparse.ArgumentParser(description='Create eclipse project files from a HMI project.')
parser.add_argument('--sourcesetup', action="store_true", default=False)
parser.add_argument('--sharedroot', action="store", required=True)
parser.add_argument('--basedir', action="store", required=False, default='.')
parser.add_argument('--sharedresource', action="store", required=True)
parser.add_argument('--asapsharedresource', action="store", required=True)
parser.add_argument('--language', action="store", required=True)
parser.add_argument('--mains', action="store", required=False)
args = parser.parse_args()
SHARED_PATH = args.sharedroot
SOURCE_SETUP = args.sourcesetup
SHARED_RES = args.sharedresource
ASAPSHARED_RES = args.asapsharedresource
BASE_DIR = args.basedir
LANGUAGE = args.language
MAINS = args.mains
if LANGUAGE == "java":
  import createEclipseJavaProject

if LANGUAGE == "python":
  import createEclipsePythonProject
