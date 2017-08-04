from sylfk.view import View

class BaseView(View):
	methods = ['GET', 'POST']
	def post(self, request, *args, **options):
		pass

	def post(self, request, *args, **options):
		pass

	def dispatch_request(self, request, *args, **options):
		methods_meta = {
			'GET': self.get,
			'POST': self.post
		}

		if request.method in methods_meta:
			return methods_meta[request.method](request, *args, **options)
		else:
			return '<h1>Unkown or unsupported require method</h1>'
			