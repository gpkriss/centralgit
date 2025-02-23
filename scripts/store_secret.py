import os
import boto3

# AWS Secrets Manager client
client = boto3.client('secretsmanager', region_name='us-east-1')

# Directory where secrets are stored
secrets_dir = "secrets"

# Iterate over each secret file and store it in AWS Secrets Manager
for secret_file in os.listdir(secrets_dir):
    secret_name = secret_file.replace(".txt", "")  # Use filename as secret name
    secret_path = os.path.join(secrets_dir, secret_file)

    with open(secret_path, "r") as file:
        secret_value = file.read().strip()

    # Check if the secret exists
    try:
        client.get_secret_value(SecretId=secret_name)
        client.update_secret(SecretId=secret_name, SecretString=secret_value)
        print(f"Updated existing secret: {secret_name}")
    except client.exceptions.ResourceNotFoundException:
        client.create_secret(Name=secret_name, SecretString=secret_value)
        print(f"Created new secret: {secret_name}")



