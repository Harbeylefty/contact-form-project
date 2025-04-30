Serverless Contact Form with AWS: Lambda, DynamoDB, API Gateway, and SNS
Project Overview
This project is a serverless contact form system that processes user submissions without managing servers. It uses AWS Lambda, API Gateway, DynamoDB, and SNS to handle data, store it securely, and send real-time notifications. Submissions are captured, saved to DynamoDB, and an admin notification is sent via SNS. The system is scalable, low-maintenance, and secure, using IAM roles with least privilege.
Highlights

Captures user form submissions
API Gateway triggers Lambda on form submission
Lambda processes and stores data in DynamoDB
SNS sends real-time email notifications to the admin
Secures access with IAM roles following least privilege

Prerequisites

AWS Account
Basic knowledge of AWS services (Lambda, API Gateway, IAM, DynamoDB, SNS, S3)
Familiarity with Python for the Lambda function
Ability to manage IAM roles, policies, and resources
Understanding of CORS and HTTP basics for API Gateway

Setup Instructions
Follow these steps to set up the project, creating resources in the order they’re needed.
Clone the Repository
Clone this repository to get started:  
git clone https://github.com/Harbeylefty/contact-form-project.git
cd contact-form-project

Create DynamoDB Table
Create a DynamoDB table to store form submissions:  

Go to DynamoDB in the AWS Console.  
Click Create table.  
Name: ContactFormSubmissions.  
Partition Key: submissionId (String).  
Use default settings with on-demand billing mode.  
Click Create table.

Create SNS Topic
Set up an SNS topic for admin notifications:  

Go to SNS in the AWS Console.  
Click Create topic, select Standard type.  
Name: ContactFormTopic.  
Click Create topic.

Add Subscription to the SNS Topic

In SNS, click Create subscription.  
Select the ContactFormTopic ARN.  
Protocol: Email (or SMS if preferred).  
Endpoint: Enter your email address (or phone number for SMS).  
Click Create subscription.  
Confirm the subscription via the email link sent to you.

Set Up IAM Role and Permissions for Lambda
Create an IAM role for Lambda with the necessary permissions.
Create IAM Policy

Go to IAM in the AWS Console.  
Click Policies > Create policy.  
In the JSON editor, paste:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowDynamoDBAndSNSAccess",
            "Effect": "Allow",
            "Action": [
                "sns:Publish",
                "dynamodb:PutItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:038462762530:table/ContactFormSubmissions",
                "arn:aws:sns:us-east-1:038462762530:ContactFormTopic"
            ]
        }
    ]
}


Click Next, name the policy ContactFormPermissions, and click Create policy.

Create IAM Role

In IAM, click Roles > Create role.  
Select AWS service > Lambda.  
Attach policies:  
AWSLambdaBasicExecutionRole (for logging)  
ContactFormPermissions (created above)


Name the role (e.g., ContactFormLambdaRole) and click Create role.

Deploy Lambda Function
Deploy the Lambda function to process form submissions.
Create the Lambda Function

Go to Lambda in the AWS Console.  
Click Create function.  
Choose Author from scratch.  
Name: contact-form-function.  
Runtime: Python 3.13.  
Execution role: Select the existing role ContactFormLambdaRole.  
Click Create function.

Add Lambda Function Code
Copy the following code into the Lambda editor:  
import json
import boto3
import logging
import time

logging.getLogger().setLevel(logging.INFO)
sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    try:
        body = json.loads(event.get('body', '{}'))
        name = body.get('name')
        email = body.get('email')
        message = body.get('message')

        if not all([name, email, message]):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'message': 'Missing required fields'})
            }

        # Save to DynamoDB
        table = dynamodb.Table('ContactFormSubmissions')
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        submission_id = f"{timestamp}-{email}"
        table.put_item(
            Item={
                'submissionId': submission_id,
                'name': name,
                'email': email,
                'message': message,
                'timestamp': timestamp
            }
        )
        logging.info(f"Saved submission to DynamoDB: {submission_id}")

        # Publish to SNS
        topic_arn = 'arn:aws:sns:us-east-1:038462762530:ContactFormTopic'
        message_body = f"""
        New contact form submission:

        Name: {name}
        Email: {email}
        Message: {message}
        """
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message_body,
            Subject='New Contact Form Submission'
        )
        logging.info(f"SNS Publish Response: {response}")

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'Form submitted successfully!'})
        }

    except json.JSONDecodeError:
        logging.error("Invalid JSON in request body")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'message': 'Invalid JSON format'})
        }
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'message': 'Error processing form'})
        }


Click Deploy to save. Ensure the DynamoDB table name and SNS topic ARN match your setup.

Test the Lambda Function

In the Lambda console, click Test.  
Create a test event with the following:

{
  "body": "{\"name\":\"John Wick\",\"email\":\"john.wick@example.com\",\"message\":\"This is a sample message!\"}"
}


Click Test. You should see a 200 status code with the message "Form submitted successfully!" in the logs.  
Check your email for an SNS notification with the user’s details.  
In DynamoDB, go to ContactFormSubmissions and click Explore items to confirm the submission is stored.

Set Up API Gateway to Trigger Lambda Function
Set up API Gateway to expose the Lambda function to the internet.  

Go to API Gateway in the AWS Console.  
Click Create API, select REST API, and click Build.  
Choose New API, name it, and set the endpoint type to Regional.  
Click Create API.  
Click Create resource, name it contactform, and enable CORS.  
Click Create resource.

Create POST Method

Select the /contactform resource and click Create Method.  
Method type: POST.  
Integration type: Lambda Function.  
Select contact-form-function and enable Lambda proxy integration.  
Click Create method.

Deploy the API

Click Deploy API, select New stage, name it test, and click Deploy.  
Note the Invoke URL (e.g., https://<id>.execute-api.us-east-1.amazonaws.com/test/contactform).

Test the API with Postman

Open Postman and create a new HTTP request.  
Set method to POST.  
URL: Append /contactform to the Invoke URL (e.g., https://<id>.execute-api.us-east-1.amazonaws.com/test/contactform).  
Body: Select raw > JSON, and add:

{
  "name": "Joshua Jackson",
  "email": "joshuajackson@example.com",
  "message": "This is a test message!"
}


Headers: Ensure Content-Type is application/json.  
Click Send. You should see a response: "message: Form submitted successfully".

Set Up S3 Frontend
Host the static frontend on S3 to serve the contact form.  

Go to S3 in the AWS Console.  
Create a bucket (e.g., contact-form-frontend).  
Enable Static website hosting in the bucket properties.  
Upload index.html from the repo to the bucket.  
Make the bucket public by setting a policy to allow read access (refer to the article for the policy JSON).  
Update index.html with the API Gateway Invoke URL (e.g., https://<id>.execute-api.us-east-1.amazonaws.com/test/contactform).  
Re-upload index.html to the bucket.  
Access the bucket’s website URL (e.g., http://contact-form-frontend.s3-website-us-east-1.amazonaws.com).

Usage

Open the S3 website URL in a browser.  
Fill in the form (name, email, message) and submit.  
Verify:  
The frontend shows "Form submitted successfully!" (or "Please fill out this field" if a field is empty).  
The submission is in the ContactFormSubmissions DynamoDB table.  
You receive an SNS email notification with the user’s details.



Files in This Repository

index.html: Static frontend for the contact form, hosted on S3
assets/architecture.png: Architecture diagram of the system

Conclusion
This serverless contact form is efficient, secure, and easy to maintain. Using API Gateway, Lambda, SNS, and DynamoDB, it collects user submissions, stores data safely, and sends real-time notifications. It runs without managing servers, keeping operations simple and costs low. The IAM role ensures each component has only the permissions it needs. This project showcases how AWS serverless tools can build flexible, dependable systems.
Thank you for following along. I hope this project proves valuable for your serverless projects!
Connect With Me

LinkedIn
X (Twitter)
Email

License
This project is licensed under the MIT License - see the LICENSE file for details.
