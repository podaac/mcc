from utils.filehandler import FileHandler

import argparse


# Set up input argument handling
parser = argparse.ArgumentParser(description="Update component version values in the related json file for test execution")
parser.add_argument('-jenkinsbuild', type=str, default="None", help="Build number on Jenkins")
parser.add_argument('-custom', type=str, default="", help="Custom text to add to the Testrun's name in TestRail")
args = vars(parser.parse_args())

# Saving the input arguments into variables
JenkinsBuildNumber = args['jenkinsbuild']if args['jenkinsbuild']!="" else "None"
customText = args['custom']if args['custom']!="" else ""

# Putting the variables into the component_version_info.json file
filename = "component_version_info.json"
location = "./config"
fileLocation = f'{location}/{filename}'

fileExists = FileHandler.CheckIfFileExists(fileLocation)
if not fileExists:
    FileHandler.CreateFile(fileLocation, '{}')

data = FileHandler.GetJsonFileContent(filename, location)
updated = False

if JenkinsBuildNumber != "None":
    data['Jenkins_Build'] = JenkinsBuildNumber
    updated = True

if customText != "":
    data['Custom_Text'] = customText
    updated = True

FileHandler.WriteJsonFile(filename, location, data)

# Verify file content update
jsonData = FileHandler.GetJsonFileContent(filename, location)
if updated:
    print("Version file updated successfully!")