# detach-billing

This cloud function validates and submits project creation requests

## Input

When GCP Cloud Billing detects that a budget has exceeded one of the threshholds, a message is sent via a Pub/Sub topic to this Cloud Function, containing information about the budget that sent the notification. [This page](https://cloud.google.com/billing/docs/how-to/budgets-programmatic-notifications#notification_format) contains information about the format of these alerts.

## Output
If the budget that generated the notification is 150% over-budget, then the Cloud Function removes the Billing Account from the Cloud Lab project.

## Testing
The budgets created by Cloud Run send billing notifications to the Pub/Sub Topic `cloud-lab-budget-notification-topic`. You can manually create a message to submit to the Cloud Function:
1. Navigate to the `cloud-lab-budget-notification-topic` in Pub/Sub, then at bottom navigate to `Messages --> Publish Message`.
2. Fill out the resulting form, then click `Publish`
    - The message body should consist of a JSON with the values detailed in the `Data` table on [the page that describes the notification data structures](https://cloud.google.com/billing/docs/how-to/budgets-programmatic-notifications#notification_format).
    - IMPORTANT: `Budget Display Name` should EXACTLY match the name in the `Budgets and Alerts` page. Specifically, the name should be `Budget for NIH Cloud Lab: ${project_name}`. The colon is important - it's used by the Cloud Function to find the name of the project, since that information is not passed along with the message
    - `alertThresholdExceeded` is the key value - it should be set to at least `1.5` to trigger the detachment
    - Add message attributes to the test message according to the `Attributes` table in the documentation link above. You can get this information from the `Budgets and Alerts` page.
3. Check the logs of the Cloud Function. You should see a message to the effect of `Billing disabled: ${json}`, where `json` is the response from the Billing API.
4. Navigate to the project in Resource Manager. You should see a prompt telling you to add a Billing ID to the project. You can also confirm that the Billing ID has been removed by going to the Billing page for the project.

To test other alerts, you can set `alertThresholdExceed` to a value below `1.5` - this will trigger the function, but will not result in an action since the threshold is not high enough.

Note also that different GCP services report usage and billing to the Billing page at different intervals. To simulate a more 'real-world' test, you can manually set the budget to a small value (e.g. $1) and spin up a Compute instance. Doing so should more gradually consume the budget and send alerts at the thresholds you specify. Note, however, that there is a delay from when a charge is incurred to when that charge is reported to Cloud Billing. This delay varies from service to service, and is usually on the order of minutes (but some services can see delays on the order of hours). This should be kept in mind when testing.
