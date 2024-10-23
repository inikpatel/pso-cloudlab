# Copyright 2023 Google. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to
# your agreement with Google.
import os
import requests
#from google.cloud import pubsub_v1
from google.cloud import tasks_v2, firestore, compute_v1
import datetime
import json
from google.protobuf import duration_pb2, timestamp_pb2
import random
import string
import re
import google.auth
import google.auth.transport.requests

credentials, project_id = google.auth.default()
request = google.auth.transport.requests.Request()
credentials.refresh(request=request)

FN_URL = os.environ.get("GIT_FN_URL")

METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/'
METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
SERVICE_ACCOUNT = 'default'
#PREFIX =  "afrl"

## Removing PROJECT_PREFIX to prevent duplication of {env}-{impact_level}
PROJECT_PREFIX = os.environ['PROJECT_PREFIX']

#ENVIRONMENT = 'sbx'
ENVIRONMENT = os.environ['ENVIRONMENT']
db = firestore.Client()

#publisher = pubsub_v1.PublisherClient()
#topic_name = os.environ["TOPIC_NAME"]


#FUNCTION_URL = os.environ["EMAIL_FUNCTION_URL"] #email cloud function URL
TASK_QUEUE_NAME = os.environ["QUEUE_NAME"] #full path: projects/{{project}}/locations/{{location}}/queues/{{name}}

NETWORK_PROJECT = os.environ['NETWORK_PROJECT']
NETWORK_REGION = os.environ['NETWORK_REGION']

def get_future_timestamp(delay_seconds):
      # Convert "seconds from now" into an rfc3339 datetime string.
      d = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay_seconds)

      # Create Timestamp protobuf.
      timestamp = timestamp_pb2.Timestamp()
      timestamp.FromDatetime(d)

      return timestamp

"""
def add_email_cloud_task(email,requested_project):
   client = tasks_v2.CloudTasksClient()

   payload = {'email_address': email, 'project_id': requested_project}
   payload = json.dumps(payload)
   schedule_time = get_future_timestamp(180)
   task_name = 'email-' + requested_project + "-" + str(round(datetime.datetime.timestamp(datetime.datetime.now())))
   deadline = duration_pb2.Duration().FromSeconds(900)

   # Construct the request body.
   task = tasks_v2.Task(
    http_request = tasks_v2.HttpRequest(
        # Specify the type of request.
        http_method = tasks_v2.HttpMethod.POST,
        url = FUNCTION_URL,  # The full url path that the task will be sent to.
        body = payload.encode(),
        oidc_token = tasks_v2.OidcToken(
            service_account_email=credentials.service_account_email
        )
    ),
    schedule_time = schedule_time,
    name = F"{TASK_QUEUE_NAME}/tasks/{task_name}",
    dispatch_deadline = deadline
   )

   print(f"task is: {task}")

   task_req = tasks_v2.CreateTaskRequest(
      parent = TASK_QUEUE_NAME,
      task = task,
        )

   print(f"task req: {task_req}")

   # Use the client to build and send the task.
   response = client.create_task(task_req)
   if response:
      print("Created task {}".format(response.name))
      return True
   return False
"""

def generate_unique_id():
   # Generate a random alphanumeric string
   unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
   return unique_id

def is_valid_project_name(s):
    pattern = r'^[a-z][-a-z0-9]{3,12}[a-z0-9]$'
    return bool(re.match(pattern, s))


def hello_firestore(event, context):
   """Triggered by a change to a Firestore document.
   Args:
      event (dict): Event payload.
      context (google.cloud.functions.Context): Metadata for the event.
   """
   resource_string = context.resource
   # print out the resource string that triggered the function
   print(f"Context is: {context}")
   print(f"Function triggered by change to: {resource_string}")
   resource_list = resource_string.split('/')
   coll = resource_list[5]
   doc = resource_list[6]
   print(f"Event: {event}")

   #get document that triggers this function
   path_parts = context.resource.split('/documents/')[1].split('/')
   collection_path = path_parts[0]
   document_path = '/'.join(path_parts[1:])
   affected_doc = db.collection(collection_path).document(document_path)


   project_data = {}
   for k, v in event['value']['fields'].items():
      for type, data in v.items():
         project_data[k] = data
   #Required Values
   email = project_data['user_email']
   #group = project_data['group_email']
   project_name = project_data['project_name']
   terms_accept_time = project_data['terms_accept_time']
   terms_accepted = project_data['terms_accepted']
   #support_terms_accepted = project_data['support_terms_accepted']
   budget_terms_accepted = project_data['budget_terms_accepted']
   beta_terms_accepted = project_data['beta_terms_accepted']
   #google_group_membership = project_data['google_group_membership']




   #Optional Values


   department = project_data.get('department')
   description = project_data.get('description')
   data_type = project_data.get('data_type')
   #cui_specs = project_data.get('cui_specifications')

   if department:
      department = department.lower()
   if not is_valid_project_name(project_name):
      print(f"ERROR: Project Name must be minimum of 3 characters and maximum of 12 characters. It can have lowercase letters, digits, or hyphens.It must start with a lowercase letter and end with a letter or number (Given Project Name is: {project_name}).")
      return
   unique_id = generate_unique_id()
   project_id = f"{PROJECT_PREFIX}-{ENVIRONMENT}-{project_name}-{unique_id}"

   # Code for checking available subnet in a shared VPC. Only use for custom engagements
   #subnet = get_open_subnet(NETWORK_PROJECT, NETWORK_REGION)
   #update new project_id

   #Exit gracefully if project_id has already been set on this doc
   #Start Firestore transaction
   transaction = db.transaction()
   if not add_project_id(transaction, affected_doc, project_id):
      status = "Project ID already set, exiting"
      print(status)
      return status

   #Continue execution if this function wrote project_id succesfully
   status = f"Creating a project with expected ID: {project_id}"
   print(status)


  #Generates a JSON object to pass to an http function to create a new yaml file in a target git repo

   _content = {
    #  'group':group,
      'project':project_id,
      'email':email,
      'description': description,
      'data_type': data_type,
      'terms_accept_time': terms_accept_time,
      'terms_accepted': terms_accepted,
   #   'support_terms_accepted': support_terms_accepted,
      'budget_terms_accepted': budget_terms_accepted,
      'beta_terms_accepted': beta_terms_accepted,
      #'subnet': f"{NETWORK_REGION}/{subnet}",
      #'host_project': NETWORK_PROJECT
      #'group_membership': google_group_membership
      }

   print(f"Calling git function with content: {_content}")
   response = call_http_fn(FN_URL, _content)
   print(response)
 #EWG  #publisher.publish(topic_name, b'A new project has been requested!', email=email, department=department, project_id=project_id)

   #add email task to task queue
   """
   try:
      add_task = add_email_cloud_task(email, project_id)
      return
   except Exception as e:
      print(f"ERROR: Unable to create email task for email={email} and project={project_id}.")
      print(e)

   #if add_task == False:
   #   print(f"ERROR: Unable to create email task for email={email} and project={project_id}.")
   #   return
   """



@firestore.transactional
def add_project_id(transaction, doc, project_id, subnet=None, host_project=None ):
    snapshot = doc.get(transaction=transaction)
    json = snapshot.to_dict()
    print(json)
    existing_id = json.get('project_id')
    if existing_id:
        status = f"Project ID {existing_id} has already been created for this submission."
        print(status)
        return False

    transaction.update(doc, {u'project_id': project_id, u'subnet': subnet, u'host_project': host_project})
    return True


def call_http_fn(url, content):
   token = get_id_token(url)
   headers = {'Authorization': f'bearer {token}'}

   print(f'Sending request with content: {content}')
   r = requests.post(url, json=content, headers=headers)
   r.raise_for_status()

   content = r.content
   text = r.text

   print(f'Response content: {content}')
   print(f'Response text: {text}')

   return text


def get_id_token(req_url):
   _params = {"audience":req_url}
   url = f'{METADATA_URL}/instance/service-accounts/{SERVICE_ACCOUNT}/identity'
   # Request an access token from the metadata server.
   r = requests.get(url, headers=METADATA_HEADERS, params=_params)
   r.raise_for_status()

   # Extract the access token from the response.
   #json when getting access token, text when ID token
   #access_token = r.json()['access_token']
   access_token = r.text

   return access_token


def list_subnets(project, region, client):
    # Initialize request argument(s)
    request = compute_v1.ListSubnetworksRequest(
        project = project,
        region = region,
    )
    # Make the request
    response = client.list(request=request)

    # Handle the response
    return(response)

def get_subnet_iam(project, region, subnet, client):
    request = compute_v1.GetIamPolicySubnetworkRequest(
        project = project,
        region= region,
        resource = subnet,
    )
    response = client.get_iam_policy(request=request)
    return(response)


def get_open_subnet(project, region):
   client = compute_v1.SubnetworksClient()
    #Get list of subnets in the region
   subnets = list_subnets(project, region, client)

   #Loop through each subnet and get IAM bindings.
   for subnet in subnets:
      name = subnet.name
      #Get IAM bindings
      iam = get_subnet_iam(project, region, name, client)

      #Return first subnet without any IAM bindings
      if iam.bindings:
         continue
      else:
         print(f"{name} is the first subnet without bindings")
         return(name)
         break
      raise ValueError("No available subnets")
