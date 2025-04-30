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
        topic_arn = 'arn:aws:sns:REGION:ACCOUNT_ID:ContactFormTopic'
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
