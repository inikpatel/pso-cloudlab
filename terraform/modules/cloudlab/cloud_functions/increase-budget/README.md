# increase-budget

This Cloud Function validates and submits project creation requests

## Input

The Cloud Function sits behind a HTTP server (specifically a Flask server, a Python-based small HTTP server library), and any requests made to it are presented to the function in a `flask.Request` object. The root URI for the endpoint is of the form `https://"${gcp_region}-${project_name}.cloudfunctions.net/${function-name}"`. So, for example:
```
https://us-east4-example-project.cloudfunctions.net/increase-budget
```

The full URI also contains three parameters:
- `ic`
- `email`
- `project_id`

These can appear in any order, but all must be present. A full URI, then would look like:

```
https://us-east4-example-project.cloudfunctions.net/increase-budget?email=example@example.com&ic=nih&project_id=1234
```

Note the question mark (`?`) at the beginning of the parameter list, and the ampersands (`&`) separating each parameter/value pair. These three values must be identical to the project's entry in Firestore.

## Output

After verifying that all three fields contain values, the function sends those values as part of a message to the `increase-budget` Pub/Sub topic, and returns a `200 OK` signal and message to the user. If the validation fails, a `400 Bad Request` and message is returned to the user

## Testing

To test this function, you can manually build the link using the template above:
1. Build, then click the link. You should see the `"Request sent to increase budget for project with unique id {project_id}"` message and a `200 OK` signal.
2. Check the logs for this Cloud Function. There should be a message to the effect of `Function execution took 2230 ms. Finished with status code: 200`
3. Check the logs of the `cloud-lab` Cloud Run image. There should be Terraform output that describes updating the budget.
4. Check the budget for the project - the limit should now be $1000.

If you want to test the failure states you can leave out a parameter. Doing so should return a error message (e.g. `"Incorrect arguments, please check the link"`), a `400 Bad Request` signal, and no further action from the Cloud Function.
