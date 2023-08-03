import subprocess
import json
import os
from concurrent.futures import ThreadPoolExecutor

def build_docker_image(build_args, tag, context, log_file_name="build.log"):
    command = ["docker", "build"]
    for key, value in build_args.items():
        command.extend(["--build-arg", f"{key}={value}"])
    command.extend(["-t", tag, context, "--progress=plain"])

    log_file_path = os.path.join(context, log_file_name)
    with open(log_file_path, 'w') as file:
        process = subprocess.Popen(command, stdout=file, stderr=file)
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            process.wait()
            print(f"Build process for {tag} terminated.")
            raise

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Read the configuration from a JSON file and parse it
config_file_content = read_file('config.json')
config = json.loads(config_file_content)

# Extract common build arguments
common_args = config['common_args']

# Read any files specified in common_args
for key, value in common_args.items():
    if value.startswith("./"):
        common_args[key] = read_file(value)

# Use a thread pool to build the images in parallel
with ThreadPoolExecutor() as executor:
    futures = []
    for image_name, image_config in config['images'].items():
        build_args = {**common_args, **image_config}
        context = os.path.join(os.getcwd(), image_name)
        tag = build_args.pop('TAG')
        print(f"Starting build for image {tag}...")
        future = executor.submit(build_docker_image, build_args, tag, context)
        futures.append(future)

    # Wait for all build processes to complete
    for future in futures:
        future.result()

    print("All builds completed.")