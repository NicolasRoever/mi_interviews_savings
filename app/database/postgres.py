import json 
import logging 
from psycopg2 import connect, OperationalError
from psycopg2.extras import RealDictCursor 
from core.auxiliary import DecimalEncoder


class PostgreSQL(object):
    def __init__(self, database_url:str) :
        """ 
        Initialize the PostgreSQL database connection and table.
        
        Note: we are using the URL in format
            "postgresql://username:password@host:port/database"
        and we try to create a table if none exists.
        """
        self.database_url = database_url
        create_table_query = """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id VARCHAR PRIMARY KEY, data JSONB
            );
        """
        try:
            with connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_table_query)
            logging.info("PostgreSQL connection established. Should happen only once!")
        except OperationalError as e:
            logging.error(f"Database connection failed: {e}")
            raise e

    def load_remote_session(self, session_id:str) -> dict:
        """ Retrieve the interview session data from the database. """
        select_query = "SELECT data FROM sessions WHERE session_id = %s;"
        with connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(select_query, (session_id,))
                result = cursor.fetchone()
        if not result:
            logging.warning(f"Can't load session '{session_id}': not started!")
        return result['data'] if result else {}

    def delete_remote_session(self, session_id:str):
        """ Delete session data from the database. """
        delete_query = "DELETE FROM sessions WHERE session_id = %s;"
        with connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(delete_query, (session_id,))
        logging.info(f"Session '{session_id}' deleted!")

    def update_remote_session(self, session_id:str, data:dict):
        """ Update or insert session data in the database. """
        insert_query = """
            INSERT INTO sessions (session_id, data) VALUES (%s, %s)
            ON CONFLICT (session_id) DO UPDATE SET data = EXCLUDED.data;
        """
        with connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(insert_query, (session_id, json.dumps(data, cls=DecimalEncoder)))
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
        select_query = "SELECT data FROM sessions;"
        with connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(select_query)
                result = cursor.fetchall()
        if result:
            for session_obj in result:
                # Skip keys not specified
                if sessions and not session_obj['data']['session_id'] in sessions: 
                    continue
                # Add all messages in current interview session
                chats.extend([message for message in session_obj['data']['chat']])

        logging.info(f"Retrieved {len(chats)} messages!")
        return chats
