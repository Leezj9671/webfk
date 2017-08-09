from sylfk import SYLFk, simple_template
from sylfk.view import Controller
from sylfk.session import session

from core.base_view import BaseView, SessionView

class Index(SessionView):
	def get(self, request):
		user = session.get(request, 'user')
		return simple_template("index.html", user=user, message="yomantemplate")

class Login(BaseView):
	"""docstring for Login"""
	def get(self, request):
		return simple_template("login.html")

	def post(self, request):
		user = request.form['user']
		session.push(request, 'user', user)
		return redirect('/')

class Logout(SessionView):

	def get(self, request):
		session.pop(request, 'user')
		return redirect('/')
		
app = SYLFk()
url_map = [
	{
		'url': '/',
		'view': Index,
		'endpoint': 'index'
	},
	{
		'url': '/login',
		'view': Login,
		'endpoint': 'test'
	},
	{
		'url': '/logout',
		'view': Logout,
		'endpoint': 'logout'
	}
]

index_controller = Controller('index', url_map)
app.load_controller(index_controller)

app.run()