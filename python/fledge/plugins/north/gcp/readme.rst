.. Links in new tabs

.. |gcp console| raw:: html

   <a href="https://console.cloud.google.com" target="_blank">GCP Console</a>

.. |pubsub| raw:: html

   <a href="https://console.cloud.google.com/cloudpubsub" target="_blank">Pub-Sub</a>

.. |service account| raw:: html

    <a href="https://console.cloud.google.com/iam-admin/serviceaccounts" target="_blank">Service Account</a>

*****************
Fledge North GCP
*****************

 Sending image data to Google Cloud for training machine learning models

Prerequisite
~~~~~~~~~~~~
1. Configuring a Separate Cloud Pub/Sub Topic
    a) Setting up your Pub/Sub topic and subscription
        i) Log into Google Cloud Console. |gcp console|

        ii) Go to the Pub/Sub section of the Google Cloud Console. |pubsub|

            Follow the prompt to enable the API.
        iii) Click Create a topic. Publishing applications send messages to topics. Use camera-data as the Name.

             By default, the console will also create a default subscription with the name: camera-data-sub. Keep the ‘Add a default subscription’ enabled

             Click ‘Create topic’ to create the topic and default subscription

     b) Creating service account credentials
        i)    In the Cloud Console, go to the Service Accounts page. |service account|
        ii)   Select your project.
        iii)  Click Create Service Account.
        iv)   In the Service account name field, enter a name: pubsub-publisher. The Cloud Console fills in the Service account ID field based on this name.
        v)    Click Create and continue.
        vi)   The service account needs publishing permissions. Use the Select a role dropdown to add the Pub/Sub Publisher role.
               Tip: Use the string pub to filter for Pub/Sub roles.
        vii)  Click Add another role and add Pub/Sub Subscriber.
        viii) Click Done to finish creating the service account.
               Do not close your browser window. You will use it in the next step.
        ix)    Download a JSON key for the service account you just created. The client library uses the key to access the Pub/Sub API.
            - In the Cloud Console, click the email address for the service account that you created.
            - Click Keys.
            - Click Add key, then click Create new key.
            - Click Create. A JSON key file is downloaded to your computer.
            - Rename the key file to credentials.json (OPTIONAL)

2. Install pip requirements

    .. code-block:: console

        pip3 install -Ir requirements.txt --user --no-cache-dir


3. Load JSON key for service account in certificate store.

    a) via curl command

        .. code-block:: console

            $ curl -sF "cert=@credentials.json" -F "overwrite=1" http://localhost:8081/fledge/certificate

            where credentials.json is the service account file

    b) via GUI

        Go to Certificate Store -> Import -> Choose certificate -> Import
