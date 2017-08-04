
class View(object):
	"""docstring for View"""
	methods = None
	methods_meta = None

	def dispatch_request(self, request, *args, **options):
		raise NotImplementedError

	@classmethod
	def get_func(cls, name):
		
		def func(*args, **kwargs):
			obj = func.view_class()
			return obj.dispatch_request(*args, **kwargs)

		func.view_class = cls
		func.__name__ = name
		func.__doc__ = cls.__doc__
		func.__module__ = cls.__module__
		func.methods = cls.methods

		return func

class Controller(object):
	"""docstring for Controller"""
	def __init__(self, name, url_map):
		self.url_map = url_map
		self.name = name

	def __name__(self):
		return self.name		