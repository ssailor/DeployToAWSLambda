import argparse
import os
import sys
import json
import zipfile
import boto3

class ProjectInfo:

    def __init__(self, project_name, zip_info, lambda_info):
        self.ProjectName = project_name
        self.ZipInfo = zip_info
        self.LambdaInfo = lambda_info


class ZipInfo:

    def __init__(self, source_directory, file_name, ignore_files):
        self.SourceDirectory = source_directory
        self.FileName = file_name
        self.IgnoreFiles = ignore_files


class LambdaInfo:

    def __init__(self, arn, profile_name, region_name):
        self.ARN = arn
        self.ProfileName = profile_name
        self.RegionName = region_name


def get_file_byte(file_path):
    """Generates the binary of the provided file."""
    # Guard statement to ensure that the file provided is a valid file
    if not os.path.isfile(file_path):
        raise FileNotFoundError("The provided file " + str(file_path) + " is not a valid file" )

    # Open the specified file, read the whole thing into binary and return the binary.
    with open(file_path, "rb") as binary:
        file_binary = binary.read()
        binary.close()
        return file_binary


def get_project_info(config_file_path, selected_project_name):
    """Parses the config file to find the desired project info then maps it to it's model objects."""
    config = None
    output_object = None

    # Open the file and load it into json
    with open(config_file_path) as config_file:
        config = json.load(config_file)
        config_file.close()

    # Check the config data for the desired project and return it to the user as a ProjectInfo instance.
    if selected_project_name and selected_project_name is not None:
        try:
            project = config["Projects"]
            for item in project:

                project_name = str(item["ProjectInfo"]["ProjectName"])

                # Check if the current project is the desired one
                if selected_project_name.lower() == project_name.lower():
                    # Map ZipInfo attributes
                    source_directory = str(item["ProjectInfo"]["ZipInfo"]["SourceDirectory"])
                    file_name = str(item["ProjectInfo"]["ZipInfo"]["FileName"])

                    # Check if optional attribute is found in config file and if not then pass along as an empty list
                    if "IgnoreFile" in item["ProjectInfo"]["ZipInfo"]:
                        ignore_files = item["ProjectInfo"]["ZipInfo"]["IgnoreFiles"]
                    else:
                        ignore_files = []

                    # Create ZipInfo instance
                    zip_info = ZipInfo(source_directory, file_name, ignore_files)

                    # Map LambdaInfo attributes
                    arn = str(item["ProjectInfo"]["LambdaInfo"]["ARN"])

                    # For optional attributes, check if they are present in the config file and if not then set attribute value to None
                    if "ProfileName" in item["ProjectInfo"]["LambdaInfo"]:
                        profile_name = str(item["ProjectInfo"]["LambdaInfo"]["ProfileName"])
                    else:
                        profile_name = None
                    
                    if "RegionName" in item["ProjectInfo"]["LambdaInfo"]:
                        region_name = str(item["ProjectInfo"]["LambdaInfo"]["RegionName"])
                    else:
                        region_name = None

                    # Create LambdaInfo Instance
                    lambda_info = LambdaInfo(arn, profile_name, region_name)

                    # Assign the output to be the ProjectInfo instance
                    output_object = ProjectInfo(project_name, zip_info, lambda_info)
        except KeyError as k: 
            raise KeyError("The config file is malformed and is missing the "+ str(k.args[0]) + " section. Please see the documentation for the proper config file format.")

    else:
        raise ValueError("A project name needs to be provided")

    # Guard statement to protect against not finding a project
    if output_object is None:
        raise ValueError("Unable to find the specified ProjectName in the config file.")

    return output_object


def upload_to_lambda(function_arn, bytes_of_zip, profile_name=None, region_name=None):
    
    # Guard statement to ensure that the program has the required AWS ARN
    if not function_arn or function_arn is None:
        raise ValueError("An AWS Lambda ARN is required to upload the code package.")

    # Guard statement to ensure that the program has a byte array of the zipfile
    if not bytes_of_zip or bytes_of_zip is None:
        raise ValueError("A binary representation of the zip file is required in order to upload to lambda.")

    # Guard statement to set default values for the profile name and region name
    if not profile_name or profile_name is None:
        profile_name = "default"
    
    if not region_name or region_name is None:
        region_name = "us-east-1"

    # Create a session, in the session you can add things such as the region or which profile you wish to use
    session = boto3.session.Session(profile_name=profile_name, region_name=region_name)

    # Create a client from the session for lambda
    client = session.client(service_name='lambda')

    # Call the function that updates the code package for your lambda function
    response = client.update_function_code(
        FunctionName=function_arn,
        ZipFile=bytes_of_zip
    )

    # Return the response provided by the boto call
    return response


def flat_zip_files(source_directory, zip_filename, output_directory, ignore_list):
    
    # Guard statement to check if the source directory is a directory
    if not os.path.isdir(source_directory):
        raise NotADirectoryError("The provided value for SourceDirectory is not a valid directory")

    # Guard statement to check if the output directory is a directory
    if not os.path.isdir(output_directory):
        raise NotADirectoryError("The provided value for OutputDirectory is not a valid directory")

    # Create var to store the zip path and filename
    output_file = None

    # create the full path from the name and
    output_file = os.path.join(output_directory, zip_filename)

    # Create instance of zipfile object, set the path/filename to the user
    # provided value, set it to write and compression to deflated
    zfile = zipfile.ZipFile(output_file, mode='w', compression=zipfile.ZIP_DEFLATED)

    # Walk the file structure to get the files and zip them into the specified
    # zip directory
    for root, _, files in os.walk(source_directory):
        for file in files:
            # Check if the current file is on the ignore list.
            if file not in ignore_list:
                # Write current file to the zip file in the required flattened format
                zfile.write(os.path.join(root, file), arcname=file)

    # Close the zip connection
    zfile.close()

    # return the path of the created zip file
    return output_file


def main():
    
    # Variable flag to determine the program should run without command line output
    run_silent = False 

    # Variable for the project name provided by the user
    selected_project_name = None

    # Get the directory that this current file is located
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Get the config file from the current file's directory
    config_file_path = os.path.join(current_directory, "config.json")

    # Guard statement to check that the config file is where the program expects it to be
    if not os.path.isfile(config_file_path):
        raise FileNotFoundError("The config file was not found in the same directory as the python project")

    # Create an ArgumentParser to be able to provide command line options for the user to interact with the program
    arg_parser = argparse.ArgumentParser(description='Deploy project code to AWS lambda using the values store in the programs config file.')
    # Add a required parameter for the projectname that is stored in the json config file
    arg_parser.add_argument('-P', '--projectname', help="Name of the project stored in the config file", required = True)
    # Add an optional boolean parameter for the program to run silently or not
    arg_parser.add_argument('-s', '--silent', help="Run without output", action="store_true", default = False)

    # Get a collection of the command line arguments and assign the values to local variables
    args = arg_parser.parse_args()
    run_silent = args.silent
    selected_project_name = args.projectname

    # Parse and consume the config file and raise an exception if the specified project is not found
    project_info = get_project_info(config_file_path, selected_project_name)

    # Zip the files using the data from the config file
    zip_file = flat_zip_files(project_info.ZipInfo.SourceDirectory, project_info.ZipInfo.FileName, current_directory, project_info.ZipInfo.IgnoreFiles)

    # Get a byte array of zip file (This is required to upload to lambda)
    bytes_of_zip = get_file_byte(zip_file)

    # Push the zip package to AWS Lambda
    upload_response = upload_to_lambda(project_info.LambdaInfo.ARN, bytes_of_zip, project_info.LambdaInfo.ProfileName, project_info.LambdaInfo.RegionName)

    if not run_silent:
        # Print the respone provided by the boto call
        print(json.dumps(upload_response, indent=4))

    # Delete the created zip file
    os.remove(zip_file)

if __name__ == '__main__':
    main()
