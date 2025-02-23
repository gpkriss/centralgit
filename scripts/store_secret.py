import json
import boto3
import os

# AWS Client Setup
client = boto3.client('secretsmanager', region_name='us-east-1')

# Load secrets from JSON file
with open('secrets.json', 'r') as file:
    secrets = json.load(file)

# Define AWS Secret Name
aws_secret_name = "github-repo-secrets"

# Convert secrets dictionary to JSON string
secrets_string = json.dumps(secrets)

# Check if the secret exists in AWS Secrets Manager
try:
    response = client.get_secret_value(SecretId=aws_secret_name)
    # If it exists, update the secret
    client.update_secret(SecretId=aws_secret_name, SecretString=secrets_string)
    print(f"Updated existing secret: {aws_secret_name}")
except client.exceptions.ResourceNotFoundException:
    # If it does not exist, create a new secret
    client.create_secret(Name=aws_secret_name, SecretString=secrets_string)
    print(f"Created new secret: {aws_secret_name}")


