import json
import boto3
import logging
import time

logging.getLogger().setLevel(logging.INFO)
sns_client = boto3.client('sns')
s3_client = boto3.client('s3')

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

        # Save to S3
        bucket_name = 'contactform-submission-bucket'  # Replace with your bucket name
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        key = f"submissions/{timestamp}-{email}.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps({
                'name': name,
                'email': email,
                'message': message,
                'timestamp': timestamp
            }),
            ServerSideEncryption='AES256'
        )
        logging.info(f"Saved submission to S3: {key}")

        # Publish to SNS
        topic_arn = 'arn:aws:sns:us-east-1:038462762530:contactformsubmission'
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



























# import json
# import boto3
# import logging

# # Set up logging
# logging.getLogger().setLevel(logging.INFO)
# sns_client = boto3.client('sns')

# def lambda_handler(event, context):
#     # Define CORS headers
#     headers = {
#         'Content-Type': 'application/json',
#         'Access-Control-Allow-Origin': '*',
#         'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
#         'Access-Control-Allow-Methods': 'POST,OPTIONS'
#     }
    
#     try:
#         # Safely parse the body
#         body = json.loads(event.get('body', '{}'))
#         name = body.get('name')
#         email = body.get('email')
#         message = body.get('message')

#         # Validate input
#         if not all([name, email, message]):
#             return {
#                 'statusCode': 400,
#                 'headers': headers,
#                 'body': json.dumps({'message': 'Missing required fields'})
#             }

#         # Set the SNS topic ARN
#         topic_arn = 'arn:aws:sns:us-east-1:038462762530:contactformsubmission'

#         # Construct the message body
#         message_body = f"""
#         New contact form submission:

#         Name: {name}
#         Email: {email}
#         Message: {message}
#         """

#         # Publish to SNS
#         response = sns_client.publish(
#             TopicArn=topic_arn,
#             Message=message_body,
#             Subject='New Contact Form Submission'  # Added subject for clarity
#         )
#         logging.info(f"SNS Publish Response: {response}")

#         # Return success response
#         return {
#             'statusCode': 200,
#             'headers': headers,
#             'body': json.dumps({'message': 'Form submitted successfully!'})
#         }

#     except json.JSONDecodeError:
#         logging.error("Invalid JSON in request body")
#         return {
#             'statusCode': 400,
#             'headers': headers,
#             'body': json.dumps({'message': 'Invalid JSON format'})
#         }
#     except Exception as e:
#         logging.error(f"Error sending message to SNS: {str(e)}")
#         return {
#             'statusCode': 500,
#             'headers': headers,
#             'body': json.dumps({'message': 'Error processing form'})
#         }















# import json
# import boto3

# sns_client = boto3.client('sns')

# def lambda_handler(event, context):
#     # Parse the incoming JSON data
#     body = json.loads(event['body'])
#     name = body.get('name')
#     email = body.get('email')
#     message = body.get('message')

#     # Set the SNS topic ARN (replace with your actual SNS Topic ARN)
#     topic_arn = 'arn:aws:sns:YOUR_REGION:YOUR_ACCOUNT_ID:ContactFormTopic'

#     # Construct the message body
#     message_body = f"""
#     New contact form submission:

#     Name: {name}
#     Email: {email}
#     Message: {message}
#     """

#     # Publish to SNS
#     try:
#         response = sns_client.publish(
#             TopicArn=topic_arn,
#             Message=message_body
#         )
        
#         # Return a successful response
#         return {
#             'statusCode': 200,
#             'body': json.dumps({'message': 'Form submitted successfully!'})
#         }
#     except Exception as e:
#         print(f"Error sending message to SNS: {e}")
        
#         # Return an error response
#         return {
#             'statusCode': 500,
#             'body': json.dumps({'message': 'Error processing form'})
#         }
