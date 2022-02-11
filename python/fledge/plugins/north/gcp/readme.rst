.. Links in new tabs

.. |Google Cloud Console| raw:: html

   <a href="https://console.cloud.google.com" target="_blank">GCP Console</a>

.. |Pub/Sub section| raw:: html

   <a href="https://console.cloud.google.com/cloudpubsub" target="_blank">Pub-Sub</a>

.. |Service Accounts page| raw:: html

    <a href="https://console.cloud.google.com/iam-admin/serviceaccounts" target="_blank">Service Account</a>

*****************
Fledge North GCP
*****************

 Sending image data to Google Cloud for training machine learning models

Prerequisite
~~~~~~~~~~~~

I. Configuring a Separate Cloud Pub/Sub Topic

    a) Setting up your Pub/Sub topic and subscription
        1) Log into |Google Cloud Console|.

        2) Go to the |Pub/Sub section| of the Google Cloud Console.
            Follow the prompt to enable the API.

        3) Click Create a topic. Publishing applications send messages to topics. Let say use 'camera-data' as the Name.

             By default, the console will also create a default subscription with the name: camera-data-sub. Keep the ‘Add a default subscription’ enabled
             Click ‘Create topic’ to create the topic and default subscription

    b) Creating service account credentials

       1) In the Cloud Console, go to the |Service Accounts page|.

       2) Select your project.

       3) Click Create Service Account.

       4) In the Service account name field, enter a name: pubsub-publisher. The Cloud Console fills in the Service account ID field based on this name.

       5) Click Create and continue.

       6) The service account needs publishing permissions. Use the Select a role dropdown to add the Pub/Sub Publisher role.
               Tip: Use the string pub to filter for Pub/Sub roles.

       7) Click Add another role and add Pub/Sub Subscriber.

       8) Click Done to finish creating the service account.
               Do not close your browser window. You will use it in the next step.

       9) Download a JSON key for the service account you just created. The client library uses the key to access the Pub/Sub API.

          - In the Cloud Console, click the email address for the service account that you created.
          - Click Keys.
          - Click Add key, then click Create new key.
          - Click Create. A JSON key file is downloaded to your computer.
          - Rename the key file to credentials.json (OPTIONAL)

II. Install pip requirements `from <../../../../requirements-gcp.txt>`_

   .. code-block:: console

       pip3 install -Ir requirements-gcp.txt --user --no-cache-dir

   .. note::

        You may see errors on installing pip requirements on some platforms which required pip upgrade.
        Use pip3 install --upgrade pip


III. Load JSON key for service account in certificate store.

    1) via curl command

       .. code-block:: console

           $ curl -sF "cert=@credentials.json" -F "overwrite=1" http://localhost:8081/fledge/certificate

       .. note::
           
            where credentials.json is the service account file

    2) via GUI

       Go to Certificate Store -> Import -> Choose certificate -> Import

