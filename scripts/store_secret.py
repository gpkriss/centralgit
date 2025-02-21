import os
import requests
import boto3

# GitHub API credentials
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "gpkriss"  # Change if needed
REPO_NAME = "centralgit"  # Change if needed
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# GitHub API URL for listing secrets
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def list_github_secrets():
    """Fetch all GitHub repository secrets with pagination."""
    secrets = []
    page = 1

    while True:
        response = requests.get(f"{GITHUB_API_URL}?per_page=30&page={page}", headers=HEADERS)

        if response.status_code != 200:
            print(f"❌ Error fetching secrets: {response.text}")
            return None

        data = response.json().get("secrets", [])
        if not data:
            break

        secrets.extend(data)
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
    secrets = list_github_secrets()
    if secrets is None:
        print("❌ Failed to retrieve secrets.")
        return

    print(f"🔍 Total Secrets Found: {len(secrets)}")

    for secret in secrets:
        secret_name = secret["name"]
        secret_value = os.getenv(secret_name)  # Fetch the actual secret value from the environment

        if secret_value:
            store_secret_in_aws(secret_name, secret_value)
        else:
            print(f"⚠️ Warning: No value found for secret '{secret_name}'. Skipping.")

if __name__ == "__main__":
    main()

