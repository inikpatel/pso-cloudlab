# welcome email

This cloud function validates that the requested project has been created and sends an email to the user with relevant information about cloud lab and the project.

## Input

The Cloud Function sits behind a cloud task queue, and any requests made to it are presented to the function in a `Request` object. The root URI for the endpoint is of the form `https://"${gcp_region}-${project_name}.cloudfunctions.net/${function-name}"`. So, for example:
```
https://us-east4-example-project.cloudfunctions.net/welcome-email
```

The full URI also contains two parameters:
- `email_address`
- `project_id`

These can appear in any order, but all must be present. A full URI, then would look like:

```
https://us-east4-example-project.cloudfunctions.net/welcome_email?email=example@example.com&project_id=1234
```

Note the question mark (`?`) at the beginning of the parameter list, and the ampersands (`&`) separating each parameter/value pair. These three values must be identical to the project's entry in Firestore.

## Output

After verifying that all two fields contain values, the function checks if the project has been successfully created based on the given project_id, if so it sends a welcome email with relevant links to the user and returns a `200 OK` signal which removes the request from the cloud task queue. If the validation fails or the project doesn't exist a `4xx` is returned and and message is returned to the user. Since a `4xx` had been returned the cloud tasks queue is not cleared and will try to trigger the function again after a specific time.

## Testing

This function requires a smtp relay setup on the workspace domain to send the email.

To test this function, you can manually build the link using the template above:
1. Build, then click the link. You should see the `"Email sent to user."` message and a `200 OK` signal.
2. Check the logs for this Cloud Function. There should be a message to the effect of `Function execution took 2230 ms. Finished with status code: 200`

If you want to test the failure states you can leave out a parameter. Doing so should return a error message (e.g. `"Incorrect arguments, please check the link"`), a `400 Bad Request` signal, and no further action from the Cloud Function.
