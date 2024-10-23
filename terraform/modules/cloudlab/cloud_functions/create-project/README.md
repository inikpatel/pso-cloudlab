# create-project

This cloud function validates and submits project creation requests

## Input

When a new record is written to the Firestore collection, a signal is sent to this Cloud Function with the new record as a payload (the data is held within `event["value"]["fields"]`).

## Output

Once the Firestore records have been validated, the Department, Email, and Project ID fields are passed along to the `git-push` function via a http POST request. The `git-push` function commits the change in the desired target git repository to trigger the downstream cicd pipeline.

If the `git-push` function call is succesfull, the above values are passed to the `email-task` Cloud Task Queue to send emails to end users.

## Testing

To test this function, create a new record in the Firestore collection in the Builder project, then follow the logs as the project builds:
1. Click the three dots next to the "schema" and select "Add Similar Record"
2. Fill out the resulting form and click "Save"
    - All fields should have a value
    - The 'email' field should contain a full email address (e.g. 'test@example.com'). However, if you want to test user access to the project, it should be a Google identity that would be able to access the resulting project
3. In the Cloud Log for this function, you should see:
    ```
    Creating a project with expected name: ${project_name}
    ```
