import json
import logging
import os
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from core.auxiliary import DecimalEncoder


class RedisWrapper(object):
    def __init__(self) :
        """ 
        Initialize the Redis connection using required environment variables.
        """
        self.client = Redis(
            host=os.environ["REDIS_HOST"], 
            port=os.environ["REDIS_PORT"],
            password=os.environ["REDIS_PASSWORD"]
        )
        try:
            self.client.keys()
            logging.info("Redis connection established. Should happen only once!")
        except RedisConnectionError as e:
            logging.error(f"Database connection failed: {e}")
            raise e
        logging.info("Redis connection established -- should happen only once!")

    def load_remote_session(self, session_id:str) -> dict:
        """ Retrieve the interview session data from the database. """
        if self.client.exists(session_id):
            return json.loads(self.client.get(session_id))
        logging.warning(f"Can't load session '{session_id}': not started!")
        return {}

    def delete_remote_session(self, session_id:str):
        """ Delete session data from the database. """
        self.client.delete(session_id)
        logging.info(f"Session '{session_id}' deleted!")

    def update_remote_session(self, session_id:str, data:dict):
        """ Update or insert session data in the database. """
        assert isinstance(data, dict)
        self.client.set(session_id, json.dumps(data, cls=DecimalEncoder))
        assert self.client.get(session_id)
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
        for session_id in self.client.keys():
            # Skip keys not specified
            if sessions and not session_id in sessions: 
                continue
            # Add all messages in current interview session
            chats.extend([message for message in json.loads(
                self.client.get(session_id))['chat']
            ])
        logging.info(f"Retrieved {len(chats)} messages!")
        return chats

