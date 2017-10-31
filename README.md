# DeployToAWSLambda

DeployToAWSLambda intended to make it faster and easier to deploy code to your AWS Lambda functions. This project uses the AWS Python SDK (boto3), to upload local source code to a specified AWS Lambda function. Values are stored in a json config file in the same directory as the program. In order to use this program the user will call it though the commandline giving it a commandline argument of the project name the wish to upload which is also stored in the json file. 

## Getting Started
These instructions will get your local machine set up for use of this utility.

### Prerequisites

- Python 3
- Local AWS CLI/SDK Profiles (For more information : http://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html)

### Installing

Step by step instructions of how to install and set up this project.

1. Clone this repo to a desired folder on your machine
2. If you have not already, get AWS access keys from your AWS account and store them as a profile on your machine in the AWS Credentials file. (See the link in Prerequisites for more info )
3. Update the *config.json* file with an entry in the Projects array in the following object: 

```
    {
        "ProjectInfo": {
            "ProjectName": "SAMPLE PROJECT NAME",
            "ZipInfo": {
                "SourceDirectory": "SAMPLE SOURCE DIRECTORY",
                "FileName": "SAMPLE FILENAME",
                "IgnoreFiles": ["File1.txt", "File2.bat"]
            },
            "LambdaInfo": {
                "ARN": "SAMPLE ARN",
                "ProfileName": "SAMPLE PROFILE NAME",
                "RegionName": "SAMPLE REGION NAME"
            }
        }
    }
```
4. Replace the values in the json ProjectInfo object with the following pieces of information:
    - **ProjectName** - The name of the project, this will be the commandline argument you need to provide in the the terminal/commandline.
    - **SourceDirectory** - The folder that contains the source code you wish to upload (Note: All files in the folder will be zipped unless added to the IgnoreFiles list)
    - **FileName** - The name of the resulting zip file that will be uploaded
    - **IgnoreFiles** - Files in the SourceDirectory that you wish to be excluded from the zip file
    - **ARN** - The Amazon ARN (Amazon Resource Name) for the lambda function you wish to upload the code to. This can be found in your lambda function and should look similar to
    ```arn:aws:lambda:us-east-1:000000000000:function:SampleFunction```
    - **ProfileName** - The name of the profile in your AWS Credentials file
    - **RegionName** - The region your Lambda function is located

5. (*Optional*) Create a bat file or shell script in the folder you store your source code and add it to the IgnoreFiles list in the json config file. This will allow you to deploy from a script within the folder you have the code. 

```
Sample: Deploy.bat
python "C:/DeployToAWSLambda/DeployToAWSLambda.py" SampleProjectName
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
