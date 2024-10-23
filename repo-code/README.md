# Cloud Lab User Project Repo

## overview

This repo contains the Terraform code that provisions projects for Cloud Lab users.

It leverages Cloud Foundation Fabric Project Factory to create projects, and also allows user to pick selected blueprints to be deployed into the projects.

All projects are created under the Cloud Lab's user project folder. There's no shared VPC at the moment, which means each project can have its own VPC network.

The supported blueprints are:

- **default**: a project with certain services enabled, and a budget plan attached;
- **cloud storage**: a project with a Cloud Storage Bucket created.
- **data playground**: adapted from [here](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/blueprints/data-solutions/data-playground)

All configurations are stored under `data/` directory, the `defaults.yaml` contains the common variables shared by all Cloud Lab projects.

Under `data/templates` are the blueprint template files, it is used to create the actual project factory configuration file with input variables from the user input in the Cloud Lab UI app.

Under `data/projects` are the actual definitions of each user project in YAML format. These files are created by the Cloud Lab's Cloud Run function, it checks out the templates, applies the user input to render a new configuration file, then checks in the new project definition file. A CICD workflow has been pre-defined to pick up the changes and kicks off the Terraform deployment.

## Default settings

For all projects, we need to define the following variables manually in `data/defaults.yaml` file before pushing to the cloud source repository.

- **essential_contacts**: this should be a list of users or groups that own or manage the project;
- **folder_id**: this is the parent folder of all Cloud Lab user projects;
- **template**: by default it will pick up 'default', can be set to 'data-playground' or 'storage', or others when we expand the support of more blueprints;
- **group_iam**: a list of roles assigned to the admin users and groups;
- **labels**: to be attached to the project and resources within the project;
- **services**: services to be enabled by default in the project;
- **vpc**: (optional), currently not used, for shared VPC settings;

## Project settings

For each project, depends on the template, additional services and roles can be added. These values are defined in the corresponding template files under `data/templates` and merged with the default settings.

Each project will have its own file `data/projects/<project-id>.yaml`, the file name is the same as the project id. A sample file `data/projects/project.yaml.sample` is provided as reference.

## Deployment

This repo is hosted in the Cloud Source Repository of the Cloud Lab infrastructure project. It is meant to be run by the CICD pipeline set up by the Cloud Lab infrastructure. And once the initial set up is completed with `data/defaults.yaml` file, it should be handled by the Cloud Lab's Cloud Run app only.

If there is an error during the CICD flow, as observed in the build history in the Cloud Build console, we may need to manually checkout the code and run it locally to troubleshoot and fix the issue.

To run it locally after checking out the latest code from the Cloud Source Repository, run the project factory by running

```bash
terraform init
terraform plan
terraform apply
```

## Customization

If a new blueprint needs to be added, we should make the following modifications:

1. add a new template file in `data/templates` sub-directory;
2. add new supporting modules to `modules` directory;
3. modify `main.tf` to create a list of the projects that will host the new blueprints;
4. modify `main.tf` to create a new module to deploy the blueprints in the list of projects identified in step 3;
5. thorough test with a mockup project configuration file in `data/projects`;
6. modify the UI app in the Cloud Lab infrastructure project to add this new blueprint as an option of 'template';
7. test it end to end, i.e. from UI to deployment.

## Limitations

- only one blueprint can be picked for a project, cannot combine multiple ones;
- cannot selectively update projects, it goes through all projects;
- Cloud Lab UI does not support project deletion via CICD automation, has to go through modification of project definitions and deployment.