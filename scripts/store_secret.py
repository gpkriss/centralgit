import boto3
import json
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SECRET_NAME = f"github-secrets-{os.getenv('GITHUB_REPOSITORY', 'default-repo').replace('/', '-')}"

def store_secrets(secret_name, secret_data, region):
    client = boto3.client("secretsmanager", region_name=region)

    try:
        # Convert dict to JSON string
        secret_string = json.dumps(secret_data)
        
        # Try creating the secret first
        client.create_secret(Name=secret_name, SecretString=secret_string)
        print(f" Secret {secret_name} created successfully!")
    except client.exceptions.ResourceExistsException:
        # If secret already exists, update it
        client.update_secret(SecretId=secret_name, SecretString=secret_string)
        print(f" Secret {secret_name} updated successfully!")

# Read secrets from file (passed from GitHub Actions)
with open("secrets.json", "r") as file:
    secrets = json.load(file)

print(f" Total Secrets Found: {len(secrets)}")
print(f" Secret Names: {', '.join(secrets.keys())}")

# Store all secrets in AWS Secrets Manager
store_secrets(SECRET_NAME, secrets, AWS_REGION)

