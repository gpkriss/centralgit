import boto3
import os

# AWS Secrets Manager client
client = boto3.client('secretsmanager', region_name='us-east-1')

# Read secret names from the file
with open("secret_names.txt", "r") as file:
    secret_names = [line.strip() for line in file.readlines()]

# Store each secret individually
for secret_name in secret_names:
    secret_value = os.getenv(secret_name)  # Get secret value from env vars

    if secret_value:  # Only store if value exists
        try:
            client.get_secret_value(SecretId=secret_name)
            client.update_secret(SecretId=secret_name, SecretString=secret_value)
            print(f"Updated existing secret: {secret_name}")
        except client.exceptions.ResourceNotFoundException:
            client.create_secret(Name=secret_name, SecretString=secret_value)
            print(f"Created new secret: {secret_name}")
    else:
        print(f"Skipping {secret_name}: No value found.")
