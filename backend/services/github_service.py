# backend/services/github_service.py
import os
import base64
import requests
import tempfile
import shutil
import subprocess
from pathlib import Path
from fastapi import HTTPException
from typing import Dict, List, Tuple

def parse_github_url(repo_url: str) -> tuple:
    """Parse GitHub URL to extract owner and repo name"""
    repo_url = repo_url.strip()
    
    # Remove common prefixes
    for prefix in ["https://github.com/", "http://github.com/", "github.com/"]:
        if repo_url.startswith(prefix):
            repo_url = repo_url.replace(prefix, "")
    
    repo_url = repo_url.rstrip("/").replace(".git", "")
    parts = repo_url.split("/")
    
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL format. Expected: owner/repo")
    
    return parts[0], parts[1]

def clone_and_analyze_repo(repo_url: str, github_token: str = None) -> dict:
    """Clone repo to temp directory, analyze it, then delete (supports private repos)"""
    temp_dir = None
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="repovision_")
        print(f"📦 Cloning repository to: {temp_dir}")
        
        # If token provided, inject it into the URL for authentication
        clone_url = repo_url
        if github_token and "github.com" in repo_url:
            # Convert https://github.com/user/repo to https://token@github.com/user/repo
            clone_url = repo_url.replace("https://github.com", f"https://{github_token}@github.com")
            clone_url = clone_url.replace("http://github.com", f"https://{github_token}@github.com")
            print(f"🔒 Using authenticated access for private repository")
        
        # Clone the repo (shallow clone for speed)
        clone_cmd = ["git", "clone", "--depth", "1", clone_url, temp_dir]
        result = subprocess.run(
            clone_cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"Git clone failed: {result.stderr}")
        
        print(f"✅ Repository cloned successfully")
        
        # Analyze the cloned repository
        repo_data = analyze_local_repo(temp_dir, repo_url)
        
        return repo_data
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Repository clone timed out")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to clone repo: {str(e)}")
    finally:
        # Cleanup: Delete temp directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"🗑️ Cleaned up temp directory")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete temp dir: {e}")

def analyze_local_repo(repo_path: str, repo_url: str) -> dict:
    """Analyze locally cloned repository"""
    owner, repo_name = parse_github_url(repo_url)
    
    # Get repo info from GitHub API (for metadata)
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    github_token = os.getenv("GITHUB_TOKEN", None)
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    
    try:
        repo_response = requests.get(api_url, headers=headers, timeout=10)
        repo_info = repo_response.json() if repo_response.status_code == 200 else {}
    except:
        repo_info = {}
    
    print("📂 Building file tree from cloned repo...")
    
    # Build file structure
    file_structure = build_file_tree_from_disk(repo_path)
    
    print("📄 Reading important file contents...")
    
    # Read important files
    file_contents = read_important_files(repo_path)
    
    print(f"✅ Analyzed {len(file_contents)} files")
    
    # Read README
    readme_content = read_readme_from_disk(repo_path)
    
    # Detect languages
    languages = detect_languages(repo_path)
    
    # Analyze dependencies
    dependencies = analyze_dependencies_from_disk(repo_path)
    
    return {
        "name": repo_info.get("name", repo_name),
        "description": repo_info.get("description", ""),
        "language": repo_info.get("language", detect_primary_language(languages)),
        "languages": languages,
        "file_structure": file_structure,
        "file_contents": file_contents,
        "dependencies": dependencies,
        "readme": readme_content,
        "stars": repo_info.get("stargazers_count", 0),
        "forks": repo_info.get("forks_count", 0),
        "open_issues": repo_info.get("open_issues_count", 0),
        "topics": repo_info.get("topics", []),
        "total_files_analyzed": len(file_contents)
    }

def build_file_tree_from_disk(repo_path: str, max_depth: int = 5) -> dict:
    """Build file tree from local repository"""
    
    # Directories to skip
    skip_dirs = {
        '.git', 'node_modules', '__pycache__', '.next', 'dist', 'build',
        'coverage', '.venv', 'venv', 'env', '.idea', '.vscode', 'target'
    }
    
    def build_tree(path: str, depth: int = 0) -> dict:
        if depth > max_depth:
            return {}
        
        tree = {}
        try:
            for item in os.listdir(path):
                if item.startswith('.') and item != '.env':
                    continue
                
                item_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    if item not in skip_dirs:
                        tree[item] = {
                            "type": "dir",
                            "path": os.path.relpath(item_path, repo_path),
                            "contents": build_tree(item_path, depth + 1)
                        }
                else:
                    # File info
                    size = os.path.getsize(item_path)
                    extension = item.split(".")[-1] if "." in item else "none"
                    
                    # Determine purpose
                    purpose = classify_file_purpose(item, os.path.relpath(item_path, repo_path))
                    
                    tree[item] = {
                        "type": "file",
                        "path": os.path.relpath(item_path, repo_path),
                        "size": size,
                        "extension": extension,
                        "purpose": purpose
                    }
        except PermissionError:
            pass
        
        return tree
    
    return build_tree(repo_path)

def classify_file_purpose(filename: str, filepath: str) -> str:
    """Classify file purpose based on name and path"""
    name_lower = filename.lower()
    path_lower = filepath.lower()
    
    if any(x in name_lower for x in ["test", "spec", ".test.", "_test"]):
        return "testing"
    elif any(x in name_lower for x in ["config", "setup", ".env", "settings"]):
        return "configuration"
    elif any(x in name_lower for x in ["model", "schema", "entity"]):
        return "data_model"
    elif any(x in name_lower for x in ["route", "endpoint", "api", "controller"]):
        return "api"
    elif any(x in name_lower for x in ["component", "view", "page", "screen"]):
        return "ui"
    elif any(x in name_lower for x in ["util", "helper", "tool"]):
        return "utility"
    elif any(x in name_lower for x in ["service", "provider", "manager"]):
        return "service"
    elif any(x in name_lower for x in ["middleware", "interceptor"]):
        return "middleware"
    elif filename in ["package.json", "requirements.txt", "Cargo.toml", "go.mod"]:
        return "dependencies"
    else:
        return "general"

def read_important_files(repo_path: str, max_files: int = 100) -> dict:
    """Read important files from local repository"""
    important_files = {}
    
    # Important file patterns
    important_patterns = [
        "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.java", "*.go", "*.rs",
        "*.cpp", "*.c", "*.h", "*.rb", "*.php", "*.swift", "*.kt",
        "package.json", "requirements.txt", "Cargo.toml", "go.mod",
        "Dockerfile", "docker-compose.yml", "*.yml", "*.yaml", "*.json"
    ]
    
    code_extensions = {
        'py', 'js', 'jsx', 'ts', 'tsx', 'java', 'go', 'rs', 'cpp', 'c', 'h',
        'rb', 'php', 'swift', 'kt', 'scala', 'sh', 'yml', 'yaml', 'json', 'xml'
    }
    
    skip_dirs = {
        '.git', 'node_modules', '__pycache__', '.next', 'dist', 'build',
        'coverage', '.venv', 'venv', 'env', '.idea', '.vscode', 'target'
    }
    
    file_count = 0
    
    for root, dirs, files in os.walk(repo_path):
        # Remove skip directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file_count >= max_files:
                break
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            
            # Check if should read this file
            extension = file.split(".")[-1] if "." in file else ""
            size = os.path.getsize(file_path)
            
            # Read if: code file or important config, and under 100KB
            if (extension in code_extensions or file in [
                "package.json", "requirements.txt", "Dockerfile", "README.md"
            ]) and size < 100000:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    purpose = classify_file_purpose(file, rel_path)
                    
                    important_files[rel_path] = {
                        "content": content[:15000],  # First 15KB
                        "size": size,
                        "extension": extension,
                        "purpose": purpose,
                        "full_size": len(content)
                    }
                    
                    file_count += 1
                    print(f"  ✓ Read: {rel_path}")
                    
                except Exception as e:
                    print(f"  ✗ Failed to read {rel_path}: {e}")
        
        if file_count >= max_files:
            break
    
    return important_files

def read_readme_from_disk(repo_path: str) -> str:
    """Read README file from repository"""
    readme_files = ["README.md", "README.txt", "README", "readme.md"]
    
    for readme_name in readme_files:
        readme_path = os.path.join(repo_path, readme_name)
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except:
                pass
    
    return ""

def detect_languages(repo_path: str) -> dict:
    """Detect programming languages in repository"""
    languages = {}
    
    language_extensions = {
        'Python': ['.py'],
        'JavaScript': ['.js', '.jsx'],
        'TypeScript': ['.ts', '.tsx'],
        'Java': ['.java'],
        'Go': ['.go'],
        'Rust': ['.rs'],
        'C++': ['.cpp', '.cc', '.cxx'],
        'C': ['.c', '.h'],
        'Ruby': ['.rb'],
        'PHP': ['.php'],
        'Swift': ['.swift'],
        'Kotlin': ['.kt']
    }
    
    for root, dirs, files in os.walk(repo_path):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__'}]
        
        for file in files:
            ext = os.path.splitext(file)[1]
            for lang, exts in language_extensions.items():
                if ext in exts:
                    languages[lang] = languages.get(lang, 0) + 1
    
    return languages

def detect_primary_language(languages: dict) -> str:
    """Detect primary language from language counts"""
    if not languages:
        return "Unknown"
    return max(languages, key=languages.get)

def analyze_dependencies_from_disk(repo_path: str) -> dict:
    """Analyze dependencies from local repository"""
    dependencies = {}
    
    dependency_files = {
        "package.json": "npm",
        "requirements.txt": "pip",
        "Cargo.toml": "cargo",
        "go.mod": "go",
        "pom.xml": "maven",
        "build.gradle": "gradle",
        "composer.json": "composer"
    }
    
    for dep_file, package_manager in dependency_files.items():
        file_path = os.path.join(repo_path, dep_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                dependencies[package_manager] = content[:3000]
            except:
                pass
    
    return dependencies

def format_file_structure(structure: dict, indent: int = 0, max_items: int = 50) -> str:
    """Format file structure for prompt with better organization"""
    result = []
    count = 0
    
    for name, info in structure.items():
        if count >= max_items:
            result.append(f"{'  ' * indent}... ({len(structure) - count} more items)")
            break
            
        prefix = "  " * indent
        if isinstance(info, dict):
            if info.get("type") == "dir":
                result.append(f"{prefix}📁 {name}/")
                if "contents" in info:
                    result.append(format_file_structure(info["contents"], indent + 1, max_items))
            else:
                purpose = info.get("purpose", "")
                size = info.get("size", 0)
                ext = info.get("extension", "")
                result.append(f"{prefix}📄 {name} [{ext}] ({purpose}, {size}B)")
        count += 1
    
    return "\n".join(result)

def format_file_contents(contents: dict) -> str:
    """Format file contents for prompt with better structure"""
    result = []
    
    for filepath, file_data in list(contents.items())[:30]:  # Limit to 30 files
        if isinstance(file_data, dict):
            content = file_data.get("content", "")
            purpose = file_data.get("purpose", "")
            extension = file_data.get("extension", "")
            full_size = file_data.get("full_size", 0)
            
            result.append(f"\n{'='*60}")
            result.append(f"FILE: {filepath}")
            result.append(f"Type: {extension} | Purpose: {purpose} | Size: {full_size}B")
            result.append(f"{'='*60}")
            result.append(content[:2000])  # Show first 2KB
            if full_size > 2000:
                result.append(f"\n... (truncated, {full_size - 2000} bytes remaining)")
        else:
            # Old format (backward compatibility)
            result.append(f"\n{'='*60}")
            result.append(f"FILE: {filepath}")
            result.append(f"{'='*60}")
            result.append(str(file_data)[:1000])
    
    return "\n".join(result)

def fetch_file_content(owner: str, repo: str, file_path: str, headers: dict) -> str:
    """Fetch content of a specific file - kept for backward compatibility"""
    return ""

def fetch_readme(api_url: str, headers: dict) -> str:
    """Fetch README content - kept for backward compatibility"""
    return ""

def build_detailed_file_tree(
    contents: list, 
    api_url: str, 
    headers: dict, 
    owner: str, 
    repo: str, 
    deep_fetch: bool = True, 
    depth: int = 0, 
    max_depth: int = 4
) -> dict:
    """Build detailed tree structure - kept for backward compatibility"""
    return {}

def fetch_important_files_deep(contents: list, owner: str, repo: str, headers: dict, file_structure: dict) -> dict:
    """Fetch important files - kept for backward compatibility"""
    return {}

def analyze_dependencies(contents: list, owner: str, repo: str, headers: dict) -> dict:
    """Analyze dependencies - kept for backward compatibility"""
    return {}

# Keep old function for backward compatibility
def fetch_github_repo_structure(repo_url: str, deep_fetch: bool = True, github_token: str = None) -> dict:
    """Main entry point - now uses git clone instead of API"""
    return clone_and_analyze_repo(repo_url, github_token)