import logging
from core.auxiliary import execute_queries, fill_prompt_with_interview_state, chat_to_string
from io import BytesIO
from base64 import b64decode

# Patch for Python3.13 runtime
import sys
if sys.version.startswith('3.13'):
    import collections
    if not hasattr(collections, 'MutableSet'):
        collections.MutableSet = collections.abc.MutableSet
        collections.MutableMapping = collections.abc.MutableMapping

from openai import OpenAI


class Agent(object):
    """ Class to manage LLM-based agents. """
    def __init__(self, timeout:int=30, max_retries:int=3):
        self.client = OpenAI(timeout=timeout, max_retries=max_retries)
        logging.info("OpenAI client instantiated. Should happen only once!")

    def transcribe(self, audio, model:str="whisper-1") -> str:
        """ Transcribe audio file. """
        audio_file = BytesIO(b64decode(audio))
        audio_file.name = "audio.webm"

        response = self.client.audio.transcriptions.create(
          model=model, 
          file=audio_file,
          language="en" # English language input
        )
        return response.text

    def construct_query(self, tasks:list, interview_state:dict) -> dict:
        """ 
        Construct OpenAI API completions query, 
        defaults to `gpt-4o-mini` model, 300 token answer limit, and temperature of 0. 
        For details see https://platform.openai.com/docs/api-reference/completions.
        """
        parameters = interview_state['parameters']
        return {
            task: {
                "messages": [{
                    "role":"user", 
                    "content": fill_prompt_with_interview_state(
                        parameters[task]['prompt'], 
                        parameters['interview_plan'],
                        interview_state
                    )
                }],
                "model": parameters[task].get('model', 'gpt-4o-mini'),
                "max_tokens": int(parameters[task].get('max_tokens', 300)),
                "temperature": float(parameters[task].get('temperature', 0))
            } for task in tasks
        }

    def review_answer(self, message:str, interview_state:dict) -> bool:
        """ Moderate answers: Are they off topic or contain harmful content? """
        interview_state['user_message'] = message
        assert interview_state["chat"][-1]["type"] == "question"
        response = execute_queries(
            self.client.chat.completions.create,
            self.construct_query(['moderator'], interview_state)
        )
        return "yes" in response["moderator"].lower()

    def review_question(self, next_question:str) -> bool:
        """ Moderate questions: Are they flagged by the moderation endpoint? """
        response = self.client.moderations.create(
            model="omni-moderation-latest",
            input=next_question,
            )
        return response.to_dict()["results"][0]["flagged"]
        
    def probe_within_topic(self, interview_state:dict) -> str:
        """ Return next 'within-topic' probing question. """
        response = execute_queries(
            self.client.chat.completions.create,
            self.construct_query(['probe'], interview_state)
        )
        return response['probe']

    def transition_topic(self, interview_state:dict) -> tuple[str, str]:
        """ 
        Determine next interview question transition from one topic
        cluster to the next. If have defined `summarize` model in parameters
        will also get summarization of interview thus far.
        """
        summarize = interview_state['parameters'].get('summarize')
        tasks = ['summary','transition'] if summarize else ['transition']
        response = execute_queries(
            self.client.chat.completions.create,
            self.construct_query(tasks, interview_state)
        )
        return response['transition'], response.get('summary', '')
