from werkzeug.exceptions import default_exceptions
from functools import wraps
from flask import make_response, jsonify, request
import time
import traceback as tb
from setup.log import Logger
from parameters import WHITELISTED_DOMAINS

# Specialized logging logger
logger = Logger()

def wrap_flask_errors():
	""" Wrap flask app-level errors as standardized JSON responses. """
	return {
		error_code: {
			error: lambda ex: make_response(jsonify({
				"http_code": getattr(ex, "http_code", 405 if "Method" in str(ex) else 400),
				"meta": {
					"type": type(ex).__name__,
					"error": str(ex) or "",
					"tb": tb.format_exc() if not ("NoneType" in tb.format_exc()) else ""
				},
				"message": str(ex) or getattr(ex, "description", ""),
			}), 
			getattr(ex, "http_code", error_code)
		)} for error_code, error in default_exceptions.items()
	}

def response_log(response, status, start_time, key="info"):
	""" Log outgoing response. Useful for debugging/monitoring. """
	logger.log(key=key, message={
		"payload":request.get_json(force=True, silent=True) or {},
		"url":request.url,
		"duration":time.time() - start_time,
		"response":response,
		"http_code":status,
		"type":response["type"] if (isinstance(response, dict) and 
			response.get("tb")) else "RequestSuccessful"
	})

def handle_500(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		start_time = time.time()
		try:
			response = f(*args, **kwargs)
		except Exception as e:
			http_code = getattr(e, "http_code", None) or getattr(e, "code", 500)
			message = str(e) or getattr(e, "message", "Service failed")
			meta = {"type":type(e).__name__,"tb":tb.format_exc(),"str":message}
			response_log(meta, http_code, start_time, key="error")
			response = make_response(jsonify(meta), http_code)
		return response
	return decorated
