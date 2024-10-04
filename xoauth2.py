import urllib.parse
import urllib.request
import json

GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'
REDIRECT_URI = 'https://oauth2.dance/'
client_id = '71648777682-resf0ugd2jcohfigajlnrahs5ah4797u.apps.googleusercontent.com'
client_secret = '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'


def AccountsUrl(command):
  """Generates the Google Accounts URL.

  Args:
    command: The command to execute.

  Returns:
    A URL for the given command.
  """
  return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)

def UrlEscape(text):
  # See OAUTH 5.1 for a definition of which characters need to be escaped.
  return urllib.parse.quote(text, safe='~-._')

def FormatUrlParams(params):
  """Formats parameters into a URL query string.

  Args:
    params: A key-value map.

  Returns:
    A URL query string version of the given parameters.
  """
  param_fragments = []
  for param in sorted(params.items(), key=lambda x: x[0]):
    param_fragments.append('%s=%s' % (param[0], UrlEscape(param[1])))
  return '&'.join(param_fragments)

def GeneratePermissionUrl(client_id, scope='https://mail.google.com/'):
  """Generates the URL for authorizing access.

  This uses the "OAuth2 for Installed Applications" flow described at
  https://developers.google.com/accounts/docs/OAuth2InstalledApp

  Args:
    client_id: Client ID obtained by registering your app.
    scope: scope for access token, e.g. 'https://mail.google.com'
  Returns:
    A URL that the user should visit in their browser.
  """
  params = {}
  params['client_id'] = client_id
  params['redirect_uri'] = REDIRECT_URI
  params['scope'] = scope
  params['response_type'] = 'code'
  params['access_type'] = 'offline'
  params['prompt'] = 'consent'
  return '%s?%s' % (AccountsUrl('o/oauth2/auth'),
                    FormatUrlParams(params))

def AuthorizeTokens(client_id, client_secret, authorization_code):
  """Obtains OAuth access token and refresh token.

  This uses the application portion of the "OAuth2 for Installed Applications"
  flow at https://developers.google.com/accounts/docs/OAuth2InstalledApp#handlingtheresponse

  Args:
    client_id: Client ID obtained by registering your app.
    client_secret: Client secret obtained by registering your app.
    authorization_code: code generated by Google Accounts after user grants
        permission.
  Returns:
    The decoded response from the Google Accounts server, as a dict. Expected
    fields include 'access_token', 'expires_in', and 'refresh_token'.
  """
  params = {}
  params['client_id'] = client_id
  params['client_secret'] = client_secret
  params['code'] = authorization_code
  params['redirect_uri'] = REDIRECT_URI
  params['grant_type'] = 'authorization_code'
  request_url = AccountsUrl('o/oauth2/token')

  response = urllib.request.urlopen(request_url, urllib.parse.urlencode(params).encode('utf-8')).read()
  return json.loads(response)

print(GeneratePermissionUrl(client_id))

authorization_code = input('Enter verification code: ')
response = AuthorizeTokens(client_id, client_secret, authorization_code)
refresh_token = response['refresh_token']
access_token = response['access_token']

with open("refresh.txt", "w") as file:
    file.write(refresh_token)