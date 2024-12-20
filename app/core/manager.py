from datetime import datetime
import logging


class InterviewManager(object):
    """
    Class to manage the conversation history for an interview 
    between the user and the AI-interviewer.

    Args:
        client: database manager
        session_id: (str) unique interview session key
    """
    def __init__(self, client, session_id:str):
        self.client = client
        self.session_id = session_id
    
    def begin_session(self, parameters:dict):
        """
        Loads interview data and variables into session.
        Note indices are 1-indexed. 

        Args:
            parameters: (dict) interview guidelines
        """
        logging.info(f"Starting new session '{self.session_id}'")
        self.data = {
            'session_id': self.session_id,
            'current_topic_idx': 1,
            'current_question_idx': 1,
            'current_finish_idx': 1,
            'chat': [],
            'flagged_messages': [],
            'terminated': False,  
            'summary': '',
            'parameters': parameters
        }
        # Add starting interview question to transcript
        self.add_message(parameters['first_question'], type="question")
        self.update_session()

    def resume_session(self):
        """ Load (remote) data into current Interview object. """
        self.data = self.client.load_remote_session(self.session_id)
        assert self.data.get('session_id') == self.session_id
        logging.info(f"Resumed existing interview session '{self.session_id}'")

    def get_session_info(self, key:str=None):
        """ Get data associated with current interview session (key). """
        return self.data[key] if key else self.data

    def is_terminated(self) -> bool:
        """ If interview has been terminated. """
        return self.data['terminated']

    def flag_risk(self, message:str):
        """ Flag possible security risk. """
        logging.warning("Flagging message for possible risk...")
        flagged = [str(datetime.now())]
        if self.data['parameters'].get('store_flagged_messages'):
            flagged.append(message)
        self.data["flagged_messages"].append(flagged)

    def flagged_too_often(self) -> bool:
        """ Check if the conversation has been flagged too often. """
        if len(self.data['flagged_messages']) >= self.data['parameters'].get('max_flags_allowed', 3):
            self.terminate("security_flags_exceeded")
            return True        
        return False

    def add_message(self, message:str, type:str):
        """ Add to chat transcript. """
        self.data['chat'].append({
            'order':len(self.data['chat']),
            'type':type, 
            'content':message,
            'topic_idx':self.data['current_topic_idx'],
            'question_idx':self.data['current_question_idx'],
            'time':str(datetime.now()),
            'session_id':self.session_id
        })

    def repeated_messages(self, message:str, min_length:int=5) -> bool:
        """ Check if user has repeated the same message multiple times. """
        if len(self.data["chat"]) < min_length: # Ignore for short chats
            return False
        # Return if the last or penultimate message of the user are the same
        return message in (chat['content'] for chat in self.data["chat"][-2:])

    def terminate(self, reason:str="end_of_interview"):
        """ Record termination of interview. """
        self.data["terminated"] = True
        logging.info(f"Terminating interview because: '{reason}'")

    def update_summary(self, summary:str):
        """ Update summary of prior interview. """
        self.data["summary"] = summary

    def get_current_topic(self) -> int:
        """ Return topic index. """
        return min(int(self.data["current_topic_idx"]), len(self.data['parameters']['interview_plan']))

    def get_current_topic_question(self) -> int:
        """ Return question index within topic. """
        return int(self.data["current_question_idx"])

    def get_final_question(self) -> str:
        """ Get next "final" (i.e. closing) interviewer question/comment. """
        final_questions = self.data['parameters'].get('closing_questions', [])
        try:
            out = final_questions[int(self.data["current_finish_idx"]) - 1]
        except IndexError:
            out = ""
        else:
            # Increment counter of which 'final' question we are on
            self.data["current_finish_idx"] += 1
        return out

    def update_transition(self, summary:str):
        """ 
        Having transitioned, update topic counter (and reset question). 
        
        If summary agent is provided, also update interview summary of 
        prior topics covered for future context.
        """
        self.data["current_question_idx"] = 1  
        self.data["current_topic_idx"] += 1
        if self.data['parameters'].get('summary'):
            self.update_summary(summary)

    def update_closing(self):
        self.data["current_question_idx"] = 99  
        self.data["current_topic_idx"] = 99

    def update_probe(self):
        """ Having probed within topic, simply increment question counter. """ 
        self.data["current_question_idx"] += 1  

    def update_session(self):
        """ Update session in remote database """ 
        self.client.update_remote_session(self.session_id, self.data)
   