# Copyright 2021 Google. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to
# your agreement with Google.
import base64
import json
import os
from googleapiclient import discovery
import traceback

def stop_billing(data, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
        Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_data = base64.b64decode(data['data']).decode('utf-8')
    print(f"New Notification: {pubsub_data}")
    try:
        pubsub_json = json.loads(pubsub_data)
    except json.JSONDecodeError:
        print(f"Something went wrong when attempting to decode the JSON. Message: {pubsub_data}")
        traceback.print_exc()
        return

    try:
        threshold = float(pubsub_json['alertThresholdExceeded'])
    except KeyError:
        print("This is a budget notification, but does not contain details about an exceeded threshold. Nothing to do.")
        return

    # We expect the budget to have the display name "Budget for Cloud Lab: nasa-user-6179044def1d"
    # We then split on the colon (':') to grab the name of the project
    # Because the project name is not included in the billing notification
    budget_name = pubsub_json['budgetDisplayName']
    budget_nameparts = budget_name.split(":")
    if len(budget_nameparts) == 2:
        PROJECT_ID = budget_nameparts[1].strip()
        PROJECT_NAME = 'projects/{}'.format(PROJECT_ID)
        print('The function executing for project id {} and current threshold is {} '.format(PROJECT_ID,str(threshold)))

    if threshold < 1.5:
        print(f'No action necessary. (Current threshold is : {threshold})')
        return

    if PROJECT_ID is None:
        print(f'No project specified in the budget display name. (Current budget display name is : {budget_name})')
        return

    billing = discovery.build(
        'cloudbilling',
        'v1',
        cache_discovery=False,
    )

    projects = billing.projects()

    billing_enabled = __is_billing_enabled(PROJECT_NAME, projects)

    if billing_enabled:
        __disable_billing_for_project(PROJECT_NAME, projects)
    else:
        print('Billing already disabled')


def __is_billing_enabled(project_name, projects):
    """
    Determine whether billing is enabled for a project
    @param {string} project_name Name of project to check if billing is enabled
    @return {bool} Whether project has billing enabled or not
    """
    try:
        res = projects.getBillingInfo(name=project_name).execute()
        return res['billingEnabled']
    except KeyError:
        # If billingEnabled isn't part of the return, billing is not enabled
        return False
    except Exception:
        print('Unable to determine if billing is enabled on specified project, assuming billing is enabled')
        traceback.print_exc()
        return True

def __disable_billing_for_project(project_name, projects):
    """
    Disable billing for a project by removing its billing account
    @param {string} project_name Name of project disable billing on
    """
    body = {'billingAccountName': ''}  # Disable billing
    try:
        res = projects.updateBillingInfo(name=project_name, body=body).execute()
        print(f'Billing disabled: {json.dumps(res)}')
    except Exception:
        print('Failed to disable billing, possibly check permissions')
        traceback.print_exc()
