# These settings are for django-cors-headers,
#
# For documentation about all the settings see:
# https://github.com/adamchainz/django-cors-headers
#

# A list of origins that are authorized to make cross-site HTTP requests.
# The origins in this setting will be allowed, and the requesting origin will be
# echoed back to the client in the access-control-allow-origin header.
# Defaults to [].
CORS_ALLOWED_ORIGINS = []

# The list of non-standard HTTP headers that you permit in requests from the browser.
# Sets the Access-Control-Allow-Headers header in responses to preflight requests.
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
