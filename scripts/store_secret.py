import os
import base64
import json
import requests
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

# GitHub API details
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Headers for GitHub API
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_secrets():
    """Fetches all secrets from the repository."""
    secrets = []
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Failed to fetch secrets: {response.json()}")
            return []
        
        data = response.json()
        if "secrets" not in data or not data["secrets"]:
            break  # No more secrets
        
        secrets.extend(data["secrets"])
        page += 1
    
    return secrets

def get_public_key():
    """Gets the repository's public key required to encrypt secrets."""
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/public-key"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to fetch public key: {response.json()}")
        return None, None
    
    data = response.json()
    return data["key_id"], data["key"]

def encrypt_secret(public_key, secret_value):
    """Encrypts a secret value using the repository’s public key."""
    key_bytes = base64.b64decode(public_key.encode("utf-8"))
    public_key = serialization.load_der_public_key(key_bytes)
    
    encrypted = public_key.encrypt(
        secret_value.encode("utf-8"),
        padding.PKCS1v15()
    )
    
    return base64.b64encode(encrypted).decode("utf-8")

def add_secret(secret_name, secret_value, key_id, encrypted_value):
    """Adds a secret to the repository."""
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{secret_name}"
    
    payload = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    
    response = requests.put(url, headers=HEADERS, data=json.dumps(payload))
    
    if response.status_code in [201, 204]:
        print(f"Secret {secret_name} added successfully.")
    else:
        print(f"Failed to add secret {secret_name}: {response.json()}")

def main():
    secrets = get_secrets()
    
    if not secrets:
        print("No secrets found.")
        return
    
    key_id, public_key = get_public_key()
    
    if not key_id or not public_key:
        print("Could not retrieve public key for encryption.")
        return
    
    for secret in secrets:
        secret_name = secret["name"]
        
        # Using AWS Credentials as secret values
        if secret_name == "AWS_ACCESS_KEY_ID":
            secret_value = AWS_ACCESS_KEY_ID
        elif secret_name == "AWS_SECRET_ACCESS_KEY":
            secret_value = AWS_SECRET_ACCESS_KEY
        else:
            continue  # Skip non-AWS secrets

        encrypted_value = encrypt_secret(public_key, secret_value)
        add_secret(secret_name, secret_value, key_id, encrypted_value)

if __name__ == "__main__":
    main()

