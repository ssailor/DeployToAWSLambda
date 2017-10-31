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
    # Open the specified file, read the whole thing into binary and return the binary.
    with open(file_path, "rb") as binary:
        file_binary = binary.read()
        binary.close()
        return file_binary


def get_project_info(config_file_path, selected_project_name):
    config = None
    output_object = None

    with open(config_file_path) as config_file:
        config = json.load(config_file)
        config_file.close()

    # Check the config data for the desired project and return it to the user as a ProjectInfo instance.
    if selected_project_name and selected_project_name is not None:
        for item in config["Projects"]:

            project_name = str(item["ProjectInfo"]["ProjectName"])

            # Check if the current project is the desired one
            if selected_project_name.lower() == project_name.lower():
                # Map ZipInfo attributes
                source_directory = str(item["ProjectInfo"]["ZipInfo"]["SourceDirectory"])
                file_name = str(item["ProjectInfo"]["ZipInfo"]["FileName"])
                ignore_files = item["ProjectInfo"]["ZipInfo"]["IgnoreFiles"]

                # Create ZipInfo instance
                zip_info = ZipInfo(source_directory, file_name, ignore_files)

                # Map LambdaInfo attributes
                arn = str(item["ProjectInfo"]["LambdaInfo"]["ARN"])
                profile_name = str(item["ProjectInfo"]["LambdaInfo"]["ProfileName"])
                region_name = str(item["ProjectInfo"]["LambdaInfo"]["RegionName"])

                # Create LambdaInfo Instance
                lambda_info = LambdaInfo(arn, profile_name, region_name)

                # Assign the output to be the ProjectInfo instance
                output_object = ProjectInfo(project_name, zip_info, lambda_info)

    else:
        raise ValueError("A project name needs to be provided")

    return output_object


def upload_to_lambda(function_arn, bytes_of_zip, profile_name=None, region_name="us-east-1"):

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


def flat_zip_files(source_directory, output_zip_filename, output_zip_path, ignore_list):
    # Create var to store the zip path and filename
    output_file = None

    # create the full path from the name and
    output_file = os.path.join(output_zip_path, output_zip_filename)

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
    # Variable for the project name provided by the user
    selected_project_name = None

    # Get the directory that this current file is located
    current_directory = os.path.dirname(__file__)

    # Get the config file from the current file's directory
    config_file_path = os.path.join(current_directory, "config.json")

    # Get the project name from the command line args
    try:
        selected_project_name = sys.argv[1]
    except:
        raise ValueError("ERROR: A value needs to be provided for the project name argument")

    # Parse and consume the config file
    project_info = get_project_info(config_file_path, selected_project_name)

    # Zip the files using the data from the config file
    zip_file = flat_zip_files(project_info.ZipInfo.SourceDirectory, project_info.ZipInfo.FileName, current_directory, project_info.ZipInfo.IgnoreFiles)

    # Get a byte array of zip file (This is required to upload to lambda)
    bytes_of_zip = get_file_byte(zip_file)

    # Push the zip package to AWS Lambda
    upload_response = upload_to_lambda(project_info.LambdaInfo.ARN, bytes_of_zip, project_info.LambdaInfo.ProfileName, project_info.LambdaInfo.RegionName)

    # Print the respone provided by the boto call
    print(json.dumps(upload_response, indent=4))

    # Delete the created zip file
    os.remove(zip_file)

if __name__ == '__main__':
    main()
