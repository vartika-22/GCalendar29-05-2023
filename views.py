from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
REDIRECT_URI = 'http://yourdomain.com/rest/v1/calendar/redirect/'


class GoogleCalendarInitView(View):
    def get(self, request):
        flow = Flow.from_client_secrets_file('path/to/client_secrets.json',
                                             scopes=SCOPES,
                                             redirect_uri=REDIRECT_URI)
        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true')
        request.session['oauth_state'] = state
        return HttpResponseRedirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        state = request.session.get('oauth_state')
        flow = Flow.from_client_secrets_file('path/to/client_secrets.json',
                                             scopes=SCOPES,
                                             redirect_uri=REDIRECT_URI,
                                             state=state)
        flow.fetch_token(authorization_response=request.build_absolute_uri(),
                         client_secret=CLIENT_SECRET)
        credentials = flow.credentials

        service = build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(calendarId='primary',
                                              maxResults=10).execute()
        events = events_result.get('items', [])

        return HttpResponse(json.dumps(events),
                            content_type='application/json')
