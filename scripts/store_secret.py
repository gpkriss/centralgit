import boto3
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SECRET_NAME = f"github-test-secret-{os.getenv('GITHUB_REPOSITORY', 'default-repo').replace('/', '-')}"

def store_secret(secret_name, secret_value, region):
    client = boto3.client("secretsmanager", region_name=region)

    try:
        # Try creating the secret first
        client.create_secret(Name=secret_name, SecretString=secret_value)
        print(f"Secret {secret_name} created successfully!")
    except client.exceptions.ResourceExistsException:
        # If secret already exists, update it
        client.update_secret(SecretId=secret_name, SecretString=secret_value)
        print(f"Secret {secret_name} updated successfully!")

# Read the secret value from file (passed from GitHub Actions)
with open("secret_value.txt", "r") as file:
    secret_value = file.read().strip()

# Store in AWS Secrets Manager
store_secret(SECRET_NAME, secret_value, AWS_REGION)
