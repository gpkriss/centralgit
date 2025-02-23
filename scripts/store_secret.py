import json
import boto3

# AWS Secrets Manager client
client = boto3.client('secretsmanager', region_name='us-east-1')

# Load secrets from JSON file
with open('secrets.json', 'r') as file:
    secrets = json.load(file)

# Store each secret individually
for secret_name, secret_value in secrets.items():
    try:
        # Check if the secret exists
        client.get_secret_value(SecretId=secret_name)
        client.update_secret(SecretId=secret_name, SecretString=secret_value)
        print(f"Updated existing secret: {secret_name}")
    except client.exceptions.ResourceNotFoundException:
        client.create_secret(Name=secret_name, SecretString=secret_value)
        print(f"Created new secret: {secret_name}")

