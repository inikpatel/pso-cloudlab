# Copyright 2023 Google. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to
# your agreement with Google.

import functions_framework
import requests
import os
import git
import shutil
from jinja2 import Environment, FileSystemLoader

#environment vars
TEMPLATE_FILE = os.environ['TEMPLATE_FILE']
ORIGIN_URL = os.environ['ORIGIN_URL']
FOLDER_ID = os.environ['FOLDER_ID']

ORIGIN_BRANCH = 'main'
REPO_NAME = 'cloudlab-repo'
PRJ_PATH = "data/projects"
TEMPLATE_PATH = "data/templates"

METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/'
METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
SERVICE_ACCOUNT = 'default'
PARAMS = {'scopes':'https://www.googleapis.com/auth/source.read_write'}


@functions_framework.http
def create_project_http(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    """Extract project and group from request data, expects:
    {
        group = group@group.com,
        project = project
    }
    """

    print(f'Request body: {request_json}')
    print(f'Request vars: {request_args}')

    group = request_json.get('group')
    project_name = request_json.get('project')
    requestor = request_json.get('email')
    subnet = request_json.get('subnet')
    host_project = request_json.get('host_project')
    user_template = request_json.get('data_type')

    if project_name is None:
        status = 'A valid project must be provided, project value was empty'
        print(status)
        return status, 400


    write_git_cookie()

    print(f"Input vars: ORIGIN_URL = {ORIGIN_URL}, origin_branch = {ORIGIN_BRANCH}, group = {group}, template_file = {user_template} repo_dir = {REPO_NAME}")
    print(f"Starting git project creation process for project: {project_name}")
    print(f"Cloning repo: {ORIGIN_URL}")
    repo = clone_repo()
    os.chdir(REPO_NAME)

    print(f"Creating project yaml file from template.")
    new_project = create_file(group, requestor, project_name, subnet, host_project, user_template)

    print(f"Commiting and pushing project yaml file to git repo.")

    status = commit_changes(repo, new_project)

    return status

def get_access_token():
    url = f'{METADATA_URL}/instance/service-accounts/{SERVICE_ACCOUNT}/token'
    # Request an access token from the metadata server.
    r = requests.get(url, headers=METADATA_HEADERS, params=PARAMS)
    r.raise_for_status()

    # Extract the access token from the response.
    access_token = r.json()['access_token']

    return access_token

def write_git_cookie():
    #writes a line to the gitcookies file with a valid access_token.

    cookieFile = ".gitcookies"
    access_token = get_access_token()
    line = f"source.developers.google.com\tFALSE\t/\tTRUE\t2147483647\to\tgit.sa.account={access_token}\n"

    cookieFile = os.path.abspath(cookieFile)

    # write git auth cookie to .gitcookiefile
    with open(cookieFile, 'w') as f:
        print(f"Writing git auth cookie to {cookieFile}")
        f.write(line)

    #Initialize empty git repo object in order to write global config
    repo = git.Repo.init()

    #write cookie file config value
    with repo.config_writer(config_level="global") as cw:
        cw.add_value("http", "cookiefile", cookieFile)

    return


def clone_repo():
    #remove local directory if it exists already.
    if os.path.exists(REPO_NAME):
        shutil.rmtree(REPO_NAME)

    try:
        repo = git.Repo.clone_from(ORIGIN_URL,
                            REPO_NAME,
                            branch=ORIGIN_BRANCH)
        print("Succesfully cloned repo")
        return repo
    except Exception as e:
        print(f"Error cloning repo: {e}")



def create_file(group, requestor, project_name, subnet, host_project, user_template):
    #expects working directory to be inside of the REPO_NAME folder
    _prjPath = PRJ_PATH
    _template_path = TEMPLATE_PATH
    _newfile = f"{_prjPath}/{project_name}.yaml"
    _requestor = requestor.replace("@", "__")
    _requestor = _requestor.replace(".", "_")

    print (f"Current dir is {os.getcwd()}")

    environment = Environment(loader=FileSystemLoader(_template_path))
    template = environment.get_template(user_template)

    content = template.render(
        group = group,
        requestor = _requestor,
        folder_id = FOLDER_ID,
        subnet = subnet,
        host_project = host_project
    )

    with open(_newfile, mode="w", encoding="utf-8") as prjfile:
        prjfile.write(content)
        print(f"Created {_newfile}")

    return _newfile


def commit_changes(repo, newfile):
    index = repo.index
    untracked_files = repo.untracked_files
    diff = index.diff(None)

    if (untracked_files or diff):
        print("Diff or new file detected.")
        print(f"Untracked files: {untracked_files}")
        print(f"Diff: {diff}")

        print(f"Git commit of {newfile}")
        index.add([newfile])
        index.commit(f"Automated commit of {newfile}")
        status = repo.git.status()
        print (f"Git status before Push: {status}")

        #push to repo
        try:
            repo.git.push()
            status = f'Succesfully pushed commit to repo.'

           # sha = repo.head.commit.hexsha
           #TO-DO: Return commit hash in order to get build status later. Ex. gcloud builds list --filter=source.repoSource.commitSha:"shagoeshere"
            print(status)
            return status
        except:
            status = 'Error pushing to git repo, check logs for more information.'
            print (status)
            return status

    else:
        status = 'No Diff detected, no action taken'
        print (status)
        #print (f"Untracked files: {untracked_files}")
        #print (f"Diff: {diff}")
        return status


if __name__ == "__main__":

   # vars for local testing
    #repo_dir = "/tmp/cloudlab-repo"
    template_file = "cloudlab.yaml.template"

    origin_url = "SOURCE_REPO_URL_HERE"
    origin_branch = "main"
    project_name ="PROJECT_NAME_HERE"
    group = "GROUP_EMAIl@DOMAIN"
    folder_id = "folders/1234567"

    create_project(origin_url, origin_branch, group, template_file, project_name)
