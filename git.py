import os
import hashlib
import zlib
import json
import time
import argparse

# Constants
LOCAL_REPO = 'local'  # Local repository directory name
CLOUD_REPO = 'cloud'  # Cloud repository directory name
BRANCH_FILE = 'branches.json'  # File storing branch information


# Utility Functions

def init(repo):
    """Initialize a new Git repository in the specified directory."""
    git_dir = os.path.join(repo, '.git')
    
    # If the .git directory doesn't exist, create the required structure
    if not os.path.exists(git_dir):
        os.makedirs(os.path.join(git_dir, 'objects'), exist_ok=True)
        os.makedirs(os.path.join(git_dir, 'refs', 'heads'), exist_ok=True)
        
        # Create HEAD file to point to the main branch
        with open(os.path.join(git_dir, 'HEAD'), 'w') as f:
            f.write('ref: refs/heads/main\n')
        
        # Initialize branches.json with the 'main' branch
        branches = {"main": []}
        with open(os.path.join(git_dir, BRANCH_FILE), 'w') as f:
            json.dump(branches, f)
        
        print(f'Initialized local repository in {repo}')
    else:
        print(f'.git directory already exists in {repo}')


def init_cloud(repo):
    """Initialize the cloud repository with necessary files and structure."""
    if not os.path.exists(repo):
        os.makedirs(os.path.join(repo, '.git', 'objects'), exist_ok=True)
        os.makedirs(os.path.join(repo, '.git', 'refs', 'heads'), exist_ok=True)
        
        # Create HEAD file and set default to the main branch
        with open(os.path.join(repo, '.git', 'HEAD'), 'w') as f:
            f.write('ref: refs/heads/main\n')
        
        # Initialize branches.json for cloud repo
        branches = {"main": []}
        with open(os.path.join(repo, '.git', BRANCH_FILE), 'w') as f:
            json.dump(branches, f)
        
        print(f'Initialized cloud repository in {repo}')
    else:
        print(f'Cloud repository already exists in {repo}')


def hash_object(data, repo):
    """Hash the given data, compress it, and store it in the object database."""
    header = f'blob {len(data)}\0'.encode() + data
    sha1 = hashlib.sha1(header).hexdigest()
    path = os.path.join(repo, '.git', 'objects', sha1[:2], sha1[2:])
    
    # Ensure the directory exists before saving the object
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Compress and save the object
    with open(path, 'wb') as f:
        f.write(zlib.compress(header))
    
    return sha1


def add(file_path, repo):
    """Add a file to the staging area (index) in the repository."""
    with open(file_path, 'rb') as f:
        data = f.read()
    
    sha1 = hash_object(data, repo)
    index_path = os.path.join(repo, '.git', 'index.json')
    
    # Load existing index or create a new one
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            index = json.load(f)
    else:
        index = {}
    
    # Add file and its corresponding hash to the index
    index[file_path] = sha1
    with open(index_path, 'w') as f:
        json.dump(index, f)
    
    print(f'Added {file_path} to index with hash {sha1}')


def commit(message, repo):
    """Commit the staged changes (files in the index) to the repository."""
    index_path = os.path.join(repo, '.git', 'index.json')
    
    # If there are no changes to commit, inform the user
    if not os.path.exists(index_path):
        print("No changes to commit.")
        return
    
    # Read the index and prepare the commit data
    with open(index_path, 'r') as f:
        index = json.load(f)
    
    timestamp = int(time.time())
    commit_data = {
        'message': message,
        'timestamp': timestamp,
        'files': index
    }
    
    # Hash the commit data
    sha1 = hash_object(json.dumps(commit_data).encode(), repo)

    # Update the branch history with the new commit
    with open(os.path.join(repo, '.git', BRANCH_FILE), 'r') as f:
        branches = json.load(f)

    current_branch = get_current_branch(repo)
    branches[current_branch].append(sha1)

    # Save the updated branch information
    with open(os.path.join(repo, '.git', BRANCH_FILE), 'w') as f:
        json.dump(branches, f)

    print(f'Committed with hash {sha1}')


def push(local_repo, cloud_repo):
    """Push the local repository changes to the cloud repository."""
    # Initialize the cloud repository if it doesn't exist
    init_cloud(cloud_repo)

    # Read the local branches and commit information
    with open(os.path.join(local_repo, '.git', BRANCH_FILE), 'r') as f:
        local_branches = json.load(f)

    cloud_branch_file = os.path.join(cloud_repo, '.git', BRANCH_FILE)
    
    # Read the cloud branch information, or create an empty one if it doesn't exist
    if os.path.exists(cloud_branch_file):
        with open(cloud_branch_file, 'r') as f:
            cloud_branches = json.load(f)
    else:
        cloud_branches = {}

    # Update cloud branches with local commits
    for branch, commits in local_branches.items():
        if branch in cloud_branches:
            cloud_branches[branch].extend(commit for commit in commits if commit not in cloud_branches[branch])
        else:
            cloud_branches[branch] = commits

    # Save the updated branch information to the cloud
    with open(cloud_branch_file, 'w') as f:
        json.dump(cloud_branches, f)

    print(f'Pushed changes to {cloud_repo}')


def create_branch(branch_name, repo):
    """Create a new branch in the repository."""
    with open(os.path.join(repo, '.git', BRANCH_FILE), 'r') as f:
        branches = json.load(f)

    current_branch = get_current_branch(repo)
    branches[branch_name] = branches[current_branch].copy()

    # Save the new branch to the branch list
    with open(os.path.join(repo, '.git', BRANCH_FILE), 'w') as f:
        json.dump(branches, f)

    print(f'Created branch {branch_name}')


def get_current_branch(repo):
    """Get the name of the current branch."""
    with open(os.path.join(repo, '.git', 'HEAD'), 'r') as f:
        return f.read().strip().split('/')[-1]


def switch_branch(branch_name, repo):
    """Switch to a different branch in the repository."""
    with open(os.path.join(repo, '.git', BRANCH_FILE), 'r') as f:
        branches = json.load(f)

    if branch_name not in branches:
        print(f'Branch {branch_name} does not exist.')
        return

    # Update the HEAD file to point to the new branch
    with open(os.path.join(repo, '.git', 'HEAD'), 'w') as f:
        f.write(f'ref: refs/heads/{branch_name}\n')

    print(f'Switched to branch {branch_name}')


def main():
    """Main function to handle command-line input and invoke the appropriate functions."""
    parser = argparse.ArgumentParser(description='Virtual GitHub Clone')
    subparsers = parser.add_subparsers(dest='command')

    # Command for initializing a new repository
    init_parser = subparsers.add_parser('init', help='Initialize a new repository')
    init_parser.add_argument('repo', help='Repository name')

    # Command for adding files to the staging area
    add_parser = subparsers.add_parser('add', help='Add a file to the index')
    add_parser.add_argument('file', help='File to add')

    # Command for committing changes
    commit_parser = subparsers.add_parser('commit', help='Commit changes')
    commit_parser.add_argument('-m', '--message', required=True, help='Commit message')

    # Command for pushing changes to the cloud repository
    push_parser = subparsers.add_parser('push', help='Push to cloud repository')

    # Command for managing branches
    branch_parser = subparsers.add_parser('branch', help='Manage branches')
    branch_parser.add_argument('branch_name', help='Branch name')
    branch_parser.add_argument('--create', action='store_true', help='Create a new branch')
    branch_parser.add_argument('--switch', action='store_true', help='Switch to the branch')

    args = parser.parse_args()

    # Execute the appropriate function based on user input
    if args.command == 'init':
        init(args.repo)
    elif args.command == 'add':
        add(args.file, LOCAL_REPO)
    elif args.command == 'commit':
        commit(args.message, LOCAL_REPO)
    elif args.command == 'push':
        push(LOCAL_REPO, CLOUD_REPO)
    elif args.command == 'branch':
        if args.create:
            create_branch(args.branch_name, LOCAL_REPO)
        elif args.switch:
            switch_branch(args.branch_name, LOCAL_REPO)
    else:
        print("Unknown command. Use 'init', 'add', 'commit', 'push', or 'branch'.")


if __name__ == "__main__":
    main()
