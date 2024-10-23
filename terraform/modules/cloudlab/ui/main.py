from datetime import datetime, timezone
import time
import os
from os import environ as env
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory
from flask_wtf import FlaskForm
from logging.config import dictConfig
from wtforms import widgets, StringField, SubmitField, TextAreaField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
import firebase_admin
from firebase_admin import firestore
from urllib.parse import urlencode
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.cloud.firestore_v1.base_query import FieldFilter
import googleapiclient.discovery
import google.auth
import traceback


import time
from auth import user
import pysnooper
load_dotenv()
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',  # <-- Solution
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

DEBUG = env['DEBUG'] if 'DEBUG' in env else False
PORT = env['PORT'] if 'PORT' in env else 8080
HOST = env['HOST'] if 'HOST' in env else '0.0.0.0'
SCOPES = ['https://www.googleapis.com/auth/cloud-identity.groups','https://www.googleapis.com/auth/cloud-platform.read-only']
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# GROUP_PREFIX = env['GROUP_PREFIX']
# GROUP_SUFFIX = env['GROUP_SUFFIX']
# GROUP_DOMAIN = env['GROUP_DOMAIN']

# CUSTOMER_ID = env['CUSTOMER_ID']

credentials, project = google.auth.default(scopes=SCOPES)

firebase_admin.initialize_app()
db = firestore.Client()


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


def search_transitive_groups(service, member, page_size):
    try:
        groups = []
        next_page_token = ''
        while True:
            query_params = urlencode(
                {
                    "query": "member_key_id == '{}' && 'cloudidentity.googleapis.com/groups.security' in labels".format(member),
                    "page_size": page_size,
                }
            )
            request = service.groups().memberships().searchTransitiveGroups(parent='groups/-')
            request.uri += "&" + query_params
            response = request.execute()
            if 'memberships' in response:
                for membership in response['memberships']:
                    for role in membership['roles']:
                        if role['role'] in ['OWNER', 'MANAGER', 'ADMIN']:
                            groups.append(membership)
                            break
            if 'nextPageToken' in response:
                next_page_token = response['nextPageToken']
            else:
                next_page_token = ''

            if len(next_page_token) == 0:
                break;

        return groups
    except Exception as e:
        traceback.print_exc()
        print(e)

def get_group_names(verified_email):
    service = create_service(verified_email)
    #data = search_transitive_groups(service, verified_email, 50)
    groups = []
    groups.append({'name': "devops", 'id': "devops@example.com"})
    #for item in data:
        #if 'displayName' in item and 'groupKey' in item:
            #group_name = item['displayName']
            #group_id = item['groupKey']['id']
            #groups.append({'name': group_name, 'id': group_id})
    traceback.print_exc()
    return groups


def create_service(verified_email):

    service_name = 'cloudidentity'
    api_version = 'v1'
    service = googleapiclient.discovery.build(
        service_name,
        api_version,
        credentials=credentials)

    return service


class NamerForm(FlaskForm):
    name = StringField(
        'You are submitting this request as the following user: ',
        validators=[
            DataRequired()],
            render_kw={'readonly': True})
    project_name = StringField(
        'Please enter a Project Name. Must be minimum of 3 characters and maximum of 9 characters. It can have lowercase letters, digits, or hyphens. It must start with a lowercase letter and end with a letter or number.',
        validators=[
            DataRequired(),
            Length(min=3, max=9),
            Regexp(
                '^[a-z][-a-z0-9]{3,12}[a-z0-9]{1}$',
                message='Must be minimum of 3 characters and maximum of 9 characters. It can have lowercase letters, digits, or hyphens. It must start with a lowercase letter and end with a letter or number.')
        ])
    description = TextAreaField(
        'Please enter the use case and other relevant info for this project (Optional): ')
    budget_terms = BooleanField(
        'A usage budget of $2,000 per project will be provided. Cloud Lab reserves the right to disconnect all access to services for violation of the budgeting or violation of the Terms of Service ',
        validators=[DataRequired()])
    beta_terms = BooleanField(
        'Cloud Lab is a Beta environment and access to services or availability may change unexpectedly ',
        validators=[DataRequired()])
    terms = BooleanField(
        'I agree to the ',
        validators=[DataRequired()])
    data_type = SelectField(
        'Please identify the project template you would like to use:',
        choices=[
            ('cloudlab.yaml.template', 'Default'),
            ('data-playground.yaml.template', 'Data playground'),
            ('cloud-storage.yaml.template', 'Cloud Storage')
        ])
    group = SelectField(
        'Please select the group used to access this project:', choices=[],
        validate_choice=False,
        validators=[DataRequired()])
    submit = SubmitField("Submit")

"""
    def validate_cui_specifications(self, cui_specifications):
        data_type_data = self.data_type.data
        cui_specifications_data = cui_specifications.data
        if data_type_data == 'controlled_unclassified_information':
            if len(cui_specifications_data) < 1:
                raise ValidationError('Please select all applicable CUI tags.')
        else:
            if len(cui_specifications_data) > 0:
                raise ValidationError('Data type is not CUI.')
"""

@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route("/", methods=['GET', 'POST'])
def project():

    projects =[]

    # Read doc to Firestore:
    try:
        #  search a doc from Firestore
        user_email = request.headers.get('X-Goog-Authenticated-User-Email')

        email = user_email.split(':')[-1]
        app.logger.info(f"User Email: {email}")
        field_filter = FieldFilter("user_email","==",email)
        docs = db.collection('collection').where(filter=field_filter).stream()
        for doc in docs:
            doc_data = doc.to_dict()
            #app.logger.info(f"doc_data: {doc_data}")
            project_id = doc_data.get('project_id')
            if project_id:
                project_name = doc_data.get('project_name')
                project_status = get_project_status(project_id)
                app.logger.info(f"Project ID {project_id} Found")
                if project_status == "ACTIVE":
                    # only display active projects
                  projects.append({
                    'name': project_name,
                    'status': project_status,
                    'url': 'https://console.cloud.google.com/welcome?' + urlencode({'project':project_id})
                  })
                else:
                  # skip deleted projects
                  app.logger.info(f"Project ID {project_id} : {project_status}.")
            else:
                app.logger.info(f"Project ID {project_id} not found")

        app.logger.info(projects)

    except Exception as e:
        app.logger.error(f'Error reading from Firestore: {e}')
        return render_template("project.html", projects=[])

    # read project status from Cloud Asset Inventory API

    return render_template("project.html", projects=projects)

# function takes in a project name or id, returns the project status
def get_project_status(project_id):
    """
    Get the status of a project.

    Args:
        project_id (str): The ID of the project to get the status of.

    Returns:
        str: The status of the project.
    """

    # Create a Cloud Resource Manager client.
    try:
        client = googleapiclient.discovery.build(
            'cloudresourcemanager', 'v1', credentials=credentials)

        # Get the project.
        project = client.projects().get(projectId=project_id).execute()

        # Return the project status.
        return project.get('lifecycleState')
    except Exception as e:
        app.logger.error(f'Error getting project status: {e}')
        return "Unknown"

@app.route("/new", methods=['GET', 'POST'])
def load_html():
    form = NamerForm(formdata=None)
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')
    user_id = request.headers.get('X-Goog-Authenticated-User-ID')
    verified_email, verified_id = user()
    groups = get_group_names(verified_email)
    group_choices = [(group['id'],group['name']) for group in groups]
    form.group.choices = group_choices
    form.name.data = verified_email

    if 'project_url' not in session:
        session['project_url'] = None
        session.permanent = False
        return render_template("index.html", form=form, project_url=session['project_url'])
    else:
        return render_template("index.html", form=form, project_url=session['project_url'])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/submit", methods=['POST'])
#@pysnooper.snoop(color=False)
def submit():
    form = NamerForm()
    if form.validate_on_submit():
        try:
            form = NamerForm()
            current_time = datetime.now(timezone.utc)
            name = request.form['name']
            #name = verified_email # Use validated email instead of user supplied
            project_name = request.form['project_name']
            description = request.form['description']
            support_terms = request.form.get('support_terms')
            budget_terms = request.form.get('budget_terms')
            beta_terms = request.form.get('beta_terms')
            terms = request.form.get('terms')
            data_type = request.form.get('data_type')
            terms_accept_time = current_time.timestamp()
            # group_email = f"{GROUP_PREFIX}{project_name}{GROUP_SUFFIX}@{GROUP_DOMAIN}"
            # google_group = create_google_group(group_email, CUSTOMER_ID)
            # group_membership = create_google_group_membership(name, group_email, CUSTOMER_ID)


            # Assign info variable
            info = {
                'user_email': name,
                'project_name': project_name,
                'description': description,
                'terms_accepted': terms,
                'terms_accept_time': terms_accept_time,
                'data_type': data_type,
                #'group_email': group_email,
                #'google_group': google_group,
                #'google_group_membership': group_membership,
                #'support_terms_accepted': support_terms,
                'budget_terms_accepted': budget_terms,
                'beta_terms_accepted': beta_terms,
            }

        except Exception as e:
            session['project_url'] = None
            flash('Unable to create your project, please try again.')
            app.logger.error(f'Error in form data submission: {e}')


        # Write doc to Firestore:
        try:
            doc = db.collection('collection').add(info)

            project_url = project_name
            #create_google_group(group_email)
            time.sleep(3)
            #create_google_group_membership(name, group_email)

            for i in range(4):
                doc_test = doc[1].get().to_dict()
                if doc_test:
                    app.logger.info("found doc")
                    project_id = doc_test.get('project_id')
                    if project_id:
                        app.logger.info(f"Project ID {project_id} Generated")
                        generate_project_url(project_id)
                        flash('Thank you! Your details have been submitted.')
                        return redirect(url_for('project'))
                    else:
                        time.sleep(3 * (i + 1))

        except Exception as e:
            session['project_url'] = None
            flash('Unable to create your project, please try again.')
            app.logger.error(f'Error writing to Firestore: {e}')
    else:
        flash('There were errors in your submission; Please check your information and resubmit.')
        app.logger.error(f'Error in validation: {form.errors}')

    return render_template("index.html", form=form, project_url=session['project_url'])

def create_google_group(group_email, customer_id):
    with build('cloudidentity', 'v1', credentials=credentials) as service:
        group_id = group_email
        group_key = {"id": group_id}
        group = {
            "parent": "customers/" + customer_id,
            "description": 'Cloud Lab Managed Security group',
            "displayName": group_email,
            "groupKey": group_key,
            # Set the label to specify creation of a Google Group.
            "labels": {
                "cloudidentity.googleapis.com/groups.discussion_forum": ""
                }
                }
        try:
            request = service.groups().create(body=group)
            request.uri += "&initialGroupConfig=WITH_INITIAL_OWNER"
            response = request.execute()
            return response
            print(response)
        except Exception as e:
                print(e)



def create_google_group_membership(user_email, group_email, customer_id):
    with build('cloudidentity', 'v1', credentials=credentials) as service:
        member_key = user_email
        group_id = group_email
        identity_source_id = "customers/" + customer_id
        param = "&groupKey.id=" + group_id
        try:
            lookupGroupNameRequest = service.groups().lookup()
            lookupGroupNameRequest.uri += param
            lookupGroupNameResponse = lookupGroupNameRequest.execute()
            groupName = lookupGroupNameResponse.get("name")
            # Create a membership object with a memberKey and a single role of type MEMBER
            membership = {
            "preferredMemberKey": {"id": member_key},
            "roles":[
                {'name' : 'MEMBER'},
                {'name' : 'MANAGER'}
            ]
            }
            # Create a membership using the ID for the parent group and a membership object
            response = service.groups().memberships().create(parent=groupName, body=membership).execute()
            return response
            print(response)
        except Exception as e:
            print(e)


@app.route("/clear", methods=['GET'])
def clear_session_data():
    if 'project_url' in session:
        session.pop('project_url', None)
    return redirect(url_for('load_html'))


def generate_project_url(project_name):
    gcp_url = 'https://console.cloud.google.com/welcome?'
    params = {'project': project_name}
    session['project_url'] = gcp_url + urlencode(params)


if __name__ == "__main__":
    app.run(debug=DEBUG, port=PORT, host=HOST)
