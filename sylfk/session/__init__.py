import base64
import time

def create_session_id():
	return base64.encodebytes(str(time.time()).encode()).decode().replace("=", '')[:-2][::-1]

def get_session_id(request):
	return request.cookies.get('session_id', '')

class Session(object):
	"""docstring for Session"""

	__instance = None

	def __init__(self, arg):
		self.__session_map__ = {}

	def __new__(cls, *args, **kwargs):
		if cls.__instance is None:
			cls.__instance = super(Session, cls).__new__(cls, *args, **kwargs)
		return cls.__instance
	
	def push(self, request, item, value):
		session_id = get_session_id(request)
		if session in self.__session_map__:
			self.__session_map__[get_session_id(request)][item] = value
		else:
			self.__session_map__[session_id] = {}
			self.__session_map__[session_id][item] = value

	def pop(self, request, item, value=True):
		current_session = self.__session_map__.get(get_session_id(request), {})
		
		if item in current_session:
			current_session.pop(item, value)

session = Session()