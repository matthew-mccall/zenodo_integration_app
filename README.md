# Zenodo Integration App
This is a custom Django Application and View Provider that allows users to upload experiment results to Zenodo

## Getting Started
### Install and Setup the Portal
> [!NOTE]
> The following is adapted from the [Airvata Django Portal Custom UI Tutorial](https://apache-airavata-django-portal.readthedocs.io/en/latest/tutorial/custom_ui_tutorial/) and the [Zenodo Developer Documentation](https://developers.zenodo.org)
1. [Install the Prerequisites](https://apache-airavata-django-portal.readthedocs.io/en/latest/tutorial/custom_ui_tutorial/#prerequisites). This application was developed and tested with Docker.
2. [Run a Gaussian computational experiment in the Django portal](https://apache-airavata-django-portal.readthedocs.io/en/latest/tutorial/custom_ui_tutorial/#hands-on-run-a-gaussian-computational-experiment-in-the-django-portal).
3. Clone this repository and change your working directory into the repository: 
```shell
git clone https://github.com/matthew-mccall/zenodo_integration_app.git
cd zenodo_integration_app
``` 
4. Setup the local Django portal development environment:
```shell
docker run --pull always -d --name custom-ui-tutorial -p 8000:8000 -v "${PWD}:/extensions" -v "${PWD}/settings_local.py:/code/django_airavata/settings_local.py" apache/airavata-django-portal
```
5. Run the following to load the default set of CMS pages:
```shell
docker exec custom-ui-tutorial python manage.py load_cms_data new_default_theme
```
6. Go to http://localhost:8000, click on Login in, enter your username and password. On the dashboard you should see the your experiments listed on the right hand side.
7. Install the zenodo_integration_app package into the Django portal's virtual environment:
```shell
docker exec -w /extensions custom-ui-tutorial pip install -e .
docker exec custom-ui-tutorial touch /code/django_airavata/wsgi.py
```
### Register the view provider:
1. Log into your local Django Portal instance at http://localhost:8000.
2. In the menu at the top, select Settings.
3. Click on the Gaussian16 application.
4. Click on the Interface tab.
5. Scroll down to the Output Field: Gaussian-Application-Output.
6. Verify that the following is in the Metadata section:
```json
{
   "output-view-providers": ["zenodo_link_view"]
}
```
### Register the Application on Zenodo
1. Log into Zenodo and go to your [Applications](https://zenodo.org/account/settings/applications/)
2. Click `New Application` under Developer applications
3. Fill out Name and Website URL. For Redirect URIs, use `http://localhost:8000/zenodo_integration_app/zenodo_callback/`. Client type is Confidential.
4. Inside the repository root folder, create a `.env` file with `ZENODO_CLIENT_ID` set to the Client ID, `ZENODO_CLIENT_SECRET` set to the Client Secret, and `ZENODO_REDIRECT_URI` to `http://localhost:8000/zenodo_integration_app/zenodo_callback/`.
5. Reload the Django portal development server:
```shell
docker exec custom-ui-tutorial touch /code/django_airavata/wsgi.py
```

At this point both the Custom Output Viewer and Custom Application should be available for use and functional for the Gaussian16 experiment within the portal.