# Serverless Contact Form with AWS

## Overview

This project implements a serverless contact form system using AWS services: **Lambda**, **API Gateway**, **DynamoDB**, and **SNS**. It captures user submissions from a static frontend, stores them securely in DynamoDB, and sends real-time email notifications to the admin via SNS. The system is **scalable**, **low-maintenance**, and follows the **principle of least privilege** with IAM roles.

---

## Features

- **Form Submission Handling**: Captures user input (name, email, message) via a static frontend hosted on S3.  
- **Serverless Processing**: API Gateway triggers a Lambda function to process submissions.  
- **Data Storage**: Stores submission data securely in a DynamoDB table.  
- **Real-Time Notifications**: Sends email notifications via SNS upon form submission.  
- **Security**: Uses IAM roles to ensure minimal permissions for each AWS service.

---

## Technologies Used

- **AWS Services**: Lambda, API Gateway, DynamoDB, SNS, IAM, S3  
- **Programming Language**: Python 3.13 (for Lambda function)  
- **Frontend**: HTML (static site hosted on S3)  
- **Tools**: AWS Management Console, Postman (for testing)

---

## Prerequisites

- An active AWS account  
- Basic knowledge of AWS services (Lambda, API Gateway, IAM, DynamoDB, SNS)  
- Familiarity with Python for Lambda function logic  
- IAM permissions to create roles, policies, and resources in AWS  
- Understanding of CORS and HTTP basics for API Gateway configuration

---

## Installation

### 1. Set Up Static Frontend

- Host a static HTML contact form on an S3 bucket.  
- Copy the `index.html` from this repository and update the API Gateway URL (see step 6).

### 2. Create DynamoDB Table

- In the AWS Management Console, navigate to DynamoDB.  
- Create a table named `ContactFormSubmissions` with `submissionId` (string) as the partition key.  
- Keep default settings and create the table.

### 3. Create SNS Topic

- Go to SNS in the AWS Management Console.  
- Create a standard topic named `ContactFormTopic`.  
- Add a subscription (e.g., Email protocol with your email address as the endpoint).  
- Confirm the subscription via the email link.

### 4. Set Up IAM Role for Lambda

- Navigate to IAM in the AWS Management Console.  
- Create a policy (`ContactFormPermissions`) with the following JSON:

```json
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
                "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/ContactFormSubmissions",
                "arn:aws:sns:REGION:ACCOUNT_ID:ContactFormTopic"
            ]
        }
    ]
}

Create a Lambda role, attaching AWSLambdaBasicExecutionRole and ContactFormPermissions.

5. Deploy Lambda Function
In the Lambda service, create a function named contact-form-function with Python 3.13 runtime.

Attach the IAM role created above.

Copy and paste the Lambda function code from the repository’s lambda_function.py (or article).

Update the DynamoDB table name and SNS topic ARN in the code.

Deploy the function.

6. Set Up API Gateway
In API Gateway, create a REST API (regional endpoint).

Create a resource (e.g., /contactform) with CORS enabled.

Add a POST method, integrating it with the Lambda function (enable Lambda proxy integration).

Deploy the API to a stage (e.g., test) and note the Invoke URL.

Update the frontend’s index.html with the Invoke URL:

7. Test the System
Test the Lambda function using the AWS Console with a sample payload:

{
    "body": "{\"name\":\"John Wick\",\"email\":\"john.wick@example.com\",\"message\":\"This is a sample message!\"}"
}

Test the API using Postman:
Send a POST request to the Invoke URL with JSON body:

{
    "name": "Joshua Jackson",
    "email": "joshuajackson@example.com",
    "message": "This is a test message!"
}

Verify Content-Type: application/json in headers.

Upload the updated index.html to S3 and test the form via the website.

Check DynamoDB for stored submissions and your email for SNS notifications.

Usage
Access the contact form via the S3-hosted website.

Submit the form with name, email, and message.

Receive a "Form submitted successfully" message on valid submissions.

Verify data in the DynamoDB table (ContactFormSubmissions).

Check email for SNS notifications with submission details.

License
This project is licensed under the MIT License.


