import os
import json
import boto3

# Initialize AWS Secrets Manager client
client = boto3.client('secretsmanager', region_name='us-east-1')  # Change region as needed

def create_or_update_secret(secret_name, secret_value):
    try:
        # Check if the secret exists
        client.get_secret_value(SecretId=secret_name)
        print(f"Updating secret: {secret_name}")
        client.update_secret(SecretId=secret_name, SecretString=secret_value)
    except client.exceptions.ResourceNotFoundException:
        print(f"Creating new secret: {secret_name}")
        client.create_secret(Name=secret_name, SecretString=secret_value)

def main():
    with open("secrets.txt", "r") as file:
        secrets = [line.strip() for line in file.readlines() if line.strip()]

    if not secrets:
        print("No secrets found.")
        return

    print(f"Processing {len(secrets)} secrets...")

    for secret_name in secrets:
        secret_value = os.getenv(secret_name)
        
        if secret_value:
            create_or_update_secret(secret_name, secret_value)
        else:
            print(f"Warning: Secret {secret_name} not found in environment variables!")

if __name__ == "__main__":
    main()


        data = response.json().get("secrets", [])
        if not data:
            break

        secrets.extend([secret["name"] for secret in data])  # Extract only secret names
        page += 1

    return secrets

def store_secret_in_aws(secret_name, secret_value):
    """Store or update a secret in AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=AWS_REGION)

    try:
        client.create_secret(Name=secret_name, SecretString=secret_value)
        print(f"✅ Secret '{secret_name}' copied to AWS Secrets Manager.")
    except client.exceptions.ResourceExistsException:
        client.update_secret(SecretId=secret_name, SecretString=secret_value)
        print(f"🔄 Secret '{secret_name}' updated in AWS Secrets Manager.")

def main():
    secret_names = list_github_secrets()
    if secret_names is None:
        print("❌ Failed to retrieve secrets.")
        return

    print(f"🔍 Total Secrets Found: {len(secret_names)}")

    for secret_name in secret_names:
        secret_value = os.getenv(secret_name)  # Fetch secret value dynamically from env

        if secret_value:
            store_secret_in_aws(secret_name, secret_value)
        else:
            print(f"⚠️ Warning: Secret '{secret_name}' is missing or not set in environment.")

if __name__ == "__main__":
    main()

