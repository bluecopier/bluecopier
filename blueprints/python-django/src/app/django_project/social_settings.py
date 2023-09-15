# Actually a Django Setting, but it seems more relevant to put it here.
# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#authentication-backends
AUTHENTICATION_BACKENDS = (
    "social_core.backends.open_id.OpenIdAuth",
    "social_core.backends.google.GoogleOpenId",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.google.GoogleOAuth",
    "social_core.backends.twitter.TwitterOAuth",
    "social_core.backends.yahoo.YahooOpenId",
    # https://docs.djangoproject.com/en/4.2/ref/contrib/auth/#django.contrib.auth.backends.ModelBackend
    "django.contrib.auth.backends.ModelBackend",
)

# https://python-social-auth.readthedocs.io/en/latest/configuration/django.html#json-field-support
SOCIAL_AUTH_JSONFIELD_ENABLED = True

# https://python-social-auth.readthedocs.io/en/latest/configuration/django.html#personalized-configuration
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)
