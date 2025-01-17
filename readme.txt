# Virtual GitHub Clone

A **Python-based** minimalistic **Git-like repository system** for **local and cloud repository management**. This system supports basic version control operations such as **adding files, committing changes, pushing to a cloud repository, and branch management**.

## Features

- **Initialize a new repository.**  
- **Add files to the index.**  
- **Commit changes to the local repository.**  
- **Push changes from the local to the cloud repository.**  
- **Branch creation and switching.**  

## Getting Started

### Prerequisites

- **Python 3.x installed on your system.**  
- **Basic knowledge of Python and command-line tools.**  

### Installation

1. Clone this repository or download the script.  
2. Place the script in your working directory.  
3. Create folders named `<local>` and `<cloud>` in your project directory (or specify your folder names in the script).  

---

## Usage

### 1. Initialize a Repository

Create a new repository in the specified folder.

```bash
python virtual_github_clone.py init <repo_name>
```

**Example:**

```bash
python virtual_github_clone.py init local
```

---

### 2. Add Files to the Repository

Add a file to the staging area (index).

```bash
python virtual_github_clone.py add <file_path>
```

**Example:**

```bash
python virtual_github_clone.py add example.txt
```

---

### 3. Commit Changes

Commit all staged files with a message.

```bash
python virtual_github_clone.py commit -m "<commit_message>"
```

**Example:**

```bash
python virtual_github_clone.py commit -m "Initial commit"
```

---

### 4. Push to Cloud Repository

Push the local commits to the cloud repository.

```bash
python virtual_github_clone.py push
```

---

### 5. Branch Management

#### Create a New Branch

```bash
python virtual_github_clone.py branch <branch_name> --create
```

**Example:**

```bash
python virtual_github_clone.py branch feature-xyz --create
```

#### Switch to a Branch

```bash
python virtual_github_clone.py branch <branch_name> --switch
```

**Example:**

```bash
python virtual_github_clone.py branch main --switch
```

---

## Directory Structure

```
project_directory/
├── local/
│   ├── .git/
│       ├── objects/
│       ├── refs/
│       ├── HEAD
│       ├── branches.json
├── cloud/
│   ├── .git/
│       ├── objects/
│       ├── refs/
│       ├── branches.json
```

---

## Notes

1. The `<local>` folder simulates your local repository.  
2. The `<cloud>` folder simulates your remote repository.  
3. Branching supports creating and switching between branches but does not include advanced merging.  

Feel free to extend this system for more features like **merging, conflict resolution, or detailed logs.** 🚀
