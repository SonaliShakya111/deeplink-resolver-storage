import requests
import json
from datetime import datetime

# Configuration
GITHUB_TOKEN = {TOKEN_PAT}
FORKED_REPO_OWNER = "SonaliShakya111"
FORKED_REPO_NAME = "deeplink-resolver-storage"
UPSTREAM_REPO_OWNER = "ONDC-Official"
UPSTREAM_REPO_NAME = "deeplink-resolver-storage"
BASE_BRANCH = "master"
GITHUB_API_URL = "https://api.github.com"

# Headers for API Requests
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

def sync_master_branch():
    """Sync the master branch of the forked repository with the upstream repository."""
    sync_url = f"{GITHUB_API_URL}/repos/{FORKED_REPO_OWNER}/{FORKED_REPO_NAME}/merge-upstream"
    payload = {"branch": BASE_BRANCH}
    response = requests.post(sync_url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print("Master branch synced successfully.")
    else:
        print("Failed to sync master branch:", response.json())

def create_branch(unique_id):
    """Create a new branch based on the master branch."""
    branch_name = f"update-{unique_id}"
    # Get the latest commit SHA from the master branch
    ref_url = f"{GITHUB_API_URL}/repos/{FORKED_REPO_OWNER}/{FORKED_REPO_NAME}/git/ref/heads/{BASE_BRANCH}"
    response = requests.get(ref_url, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to get master branch SHA:", response.json())
        return None

    sha = response.json()["object"]["sha"]

    # Create the new branch
    new_branch_url = f"{GITHUB_API_URL}/repos/{FORKED_REPO_OWNER}/{FORKED_REPO_NAME}/git/refs"
    payload = {
        "ref": f"refs/heads/{branch_name}",
        "sha": sha
    }
    response = requests.post(new_branch_url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        print(f"Branch '{branch_name}' created successfully.")
        return branch_name
    else:
        print("Failed to create branch:", response.json())
        return None

def add_file_to_branch(branch_name, unique_id, json_payload):
    """Add a file to the new branch with the unique ID and JSON payload."""
    file_path = f"{unique_id}.json"
    file_content = json.dumps(json_payload, indent=4)
    encoded_content = file_content.encode("utf-8").decode("utf-8")

    url = f"{GITHUB_API_URL}/repos/{FORKED_REPO_OWNER}/{FORKED_REPO_NAME}/contents/{file_path}"
    payload = {
        "message": f"Add file {file_path}",
        "content": encoded_content,
        "branch": branch_name
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        print(f"File '{file_path}' added successfully to branch '{branch_name}'.")
    else:
        print("Failed to add file:", response.json())

def create_pull_request(branch_name):
    """Create a pull request from the forked repository to the upstream repository."""
    pr_url = f"{GITHUB_API_URL}/repos/{UPSTREAM_REPO_OWNER}/{UPSTREAM_REPO_NAME}/pulls"
    payload = {
        "title": f"Update from branch {branch_name}",
        "head": f"{FORKED_REPO_OWNER}:{branch_name}",
        "base": BASE_BRANCH,
        "body": f"This PR adds updates from branch '{branch_name}'."
    }
    response = requests.post(pr_url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        print("Pull request created successfully:", response.json()["html_url"])
    else:
        print("Failed to create pull request:", response.json())

def handle_push_event(unique_id, json_payload):
    """Handle the push event: sync master, create branch, add file, and create PR."""
    sync_master_branch()
    branch_name = create_branch(unique_id)
    if branch_name:
        add_file_to_branch(branch_name, unique_id, json_payload)
        create_pull_request(branch_name)

# Example usage
if __name__ == "__main__":
    # Example push request data
    unique_id = "push-12345"
    json_payload = {"example_key": "example_value", "timestamp": datetime.utcnow().isoformat()}

    handle_push_event(unique_id, json_payload)
