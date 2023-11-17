#!/usr/bin/env python3
import git
import re
import json
from pygments.lexers import guess_lexer
from pathlib import Path
from gitignore_parser import rule_from_pattern, handle_negation
import os



def norm_path(path):
    if type(path) == list:
        return [Path(p).as_posix() for p in path]
    return Path(path).as_posix()

def parse_gitignore(path=None, patterns=[], base_dir=None):
    rules = []

    # Handle file patterns first
    if path:
        if base_dir is None:
            base_dir = os.path.dirname(path)
        with open(path) as ignore_file:
            counter = 0
            for line in ignore_file:
                counter += 1
                line = line.rstrip('\n')
                rule = rule_from_pattern(line, base_path=Path(base_dir).resolve(),
                                         source=(path, counter))
                if rule:
                    rules.append(rule)

    # Handle patterns provided directly
    counter = 0
    for pattern in patterns:
        counter += 1
        rule = rule_from_pattern(pattern, base_path=Path(base_dir).resolve() if base_dir else None,
                                 source=('patterns_list', counter))
        if rule:
            rules.append(rule)

    # Return the matcher function
    if not any(r.negation for r in rules):
        return lambda file_path: any(r.match(file_path) for r in rules)
    else:
        return lambda file_path: handle_negation(file_path, rules)

def get_files(directory_path='.', ignore_patterns=[], ignore_file=""):
    matches = parse_gitignore( ignore_file, ignore_patterns)
    all_files = []
    for dirpath, dirnames, filenames in os.walk(directory_path):
        # Modifying dirnames in-place to exclude ignored directories.
        # This will prevent os.walk from traversing these directories.
        dirnames[:] = [d for d in dirnames if not matches(os.path.join(dirpath, d))]
        for filename in filenames:
            full_file_path = os.path.join(dirpath, filename)
            if not matches(full_file_path):
                all_files.append(full_file_path)
    return norm_path(all_files)



def detect_language(file_path):
    """Enhanced version of detect_language to improve requirements file detection."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            lexer = guess_lexer(content)
            filename = Path(file_path).name
           
            # If lexer fails to recognize Dockerfile, check for common Docker commands
            if lexer.name == "Text" or lexer.name == "GDScript":
                
                # Check for common Docker commands
                docker_commands = ["FROM", "WORKDIR", "COPY", "RUN", "CMD", "ENTRYPOINT"]
                if any(command in content for command in docker_commands) or filename == "Dockerfile" or filename.endswith(".dockerfile"):
                    return "dockerfile"
            
                
                # Check for content structure that looks like package requirements
                requirement_patterns = ["==", ">=", "<=", ">", "<"]
                requirement_lines = [line for line in content.splitlines() if any(pattern in line for pattern in requirement_patterns)]
                if len(requirement_lines) >= 1:
                    return "requirements"

            return lexer.name
    except Exception:
        return None


def load_language_config():
    script_directory = Path(__file__).parent
    config_path = script_directory / "languages_config.json"
    
    with open(config_path, "r") as config_file:
        return json.load(config_file)

def categorize_files(files, language_config, auxiliaries_file):
    categorized_files = {
        "code": {},
        "datasource": [],
        "pipeline": [],
        "dockerfile": [],
        "requirements": [],
        "auxiliaries": [],
        "unknown": []
    }

    matches_buildignore = parse_gitignore(auxiliaries_file)

    for f in files:
        
        if matches_buildignore(f):
            categorized_files["auxiliaries"].append(f)
            continue
        
        lang = detect_language(f)
        file_extension = Path(f).suffix    
        
        if lang in categorized_files:
            categorized_files[lang].append(f)
            continue
            
        if lang and lang in language_config:
            if lang not in categorized_files["code"]:
                categorized_files["code"][lang] = []
            categorized_files["code"][lang].append(f)
            continue

        # Categorize by file extension for known languages
        for language, config in language_config.items():
            if "file_extension" in config and config["file_extension"] == file_extension:
                if language not in categorized_files["code"]:
                    categorized_files["code"][language] = []
                categorized_files["code"][language].append(f)
                break
        else: 
            # Check for YAML or JSON content by file extension
            if file_extension in [".yaml", ".yml"]:
                with open(f, 'r') as file:
                    content = file.read()
                    if '"pipeline":' in content:
                        categorized_files["pipeline"].append(f)
                    else:
                        categorized_files["unknown"].append(f)
            elif file_extension == ".json":
                with open(f, 'r') as file:
                    content = file.read()
                    if '"repo":' in content:
                        categorized_files["datasource"].append(f)
                    else:
                        categorized_files["unknown"].append(f)
            else:
                categorized_files["unknown"].append(f)

    return categorized_files


def structure_data(input_data, repo_name = None):
       
    images = {}
    
    # Helper function to find a file based on directory and then filename
    def find_file(base_dir, filename, file_list):
        # First, try matching based on directory
        for file in file_list:
            if base_dir in file:
                return file
        
        # If not found, try matching based on filename
        for file in file_list:
            if filename in file:
                return file
        
        # If still not found, return empty string
        return ''
    
    # For each code file, check and match the other files
    for lang, code_files in input_data['code'].items():
        for code_file in code_files:
            # Extract the base directory and filename from the path
            base_dir = os.path.dirname(code_file)
            filename = os.path.basename(code_file).rsplit('.', 1)[0]
            
            # Initialize the image dictionary
            image_dict = {
                'code': code_file,
                'dockerfile': find_file(base_dir, filename, input_data['dockerfile']),
                'pipeline': find_file(base_dir, filename, input_data['pipeline']),
                'datasource': find_file(base_dir, filename, input_data['datasource']),
                'requirements': find_file(base_dir, filename, input_data['requirements']),
                'dependencies': []
            }
            
            # Extract the image name
            image_name = os.path.basename(base_dir) if base_dir else filename
            
            # Add to the images dictionary
            images[image_name] = image_dict
    
    # Construct the final structured data
    structured_data = {
        "project": repo_name,
        'images': images,
        'auxiliaries': input_data['auxiliaries'],
        'unknown': input_data['unknown']
    }
    return structured_data
    

def extract_files_from_dockerfile(file_path):
    if not file_path or not os.path.exists(file_path):
        return []

    dockerfile_dir = os.path.dirname(file_path)

    with open(file_path, 'r') as f:
        content = f.read()

    # Extract all files/folders from COPY or ADD directives
    files = re.findall(r'(COPY|ADD)\s+([\S]+)\s', content)

    # Join the Dockerfile's directory with the source files/folders to make them relative to the repo root
    # and normalize the path
    resolved_paths = [os.path.normpath(os.path.join(dockerfile_dir, f[1])) for f in files]

    # Append trailing slash to directories
    for idx, path in enumerate(resolved_paths):
        if os.path.isdir(path) and not path.endswith('/'):
            resolved_paths[idx] = path + '/'

    # Replace the relative paths in the Dockerfile content with the resolved absolute paths
    for (cmd, rel_path), abs_path in zip(files, resolved_paths):
        content = content.replace(f"{cmd} {rel_path}", f"{cmd} {abs_path}")

    # Optionally write the changes back to the Dockerfile
    with open(file_path, 'w') as f:
        f.write(content)

    return resolved_paths

def update_dependencies(data):
    for image_name, image_data in data["images"].items():
        dockerfile_path = image_data["dockerfile"]
        referenced_files = extract_files_from_dockerfile(dockerfile_path)

        for ref_file in referenced_files:
            if ref_file not in data["auxiliaries"] and ref_file not in data["unknown"]:
                if ref_file != image_data["code"] and ref_file != image_data["requirements"]:
                    image_data["dependencies"].append(ref_file)
    return data
    
            
        
def main():
    repo = Path(os.environ.get("REPO_NAME"))
    
    files = get_files(directory_path=".", ignore_patterns=[".git", ".auxiliaries","Pachykouda-Jenkins-Pipeline"], ignore_file=".gitignore")
    
    language_config = load_language_config()
    categorized_files = categorize_files(files, language_config, ".auxiliaries")
    
    stuctured = structure_data(categorized_files, str(repo))
    updated = update_dependencies(stuctured)
        
    with  open("repo_structure.json", "w") as f:
        f.write(json.dumps(updated, indent=4))

if __name__ == "__main__":
    main()
