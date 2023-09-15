- Focus on AWS initially

Compute options
===============

AWS Lambda
==========

1. Zip file
2. Function URL

AWS ECS
=======

1. Build docker image
2. Push to ECR
3. Deploy to ECS via Fargate


Pulumi
======

1. Generate Pulumi/TF Deployment Code/YML/JSON based on input
2. Create stack and configure aws credentials
3. Install vendor dependencies (e.g Flask and requests) and build zip file/docker image
4. Deploy stack


How to deploy
=============

Datadog uses a cloudformation template that creates an IAM users and a lambda function
which can read lots of things. Could eventually do the same, but need to track down the exact permissions
required for all the different things we want to create/delete.
Probably easier to just ask for admin account_id/secret_key and use that to create/delete things.

Datadogs current approach to their integration
==============================================

// https://eu-north-1.console.aws.amazon.com/cloudformation/home?
// region=eu-north-1#/stacks/quickcreate?
// param_APIKey=9cbd65a51b0360548293bb91d4ac1071&
// param_APPKey=93f0ecc5fc4cb6a9e7dfc1e32e7e9ced7ff68d0f&
// param_CloudSecurityPostureManagement=false&
// param_DatadogSite=datadoghq.eu&
// param_InstallLambdaLogForwarder=true&
// stackName=DatadogIntegration&
// templateURL=https%3A%2F%2Fdatadog-cloudformation-template-quickstart.s3.amazonaws.com%2Faws%2Fmain_v2.yaml
                                                                                            nn
https://datadog-cloudformation-template-quickstart.s3.amazonaws.com/aws/main_v2.yaml
https://datadog-cloudformation-template-quickstart.s3.amazonaws.com/aws/datadog_integration_api_call_v2.yaml
https://datadog-cloudformation-template-quickstart.s3.amazonaws.com/aws/datadog_integration_role.yaml
