import logging
import json
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR")

class Logger(object):
	""" 
	Logging wrapper for logging complex objects like request/response. 
	By default will log 'warning'-level messages.
	"""
	def __init__(self):
		logging.basicConfig(
			level=getattr(logging, LOG_LEVEL),
			format="%(asctime)s %(name)-20s %(levelname)-8s %(message)s",
			encoding='utf-8',
			handlers=[logging.StreamHandler()]
		)
		self.logger = logging.getLogger("")

	def log(self, module="", key="info", message="", exclude=["cookies"], exc=False):
		log_type_dict = {
			"debug": logging.getLogger(module).debug,
			"info": logging.getLogger(module).info,
			"warning": logging.getLogger(module).warning,
			"error": logging.getLogger(module).error,
			"critical": logging.getLogger(module).critical
		}
		log_type_dict[key](self._format_message(message, exclude=exclude), exc_info=exc)

	def _format_message(self, obj, exclude=[]):
		def jsonable(obj):
			try: return json.dumps(obj)
			except: return None

		if isinstance(obj, dict): 
			log_dict = {}
			for k,v in obj.items():
				if k in exclude: continue
				if jsonable(v): log_dict[k] = v
				else: log_dict[k] = {}
			return jsonable(log_dict)
		return ". ".join(str(obj).split("\n"))

	def close(self):
		self.log(message="Closing log handlers.")
		for handler in self.logger.handlers[:]:
			self.logger.removeHandler(handler)
			handler.flush()
			handler.close()


