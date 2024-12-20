import json
from core.logic import next_question, retrieve_sessions, transcribe
from core.auxiliary import DecimalEncoder

def handler(event, context):
    """
    Lambda function for `/next` endpoint.

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict
        Specifically contains a body key with an associated dictionary of return values.
        
        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    response = {
        "statusCode": 200, 
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",            
            "Access-Control-Allow-Methods": "POST"            
        },
    }

    request = json.loads(event.get('body', '{}'))
    payload = request.get('payload', {})
    if request.get('route') == 'transcribe':
        response['body'] = json.dumps(
            transcribe(payload['audio'])
        )
    elif request.get('route') == 'next':
        response['body'] = json.dumps(
            next_question(
                payload['session_id'], 
                payload['interview_id'], 
                payload.get('user_message')
            )
        )
    elif request.get('route') == 'retrieve':
        response['body'] = json.dumps(
            retrieve_sessions(payload),
            cls=DecimalEncoder
        )
    else:
        raise ValueError("Invalid request. Please try again.")

    return response
