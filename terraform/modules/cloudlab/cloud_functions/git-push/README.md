# Git Push Function

This cloud function takes an input of a desired project-id and pushes the resulting config file to a git repository.

## Input
The `create-project` function executes a POST request to this function. This function expects the following data in the POST request:
```
    {
        group = group@example.com,
        project = project_id
    }
```

Other data may be passed in but is currently ignored. Future iterations of Cloud Lab can leverage other values.

## Output

Upon succesfull data validation, this function performs the following steps:

* Acquires an access token
* Clones the git repository defined via the `ORIGIN_URL` environment variable.
* Creates a project `.yaml` file leveraging a template in the `data/templates/` folder.
* The filename of the `.yaml` file is set to the value of the project_id.
* Commits and pushes the changes to the git repository.


## Testing

To test this function, call the function with a HTTP curl request:

```
curl -m 190 -X POST https://<function-url> \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "group": "testgroup@domain.com",
  "project": "my-test-project"
}'
```

If succesful, you should recieve an `http 200` response code with the text: `Succesfully pushed commit to repo`. Validate this by manually observing the desired git repository. The commit should then trigger the downstream cloud build trigger.
