# These settings are for django-rest-framework,
#
# For documentation about all the settings see:
# https://www.django-rest-framework.org/api-guide/settings/
#

REST_FRAMEWORK = {
    # https://www.django-rest-framework.org/api-guide/settings/#compact_json
    "COMPACT_JSON": True,
    # https://www.django-rest-framework.org/api-guide/settings/#default_renderer_classes
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    # https://www.django-rest-framework.org/api-guide/settings/#default_authentication_classes
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "todo.api.drf.jwt_authentication.JWTAuthentication",
    ],
    # https://www.django-rest-framework.org/api-guide/settings/#default_permission_classes
    "DEFAULT_PAGINATION_CLASS": "todo.api.drf.pagination.PageNumberWithPageSizePagination",
    # https://www.django-rest-framework.org/api-guide/settings/#exception_handler
    "EXCEPTION_HANDLER": "todo.api.drf.exceptionhandler.custom_exception_handler",
    # https://www.django-rest-framework.org/api-guide/settings/#default_filter_backends
    # https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter
    "FILTER_BACKEND": "django_filters.rest_framework.OrderingFilter",
}
