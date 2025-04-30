Serverless Contact Form with AWS
A serverless contact form using AWS Lambda, API Gateway, DynamoDB, and SNS to capture submissions, store them securely, and send admin notifications. Built for my portfolio to showcase DevOps skills.
Architecture

Features

S3-hosted frontend (index.html) for form submissions
API Gateway and Lambda (Python) for processing
DynamoDB (ContactFormSubmissions) for storage
SNS (ContactFormTopic) for email notifications
IAM roles with least privilege for security
Runs in AWS free tier

Prerequisites

AWS Account
Basic knowledge of AWS (Lambda, API Gateway, IAM, DynamoDB, SNS, S3)
Familiarity with Python
Understanding of CORS and HTTP basics

Setup
Clone the repo:  
git clone https://github.com/Harbeylefty/contact-form-project.git
cd contact-form-project

1. DynamoDB Table

In DynamoDB, create a table:  
Name: ContactFormSubmissions  
Partition Key: submissionId (String)  
Use default settings (on-demand billing)



2. SNS Topic

In SNS, create a topic:  
Name: ContactFormTopic (Standard type)


Add an email subscription and confirm via the email link.

3. IAM Role for Lambda

In IAM, create a policy (ContactFormPermissions):

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowDynamoDBAndSNSAccess",
            "Effect": "Allow",
            "Action": ["sns:Publish", "dynamodb:PutItem"],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:038462762530:table/ContactFormSubmissions",
                "arn:aws:sns:us-east-1:038462762530:ContactFormTopic"
            ]
        }
    ]
}


Create a role (ContactFormLambdaRole):  
Type: AWS service > Lambda  
Attach policies: AWSLambdaBasicExecutionRole, ContactFormPermissions



4. Lambda Function

In Lambda, create a function:  
Name: contact-form-function  
Runtime: Python 3.13  
Role: ContactFormLambdaRole


Add this code:

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


Deploy and test with:

{
  "body": "{\"name\":\"John Wick\",\"email\":\"john.wick@example.com\",\"message\":\"This is a sample message!\"}"
}


Verify: Check logs, DynamoDB table, and SNS email.

5. API Gateway

In API Gateway, create a REST API (Regional):  
Create a resource: /contactform (enable CORS)  
Add a POST method: Link to contact-form-function with Lambda proxy integration


Deploy to a stage (test) and note the Invoke URL (e.g., https://<id>.execute-api.us-east-1.amazonaws.com/test/contactform).

6. S3 Frontend

In S3, create a bucket (e.g., contact-form-frontend).  
Enable Static website hosting.  
Upload index.html from the repo.  
Make the bucket public (set a policy for read access).  
Update index.html with the API Gateway Invoke URL.  
Re-upload index.html.  
Access the website URL (e.g., http://contact-form-frontend.s3-website-us-east-1.amazonaws.com).

Usage

Visit the S3 website URL.  
Submit the form (name, email, message).  
Verify:  
Frontend shows "Form submitted successfully!" (or error if fields are empty)  
Submission is in DynamoDB (ContactFormSubmissions)  
SNS email is received



Files

index.html: Frontend for the contact form
assets/architecture.png: System architecture diagram

Connect With Me

LinkedIn
X (Twitter)
Email

License
This project is licensed under the MIT License - see the LICENSE file for details.
