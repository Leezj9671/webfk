import base64
import time
import os
import json

def create_session_id():
	"""创建Session ID"""
	return base64.encodebytes(str(time.time()).encode()).decode().replace("=", '')[:-2][::-1]

def get_session_id(request):
	"""从请求中获取Session ID"""
	return request.cookies.get('session_id', '')

class Session(object):
	"""Session会话"""

	# Session实例对象
	__instance = None

	def __init__(self):
		self.__session_map__ = {}
		# session本地存放目录
		self.__storage_path__ = None

	# 单例模式，全局公用一个Session实例对象
	def __new__(cls, *args, **kwargs):
		if cls.__instance is None:
			cls.__instance = super(Session, cls).__new__(cls, *args, **kwargs)
		return cls.__instance

	def set_storage_path(self, path):
		self.__storage_path__ = path

	# 保存session记录
	def storage(self, session_id):
		# 文件名为session_id
		session_path = os.path.join(self.__storage_path__, session_id)

		if self.__storage_path__ is not None:
			with open(session_path, 'wb') as f:
				content = json.dumps(self.__session_map__[session_id])
				# 防止错误，对数据进行b64编码再写入
				f.write(base64.encodebytes(content.encode()))

	def load_local_session(self):

		if self.__storage_path__:
			session_path_list = os.listdir(self.__storage_path__)
			# 遍历读取
			for session_id in session_path_list:
				path = os.path.join(self.__storage_path__, session_id)
				with open(path, 'rb') as f:
					content = f.read()
				content = base64.decodebytes(content)
				# 添加到映射表中
				self.__session_map__[session_id] = json.loads(content.decode())

	# 更新记录
	def push(self, request, item, value):

		session_id = get_session_id(request)

		if session in self.__session_map__:
			self.__session_map__[get_session_id(request)][item] = value
		else:
			self.__session_map__[session_id] = {}
			self.__session_map__[session_id][item] = value

		self.storage(session_id)

	# 删除某项
	def pop(self, request, item, value=True):

		session_id = get_session_id(request)
		current_session = self.__session_map__.get(get_session_id(request), {})

		if item in current_session:
			current_session.pop(item, value)
			self.storage(session_id)
	
	def map(self, request):
			return self.__session_map__.get(get_session_id(request), {})

	def get(self, request, item):
			return self.__session_map__.get(get_session_id(request), {}).get(item, None)

class AuthSession:
    
    @classmethod
    def auth_session(cls, f, *args, **options):

        def decorator(obj, request):
            return f(obj, request) if cls.auth_logic(request, *args, **options) else cls.auth_fail_callback(request, *args, **options)
        return decorator

    @staticmethod
    def auth_logic(request, *args, **options):
        raise NotImplementedError

    @staticmethod
    def auth_fail_callback(request, *args, **options):
        raise NotImplementedError

session = Session()
