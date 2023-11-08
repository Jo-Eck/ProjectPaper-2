import requests
from datetime import datetime

# Function to convert GitHub timestamp to datetime
def convert_github_timestamp(timestamp):
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

# Function to get repository data from GitHub API
def get_repository_data(repo_name):
    url = f"https://api.github.com/repos/{repo_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'created_at': convert_github_timestamp(data['created_at']),
            'total_commits': None,  # Placeholder for commit count
            'open_issues_count': data['open_issues_count'],
            'closed_issues_count': None  # Placeholder for closed issue count
        }
    else:
        return None

# Function to get the total number of commits in a repository
def get_total_commits(repo_name):
    url = f"https://api.github.com/repos/{repo_name}/stats/contributors"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        total_commits = sum(contributor['total'] for contributor in data)
        return total_commits
    else:
        return None


def get_closed_issues(repo_name):
    url = f"https://api.github.com/search/issues?q=repo:{repo_name}+type:issue+state:closed"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['total_count']
    else:
        return None

# Repositories list
repositories = [
    'pachyderm/pachyderm',
    'apache/airflow',
    'kubeflow/kubeflow',
    'knative/serving',
    'spotify/luigi',
    'common-workflow-language/cwltool',
    'argoproj/argo-cd'
]

# Iterate over the repositories to get their data
for repo_name in repositories:
    repo_data = get_repository_data(repo_name)
    if repo_data:
        repo_data['total_commits'] = get_total_commits(repo_name)
        repo_data['closed_issues_count'] = get_closed_issues(repo_name)
        current_time = datetime.now()
        time_diff = current_time - repo_data['created_at']
        print(f"Repository: {repo_name}")
        print(f"Created at: {repo_data['created_at']} ({time_diff.days} days ago)")
        print(f"Total commits: {repo_data['total_commits']}")
        print(f"Open issues: {repo_data['open_issues_count']}")
        print(f"Closed issues: {repo_data['closed_issues_count']}")
        print("\n")
    else:
        print(f"Failed to get data for repository: {repo_name}")
