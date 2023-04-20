from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404

from airavata_django_portal_sdk import user_storage

from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import urllib.parse

from .models import ZenodoExperiment

import os
import uuid

load_dotenv()
client_id = os.getenv("ZENODO_CLIENT_ID")
client_secret = os.getenv("ZENODO_CLIENT_SECRET")
redirect_uri = os.getenv("ZENODO_REDIRECT_URI")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
authorization_base_url = 'https://zenodo.org/oauth/authorize'
token_url = 'https://zenodo.org/oauth/token'

# Create your views here.

@login_required
def home(request):

    # Example code: Airavata API client
    # Make calls to the Airavata API from your view, for example:
    #
    # experiments = request.airavata_client.searchExperiments(
    #        request.authz_token, settings.GATEWAY_ID, request.user.username, filters={},
    #        limit=20, offset=0)
    #
    # The authorization token is always the first argument of Airavata API calls
    # and is available as 'request.authz_token'. Some API methods require a
    # 'gatewayID' argument and that is available on the Django settings object
    # as 'settings.GATEWAY_ID'.
    # For documentation on other Airavata API methods, see
    # https://docs.airavata.org/en/master/technical-documentation/airavata-api/.
    # The Airavata Django Portal uses the Airavata Python Client SDK:
    # https://github.com/apache/airavata/tree/master/airavata-api/airavata-client-sdks/airavata-python-sdk


    # Example code: user_storage module
    # In your Django views, you can make calls to the user_storage module to manage a user's files in the gateway
    #
    # user_storage.listdir(request, "")  # lists the user's home directory
    # user_storage.open_file(request, data_product_uri=...)  # open's a file for a given data_product_uri
    # user_storage.save(request, "path/in/user/storage", file)  # save a file to a path in the user's storage
    #
    # For more information as well as other user_storage functions, see https://airavata-django-portal-sdk.readthedocs.io/en/latest/

    return render(request, "zenodo_integration_app/home.html", {
        'project_name': "Zenodo Integration App"
    })

@login_required
def zenodo_callback(request):

    zenodo = OAuth2Session(client_id, redirect_uri=redirect_uri,  state=request.session['zenodo_oauth_state'], scope=["deposit:write", "deposit:actions"])
    token = zenodo.fetch_token(token_url, client_secret=client_secret,authorization_response=request.build_absolute_uri())

    request.session['zenodo_oauth_token'] = token

    return redirect('/zenodo_integration_app/zenodo_upload')

@login_required
def zenodo_upload(request):
    if not (request.session.get('zenodo_oauth_token') or request.session.get('zenodo_experiment_id')):
        return redirect('/zenodo_integration_app/error.html', {
            'error_message': 'You must be logged in to Zenodo and have an experiment selected to upload files to Zenodo.'
        })

    experiment_id = request.session['zenodo_experiment_id']
    existing_experiments = ZenodoExperiment.objects.filter(user=request.user, experiment_id=experiment_id)

    existingExperimentUrls = []

    extra = {
        'client_id': client_id,
        'client_secret': client_secret
    }

    def tokenUpdater(token):
        request.session['zenodo_oauth_token'] = token

    zenodo = OAuth2Session(
        client_id, 
        token=request.session['zenodo_oauth_token'],
        auto_refresh_kwargs=extra,
        auto_refresh_url=token_url,
        token_updater=tokenUpdater)

    if existing_experiments.exists():
        for existing_experiment in existing_experiments:
            if existing_experiment.depo_id:
                for depo_id in existing_experiment.depo_id:
                    res = zenodo.get('https://zenodo.org/api/deposit/depositions/{0}'.format(depo_id))
                    if res.status_code == 200:
                        existingExperimentUrls.append(res.json()['links']['html'])
                    elif res.status_code == 410 or res.status_code == 404:
                        existing_experiment.depo_id.remove(depo_id)

                existing_experiment.save()

    try:
        _, files = user_storage.list_experiment_dir(request, experiment_id)
    except Exception as e:
        return render(request, 'zenodo_integration_app/error.html', {
            'error_message': 'Error listing experiment files: {0}'.format(e)
        })

    fileData = []
    for file in files:
        fileData.append({
            'name': file['name'],
            'data_product_uri': file['dataProductURI']
        })

    return render(request, "zenodo_integration_app/zenodo_upload.html", {
        'project_name': "Zenodo Upload Manager",
        'experiment_files': fileData,
        'existing_experiment_urls': existingExperimentUrls
    })

@login_required
def zenodo_upload_file(request):
    # Get data product URL list from request
    data_product_uri_list = request.POST.getlist('dataProductURI')

    if not request.session.get('zenodo_oauth_token'):
        return render(request, '/zenodo_integration_app/error.html', {
            'error_message': 'No Zenodo OAuth token found in session'
        })

    # Upload files to Zenodo
    zenodo = OAuth2Session(client_id, token=request.session['zenodo_oauth_token'])
    res = zenodo.post('https://zenodo.org/api/deposit/depositions', json={
        'metadata': {
            'title': 'Plasma Science Virtual Laboratory',
            'upload_type': 'dataset',
            'description': 'Plasma Science Virtual Laboratory',
            'creators': [{'name': 'Plasma Science Virtual Laboratory', 'affiliation': 'Plasma Science Virtual Laboratory'}],
            'access_right': 'closed',
        }
    }, headers={'Content-Type': 'application/json'})

    if not res.json().get('links'):
        return render(request, "zenodo_integration_app/error.html", {
            'error_message': 'Zenodo API error: ' + res.json().get('message')
        })

    depo_id = res.json()['id']
    bucket_url = res.json()['links']['bucket']
    html_url = res.json()['links']['html']

    for data_product_uri in data_product_uri_list:
        file = user_storage.open_file(request, data_product_uri=data_product_uri)
        res = zenodo.put(bucket_url + '/' + file.name, data=file)
        if res.status_code != 200:
            return render(request, "zenodo_integration_app/error.html", {
                'error_message': 'Zenodo API error: ' + res.json().get('message')
            })

    zeneodo_experiment, created = ZenodoExperiment.objects.get_or_create(user=request.user, experiment_id=request.session['zenodo_experiment_id'])
    zeneodo_experiment.depo_id.append(depo_id)
    zeneodo_experiment.save()

    return redirect(html_url)
