#!/bin/bash

echo "----------------------------------- IMPORTANT NOTES: --------------------------------------"
echo "This file deploys your application. You should run:"
echo "    $0 <OPENAI_API_KEY> <S3_BUCKET>"; 
echo
echo "Or if you prefer, export those variables as environment variables or even modify this file "
echo "directly defining the appropriate variables with your OpenAI API key and chosen bucket name"
echo "Then, run without arguments the script: "; echo "    $0    "; 

echo "Make sure that environment S3_BUCKET and (optionally) DYNAMO_TABLE matches those during setup."
echo "-------------------------------------------------------------------------------------------"
echo 

OPENAI_API_KEY=${1:-${OPENAI_API_KEY}}
BUCKET_NAME=${2:-${S3_BUCKET}}
TABLE_NAME=${DYNAMO_TABLE:-'interview-sessions'}

if [ -z "$BUCKET_NAME" ]
then
    echo "Error: S3_BUCKET cannot be empty and must match that used during setup!"; echo; exit
fi
if [ -z "$OPENAI_API_KEY" ]
then
    echo "Error: OPENAI_API_KEY cannot be empty!"; echo; exit
fi

echo; echo "Building application including local changes..."
sam build \
	--template aws_config/template.yaml \
	--use-container \
	--no-cached


echo; echo "Deploying to cloud using provided OpenAI API Key, S3 bucket, and Dynamo table" 
sam deploy \
	--parameter-overrides OpenAIAPIKey=${OPENAI_API_KEY} Port=${PORT:-8000} TableName=$TABLE_NAME \
	--no-confirm-changeset \
	--no-fail-on-empty-changeset \
	--s3-bucket $BUCKET_NAME

echo
echo "------------------------------- IMPORTANT NOTES: ------------------------------------"
echo "Take note of the API Gatekey endpoint published above. This is where to make requests."
echo "If no changes have been deployed your endpoint will remain the same. Good luck!"
echo "-------------------------------------------------------------------------------------"
echo