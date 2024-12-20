from boto3 import resource
import logging 

class DynamoDB(object):
    def __init__(self, table_name:str) :
        """ 
        Initialize the Dynamo database table.
        """
        logging.info(f"Setting up DynamoDB for table '{table_name}'")
        self.table = resource('dynamodb').Table(table_name)
        logging.info("DynamoDB table connection established. Should happen only once!")

    def load_remote_session(self, session_id:str) -> dict:
        """ Retrieve the interview session data from the database. """
        result = self.table.get_item(Key={'session_id':session_id})
        if result.get('Item'):
            return result['Item']
        logging.warning(f"Can't load session '{session_id}': not started!")
        return {}

    def delete_remote_session(self, session_id:str):
        """ Delete session data from the database. """
        self.table.delete_item(Key={"session_id":session_id})
        logging.info(f"Session '{session_id}' deleted!")

    def update_remote_session(self, session_id:str, data:dict):
        """ Update or insert session data in the database. """
        assert 'session_id' in data
        assert data['session_id'] == session_id
        self.table.put_item(Item=data)
        logging.info(f"Session '{session_id}' updated!")

    def retrieve_sessions(self, sessions:list=None) -> list:
        """ 
        Retrieve chat history (list of dicts) for specified sessions (list of dicts)
        or *all* sessions if no sessions specified in optional argument.

        Returns
            chats: (list) of "long" form data with one session-message per row, e.g.
                [
                    {'session_id':101, 'time':0, 'role':'interviewer', 'message':'Hello', ...}
                    {'session_id':101, 'time':1, 'role':'respondent', 'message':'World', ...}
                    ...
                ]
        """
        chats = []
        last_eval = None
        while True:
            # Handle multiple chunks with contiguous scan
            resp = self.table.scan(ExclusiveStartKey=last_eval) if last_eval else self.table.scan()
            for session in resp.get('Items',[]):
                # Skip keys not specified
                if sessions and not session['session_id'] in sessions: 
                    continue
                # Add all messages in current interview session
                chats.extend([message for message in session['chat']])
            if not resp.get('LastEvaluatedKey'): break
            last_eval = resp['LastEvaluatedKey']

        logging.info(f"Retrieved {len(chats)} messages!")
        return chats
