# Copyright 2023 Google. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to
# your agreement with Google.

import functions_framework
import requests
import os
import git
import shutil
import yaml

#environment vars
ORIGIN_URL = os.environ['ORIGIN_URL']

ORIGIN_BRANCH = 'main'
REPO_NAME = 'cloudlab-repo'
PRJ_PATH = "data/projects"
DEFAULTS_FILE = "data/defaults.yaml"

METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/'
METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
SERVICE_ACCOUNT = 'default'
PARAMS = {'scopes':'https://www.googleapis.com/auth/source.read_write'}


@functions_framework.http
def increase_budget_http(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    """Extract project and group from request data, expects:
    {
        group = group@group.com,
        project = project
    }
    If this is a budget increase request, expects args amount=amount in addition to project and group data.
    """

    print(f'Request body: {request_json}')
    print(f'Request vars: {request_args}')

    group = request_json.get('group')
    project_name = request_json.get('project')

    budget_req_amt = request_args.get('amount')

    #if args = update budget:
    # write cookie
    # clone_repo()
    # update_budget()
    # commit_changes

    if None in (group, project_name, budget_req_amt):
        status = 'A valid group, amount and project must be provided'
        print(status)
        return status, 400

    try:
        budget_req_amt = int(budget_req_amt)
    except:
        status = 'A valid integer must be provided as a budget amount'
        print(status)
        return status, 400


    write_git_cookie()

    print(f"Input vars: ORIGIN_URL = {ORIGIN_URL}, origin_branch = {ORIGIN_BRANCH}, repo_dir = {REPO_NAME}")
    print(f"Starting budget increase process for project: {project_name}, amount: {budget_req_amt}")

    print(f"Cloning repo: {ORIGIN_URL}")
    repo = clone_repo()

    if budget_req_amt > 0:
        _project_file = f"./{REPO_NAME}/{PRJ_PATH}/{project_name}.yaml"
        _defaults_file = f"./{REPO_NAME}/{DEFAULTS_FILE}"

        try:
            status =  update_budget(_project_file, _defaults_file, budget_req_amt)
            if '200' in status:
                return status
        except OSError as e:
            status = f"Error opening project file. {e}  Confirm project_id is correct."
            print(status)
            return status, 400
    else:
        status = "Requested budget amount must be greater than zero"
        return status, 400

    # Commit and push updated project file
    status = commit_changes(repo, _project_file)
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
    except Exception() as e:
        print(f"Error cloning repo: {e}")



def write_yaml_file(file, data):
    with open(file, 'w') as f:
        print(f"Writing data to {file}: {data}")
        yaml.dump(data, f)


def update_budget(project_file, defaults_file, amount):
    #Read defaults
    with open(defaults_file, 'r') as defaults:
        f = yaml.safe_load(defaults)
        default_billing_alert = f.get('billing_alert')
        print(f"Default billing alert is: {default_billing_alert}")

        with open(project_file, 'r') as f:
            json = yaml.safe_load(f)
        # if billing_alert object exists:
        # set billing_alert.amount to new value
        # write new values to file
            billing_alert = json.get('billing_alert')
            try:
                old_amount = billing_alert.get('amount', '')
            except:
                old_amount = ''
            if billing_alert and old_amount != amount:
                json['billing_alert']['amount'] = amount
                write_yaml_file(project_file, json)
                status = f"Updated budget amount from {old_amount} to {amount}"
            elif not billing_alert and default_billing_alert['amount'] != amount:
                json['billing_alert'] = default_billing_alert
                json['billing_alert']['amount'] = amount
                write_yaml_file(project_file, json)
                status = f"Project was using default billing, setting new budget amount to {amount}"
                print (status)
            else:
                status = "Existing budget and requested budget are the same, no action taken."
                return status, 200

    print(status)
    return status


def commit_changes(repo, newfile):
    index = repo.index
    untracked_files = repo.untracked_files
    diff = index.diff(None)

    _trim = len(f'./{REPO_NAME}/')
    newfile = newfile[_trim:]
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
           #TO-DO: Return commit hash for future use
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
