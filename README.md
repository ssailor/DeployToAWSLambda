# DeployToAWSLambda

DeployToAWSLambda is a python utility created to make it faster and easier to deploy code to your AWS Lambda functions. This project uses the AWS Python SDK (boto3), to upload local code to a specified AWS Lambda function. Information about the project and it's corresponding lambda function are stored in a JSON config file in the same directory as the program. To use this program the user will call DeployToAWSLambda though the command line giving it a command line argument of the project name they wish to upload which, is also stored in the JSON file. 

## Getting Started
These instructions will get your local machine set up for use of this utility.

### Prerequisites

- Python 3
- Local AWS CLI/SDK Profiles (For more information: http://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html)

### Installing

Step by step instructions on how to install and set up this project.

1. Clone this repo to the desired folder on your machine
2. If you have not already, get AWS access keys from your AWS account and store them as a profile on your machine in the AWS Credentials file. (See the link in Prerequisites for more info )
3. Update the *config.json* file with ProjectInfo object(s) in the Projects array : 

```
{
    "Projects": [
        {
            "ProjectInfo": {
                "ProjectName": "SAMPLE PROJECT NAME",
                "ZipInfo": {
                    "SourceDirectory": "SAMPLE SOURCE DIRECTORY",
                    "FileName": "SAMPLE FILENAME",
                    "IgnoreFiles": [
                        "SampleFile1.txt",
                        "SampleFile2.json"
                    ]
                },
                "LambdaInfo": {
                    "ARN": "SAMPLE ARN",
                    "ProfileName": "SAMPLE PROFILE NAME",
                    "RegionName": "SAMPLE REGION NAME"
                }
            }
        }
    ]
}
```
4. Replace the values in the JSON ProjectInfo object with the following pieces of information:
    - **ProjectName** - The name of the project, this will be the command line argument you need to provide in the terminal/command line.
    - **SourceDirectory** - The folder that contains the source code you wish to upload (Note: All files in the folder will be zipped unless added to the IgnoreFiles list)
    - **FileName** - The name of the resulting zip file that will be uploaded
    - **IgnoreFiles** (*Optional*) - Files in the source directory that you wish to be excluded from the zip file
    - **ARN** - The Amazon ARN (Amazon Resource Name) for the lambda function you wish to upload the code to. This can be found in your lambda function and should look similar to
    ```arn:aws:lambda:us-east-1:000000000000:function:SampleFunction```
    - **ProfileName** (*Optional*) - The name of the profile in your AWS Credentials file
    - **RegionName** (*Optional*) - The region your Lambda function is located

5. Use the command line to call the python utility and provide the necessary and desired flags
    - __Command Line Flags__
        - **-P or --projectname** *ProjectName* *(Required)* - Specifies to the program what project you are working with. This will be the same name as the ones stored in the config file.
        - **-s or --silent** - If flag is included it will run the program in silent mode and will not provide output to the command line
        - **-h or --help** - Provides help information about available program flags

6. (*Optional*) Create a bat file or shell script in the folder you store your source code and add it to the IgnoreFiles list in the JSON config file. This will allow you to deploy from a script within the folder you have the code.

```
Sample: Deploy.bat
python "C:/DeployToAWSLambda/DeployToAWSLambda.py" -P SampleProjectName
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
