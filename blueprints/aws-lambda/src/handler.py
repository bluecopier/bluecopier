import sys

sys.path.insert(1, 'vendor')

from apig_wsgi import make_lambda_handler

# ! set module, wsgi_application = blueprint.links['wsgi'].split(':')
module = __import__('{{ module }}', locals(), globals(), ' ')
lambda_handler = make_lambda_handler(getattr(module, '{{ wsgi_application }}'))
