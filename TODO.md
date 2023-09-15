Things to do before first release
=================================

Things to prove out concept
===========================

Can target VSCode first:

$ blueprint generate django --open-in-editor

- Actions: Start webserver, Run tests, Run tests with coverage, Profile etc.

Editor support
==============
* VSCode
* IntelliJ
* GitHub Codespaces

TODO

Ideas for combining several README templates
============================================
blueprint/python: README (parent)
blueprint/python_django: README (child)
blueprint/github_action: README (grandchild)
blueprint/pytest: README (great-grandchild)
etc

{% block examples %}
{% endblock %}

{% block unit_testing %}
{% endblock %}

TODO items
==========

# TODO: dogfooding enable/disable things in current repo
# TODO: Enable/disable features
# TODO: tool: documentation (readme, contribution, code of conduct, security, authors, icons)
# TODO: tool: github (badges, dependabot)
# TODO: tool: github pages
# TODO: isort (ruff?)
# TODO: alex: https://github.com/get-alex/alex
# TODO: creating carbon database django+url from scratch
# TODO: create venv
# TODO: coverage
# TODO: Dockerfile
# TODO: js/ts (eslint)
# TODO: Performance is important, 1min from start to working app
# TODO: package manager abstraction is needed soon, so we can resolve dependencies better
# TODO: pre-commit hooks depends on pyproject generation
# TODO: separate apig_wsgi from aws-lambda-zip-url

# 1. Generate Code
# 2. Generate Tests
# 3. Generate CI/CD (GitHub Actions), including local development (docker-compose)
# 4. Generate Documentation & Github pages
# 5. Generate Delivery (Dockerfile & Serverless, AWS/GCP/Azure)
#    a) RDS
#    b) S3
#    c) Redis/RabbitMQ
# 6. Generate monitoring (Sentry, Datadog, New Relic)

# MVP:
# 2-3 high quality templates (django+drf,django+strawberry,nestjs) with both frontend and backend
# with options to deploy to more than one place (AWS, GCP, Azure, Heroku, Vercel, Netlify, Render, etc.)
# with multiple compute options (serverless, docker, kubernetes, etc.)
# with multiple database options (RDS, Aurora, DynamoDB, MongoDB, etc.)
# Web interface with a wizard to generate and deploy
# Auth using GitHub
