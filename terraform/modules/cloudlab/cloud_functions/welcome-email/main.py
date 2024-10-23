# Copyright 2023 Google. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to
# your agreement with Google.
import smtplib, ssl, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.cloud import resourcemanager_v3
import os

EMAIL_SENDER = os.environ["EMAIL_SENDER"]

def welcome_email(request):
    data = eval(request.data.decode("utf-8"))
    email = str(data.get("email_address"))
    if not email:
        print(f"The email is not set. Email received: {email}")
        return ("Email address not submitted, please check your link", 400)

    project_id = str(data.get("project_id"))
    if not project_id:
        print(f"The project ID is not set. Project ID received: {project_id}")
        return ("Project ID not submitted, please check your link", 400)

    if if_project_created(project_id):
        send_email(email, project_id)
        return("Email sent to user", 200)
    print(f"Unable to find active project with id: {project_id}")
    return("Unable to find active project", 404) #return of 4xx sends task back to queue


#Checks resource manager api to see if project exists and is active
def if_project_created(project_id):
    project = "projects/" + project_id
    client = resourcemanager_v3.ProjectsClient()

    # Initialize request argument(s)
    request1 = resourcemanager_v3.GetProjectRequest(
        name=project,
    )

    # Make the request. If we get perm denied we assume the project doesn't exist
    try:
        response = client.get_project(request=request1)
    except Exception as e:
        print("Error checking project ID.")
        print(e)
        return False

    if response is not None:
        if str(response.project_id) == project_id and str(response.state) == "State.ACTIVE":
            print("Success")
            return True
    return False


def send_email(email, project_id):

    project_link = "https://console.cloud.google.com/welcome?project=" + project_id
    sender = EMAIL_SENDER

    # Create an instance of MIMEMultipart
    message = MIMEMultipart("alternative")

    message["From"] = sender
    message["To"] = email
    message["Subject"] = "Welcome to Cloud Lab"

    # Create a leaf part, which is an instance of MIMEText.
    plain_text = "Welcome to cloud lab. Your project {} has been created.".format(project_link)
    mime_text = MIMEText(plain_text)
    # Attach the leaf part the root MIMEMultipart instance.
    message.attach(mime_text)


    html_message = open('welcome-email.html').read()
    repls = ('{{project_link}}', project_link), ('{{project}}', project_id)
    for r in repls:
        html_message = html_message.replace(*r)


    # For this one, we need to change the type to `html`.
    mime_html = MIMEText(html_message, "html")
    message.attach(mime_html)
    try:
        smtp_obj = smtplib.SMTP('smtp-relay.gmail.com', 587)
        smtp_obj.sendmail(sender,email,message.as_string())
        print("Successfully sent email")
        smtp_obj.quit()
        return("Email sent to user", 200)
    except smtplib.SMTPResponseException as e:
        print(e.smtp_error)
        print(e.smtp.code)
        print("Error: unable to send email")
        smtp_obj.quit()
        return("Unable to send email to user", 400)
