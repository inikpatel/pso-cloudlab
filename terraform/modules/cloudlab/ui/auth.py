# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import request
import os
import requests
from google.auth.transport import requests as auth_requests
from google.oauth2 import id_token
import google.cloud.logging
import json

client = google.cloud.logging.Client()
client.setup_logging()

import logging

#Metadata URL

METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1'

#IAP Audience value
IAP_AUD = os.environ.get("IAP_AUD")

def get_metadata(metadata_path, params=None):
    metadata_headers = {'Metadata-Flavor': 'Google'}
    url = f'{METADATA_URL}/{metadata_path}'
    r = requests.get(url, headers=metadata_headers, params=params)
    r.raise_for_status()
    return r.text

def validate_iap_jwt(iap_jwt, expected_audience):
    """Validate an IAP JWT.
    Args:
      iap_jwt: The contents of the X-Goog-IAP-JWT-Assertion header.
      expected_audience: The Signed Header JWT audience. See
          https://cloud.google.com/iap/docs/signed-headers-howto
          for details on how to get this value.

    Returns:
      (user_id, user_email, error_str).
    """

    try:
        decoded_jwt = id_token.verify_token(
            iap_jwt,
            auth_requests.Request(),
            audience=expected_audience,
            certs_url="https://www.gstatic.com/iap/verify/public_key",
        )

        logging.info("JWT dump:" + json.dumps(decoded_jwt) + "\n")
        return (decoded_jwt["email"], decoded_jwt["sub"])
    except Exception as e:
        logging.error("JWT validation error: " + str(e))
        raise e
        #return ("**ERROR: JWT validation error {e}**")

def user():
    project_number = get_metadata(metadata_path='project/numeric-project-id')
    expected_audience = f'/projects/{project_number}/global/backendServices/{IAP_AUD}'

    # Requests coming through IAP have special headers
    assertion = request.headers.get('X-Goog-IAP-JWT-Assertion')
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')
    user_id = request.headers.get('X-Goog-Authenticated-User-Id')
    if assertion is None:   # Request did not come through IAP
        return None, None

    valid_user = validate_iap_jwt(assertion, expected_audience)

    return valid_user
