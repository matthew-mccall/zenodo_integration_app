from django.conf import settings
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

from airavata_django_portal_sdk import user_storage

import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

load_dotenv()
client_id = os.getenv("ZENODO_CLIENT_ID")
client_secret = os.getenv("ZENODO_CLIENT_SECRET")
redirect_uri = os.getenv("ZENODO_REDIRECT_URI")
authorization_base_url = 'https://zenodo.org/oauth/authorize'

class ZenodoLinkViewProvider:
    display_type = "link"
    # As a performance optimization, the output view provider can be invoked
    # immediately instead of only after being selected by the user in the
    # portal.  Set to True to invoke immediately. Only use this with simple
    # output view providers that return quickly
    immediate = False
    name = "Zenodo Link View"

    def generate_data(self, request, experiment_output, experiment, output_file=None, **kwargs):

        # Use `output_file` or `output_files` to read from the output file(s).
        # See https://docs.python.org/3/tutorial/inputoutput.html#methods-of-file-objects
        # for how to read from file objects. For example, to read the entire file, use:
        #
        # entire_file = output_file.read()


        # Example code: user_storage module
        # To find other files in the experiment data directory, use the
        # user_storage module of the airavata_django_portal_sdk. You can use the
        # following to list the files and directories in the experiment data
        # directory:
        #
        # dirs, files = user_storage.list_experiment_dir(request, experiment.experimentId)
        #
        # The 'files' variable is a list of dictionaries, each one will have a
        # 'data-product-uri' key. Use the data-product-uri to open the file:
        #
        # data_product_uri = files[0]['data-product-uri']
        # data = user_storage.open_file(request, data_product_uri=data_product_uri)
        #
        # See https://airavata-django-portal-sdk.readthedocs.io/en/latest/#module-user_storage
        # for more information.


        # Example code: Airavata API client
        # Make calls to the Airavata API from the output view provider, for example:
        #
        # data_product = request.airavata_client.getDataProduct(
        #        request.authz_token, experiment_output.value)
        #
        # In this example, the DataProduct object is loaded for the output file.
        # 'experiment_output.value' has the Data Product URI for the output
        # file, the unique identifier in the Airavata API for this output file.
        # The returned DataProduct object contains metadata about the output
        # file and the location(s) where it is stored. See
        # http://airavata.apache.org/api-docs/master/replica_catalog_models.html#Struct_DataProductModel
        # for more information.
        #
        # The authorization token is always the first argument of Airavata API calls
        # and is available as 'request.authz_token'. Some API methods require a
        # 'gatewayID' argument and that is available on the Django settings object
        # as 'settings.GATEWAY_ID'.
        # For documentation on other Airavata API methods, see
        # https://docs.airavata.org/en/master/technical-documentation/airavata-api/.
        # The Airavata Django Portal uses the Airavata Python Client SDK:
        # https://github.com/apache/airavata/tree/master/airavata-api/airavata-client-sdks/airavata-python-sdk

        request.session['zenodo_experiment_id'] = experiment.experimentId
        
        if request.session['zenodo_oauth_token']:
            return {
                "label": "Proceed to Zenodo Upload Manager",
                "url": "/zenodo_integration_app/zenodo_upload/"
            }

        zenodo = OAuth2Session(client_id, redirect_uri=redirect_uri, scope="deposit:write deposit:actions")
        authorization_url, state = zenodo.authorization_url(authorization_base_url)

        request.session['zenodo_oauth_state'] = state

        return {
            "label": "Authenticate with Zenodo",
            "url": authorization_url
        }