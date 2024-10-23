# Cloud Lab UI

This UI program takes user identity from the HTTP headers:

- 'X-Goog-Authenticated-User-Email'
- 'X-Goog-Authenticated-User-ID'

Verify it against the JWT passed in by IAP.

With above user information, this UI program queries cloud resources
to display a list of projects under the Cloud Lab folder belong to 
the user at the landing page.

This UI program also provides a form to allow user to submit a request
for a new Cloud Lab project.

Currently the following templates can be chosen from the form:

- default
- data-playground
- cloud-storage
