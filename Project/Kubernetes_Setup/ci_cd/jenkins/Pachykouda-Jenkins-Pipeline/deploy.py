#!/usr/bin/env python3

from pathlib import Path
import python_pachyderm
import uuid
import grpc
import json
import yaml
import git
import os

import pprint

def norm_path(path):
    if type(path) == list:
        return [Path(p).as_posix() for p in path]
    return Path(path).as_posix()

def get_changed_files(repo_path='.'):
    repo = git.Repo(repo_path)
    changed_files = [item.a_path for item in repo.index.diff(None)]
    return norm_path(changed_files)
    
    
def affects_image(changed_files, data):
    """Check if any of the changed files affect one of the images."""
    affected_images = []
    
    for image_name, image_data in data["images"].items():
        for key, value in image_data.items():
            value = norm_path(value)
            print (f"key: {key} \t|  value: {value}")
            if key in ["pipeline", "datasource"]:
                continue 
            else:
                if type(value) == list:
                    if len(set(value) & set(changed_files)) > 0:
                        affected_images.append(image_name)
                        print(f"Image {image_name} is affected by change in {value}")
                        break
                else :
                    if value in changed_files:
                        affected_images.append(image_name)
                        print(f"Image {image_name} is affected by change in {value}")
                        break
                    
    return list(set(affected_images))

def create_missing_values(data, registry):
     
    for image_name, image_data in data["images"].items():
        if image_data["pipeline"] == "":
            #TODO: add support for other languages
            image_data["pipeline"] = {
                "pipeline": {
                    "name": image_name.lower(),
                    "project": {
                        "name": data["project"].lower(),
                    }
                },
                "transform": {
                    "image": f"{registry}/{data['project'].lower()}_{image_name.lower()}:latest",
                    "cmd": ["python3", image_data["code"]],
                },
            }
            
        if image_data["dockerfile"] == "":
            requirements_section = ""
            if image_data["requirements"] != "":
                requirements_section = """
                    COPY {0} /app/{0}
                    RUN pip install -r {0}
                """.format(image_data["requirements"])
                
            dockerfile_content = f"""
                FROM python
                WORKDIR /app
                {requirements_section}
                COPY {image_data["code"]} /app/{image_data["code"]}
                CMD ["python3", "{image_data["code"]}"]                 
            """
            image_data["dockerfile"] = dockerfile_content.strip()
            
    return data

def spec_to_dict(s):
    # Check if string looks like a path.
    if os.path.sep in s or (os.path.altsep and os.path.altsep in s):
        # Check if file exists.
        if os.path.exists(s):
            # If it's a file, return its content.
            with open(s, 'r') as file:
                content = file.read()
        else:
            content = s
    else:
        content = s
    
    # Try to convert content to dictionary.
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError:
            # If it's neither JSON nor YAML, return the content as is.
            return content

def build_docker_image(image_data, DOCKER_REGISTRY, repo_name, output_dir="docker_builds"):

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extracting dockerfile content or path from the image data
    dockerfile_content = image_data.get("dockerfile", "")
    
    # Determine if dockerfile is an inline content or a path
    if "FROM" in dockerfile_content:
        # Create a temporary Dockerfile in the output directory and write the content to it
        temp_dockerfile_name = f"Dockerfile_{uuid.uuid4()}"
        temp_dockerfile_path = os.path.join(output_dir, temp_dockerfile_name)
        
        with open(temp_dockerfile_path, 'w') as temp_file:
            temp_file.write(dockerfile_content)
        
        dockerfile_arg = temp_dockerfile_path
    else:
        dockerfile_arg = dockerfile_content  # Assuming it's a path
    
    # Constructing image name for the print statement
    print("="*80)
    image_name = f"{DOCKER_REGISTRY}/{str(repo_name).lower()}_{image_data['code'].lower()}:latest"
    print(f"Building image {image_name}")
    print("="*80)
    
    # Constructing the command to execute
    cmd = f"/kaniko/executor --context . --dockerfile {dockerfile_arg} --destination {image_name} --cache=true --skip-tls-verify"
    
    # Generate a unique filename for the shell script
    script_name = f"build_{uuid.uuid4()}.sh"
    script_path = os.path.join(output_dir, script_name)
    
    # Write the command to the shell script
    with open(script_path, 'w') as file:
        file.write("#!/bin/sh\n")
        file.write(cmd + "\n")
    
def connect_and_verify_pachyderm(project_name):
    
    # Create a pachyderm client
    print(f"Establishing connection to Pachyderm cluster ")
    client = python_pachyderm.Client(host="heydar20.labs.hpecorp.net", port=30650)

    # Get the list of repos 
    project_ = [project.project.name for project in client.list_project()]
    
    if project_name not in project_:
        print(f"Creating project : {project_name}")
        client.create_project(str(project_name).lower())
    
    return client

def publish_pipelines(pipelines, project_name):
    client = connect_and_verify_pachyderm(project_name)
    
    for pipeline in pipelines:
        pipeline = spec_to_dict(pipeline)
            
        try:
            client.create_pipeline_from_request( python_pachyderm.parse_dict_pipeline_spec(pipeline))
            print(f"Created pipeline {pipeline['pipeline']['name']}")    
       
        except python_pachyderm.RpcError as e:  
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                print(f"Pipeline {pipeline['pipeline']['name']} already exists")
                
                # Deleting the pipeline
                client.delete_pipeline(pipeline['pipeline']['name'], project_name=project_name)
                
                # creating the pipeline again
                client.create_pipeline_from_request( python_pachyderm.parse_dict_pipeline_spec(pipeline))
            else:
                raise e



def publish_datasources(datasources, project_name):
    # TODO
    client = connect_and_verify_pachyderm(project_name)
    
    existing_repos = [repo.repo.name for repo in client.list_repo()]
    
    for datasource in datasources:
        if datasource['repo']['name'] not in existing_repos:
            print(f"Creating new datasource (repo) {datasource['repo']['name']}")
            client.create_repo(datasource['repo']['name'])
        
        for content in datasource["contents"]:
            print(f"Adding file {content['name']} to repo {datasource['repo']['name']}@{datasource['repo']['branch']}")
            with client.commit(datasource['repo']['name'], datasource['repo']['branch']) as commit:
                # Assuming content['url'] is a file path on local machine
                with open(content['url'], 'rb') as file:
                    client.put_file_bytes(commit, content['name'], file.read())



def main():
    
    registry = os.environ["DOCKER_REGISTRY"]
    project = Path(os.environ["REPO_NAME"])
  
    
    with open( "repo_structure.json", "r") as f:
        repo_structure = json.load(f)
      
    print(f"Changes have been deteced in {get_changed_files()}"  )
    for image in affects_image(get_changed_files(), repo_structure):
        build_docker_image(
            image_data= repo_structure["images"][image],
            DOCKER_REGISTRY=registry,
            repo_name=project,
            output_dir="docker_builds")
        #connect_and_verify_pachyderm(project).start_pipeline(repo_structure[image]["pipeline_name"], project_name=project)

    
    reee = [(repo_structure["images"][x]["pipeline"]) for x in repo_structure["images"]]
    print (reee)
    publish_pipelines(reee,"project")
    
        
if __name__ == "__main__":
    main()
