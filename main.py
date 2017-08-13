from sylfk import SYLFk, simple_template, redirect, render_json
from sylfk.view import Controller
from sylfk.session import session

from core.base_view import BaseView, SessionView
from core.database import dbconn

class API(BaseView):
	def get(self, request):
		data = {
			'name': 'testname',
			'company': 'testcompany',
			'department': 'testdepartment'
		}

		return render_json(data)

class Index(SessionView):
	def get(self, request):
		user = session.get(request, 'user')
		return simple_template("index.html", user=user, message="yomantemplate")

class Login(BaseView):
	"""docstring for Login"""
	def get(self, request):
		state = request.args.get('state', "1")

		return simple_template("layout.html", title='Login', message="Input your username" if state=="1" else "Error Username")

	def post(self, request):
		ret = dbconn.execute('''SELECT * FROM user WHERE f_name=%(user)s''', request.form)

		if ret.rows == 1:
			user = request.form['user']
			session.push(request, 'user', user)
			return redirect('/')

		return redirect("/login?state=0")

class Logout(SessionView):

	def get(self, request):
		session.pop(request, 'user')
		return redirect('/')

class Register(BaseView):
	"""docstring for Register"""
	def get(self, request):
		return simple_template("layout.html", title="Register", message="Input your username")

	def post(self, request):
		ret = dbconn.insert('INSERT INTO user(f_name) VALUES(%(user)s)', request.form)

		if ret.suc:
			return redirect("/login")
		else:
			return render_json(ret.to_dict())


class Download(BaseView):
	def get(self, request):
		return render_file("main.py")

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
	},
	{
		'url': '/api',
		'view': API,
		'endpoint': 'api'
	},
	{
		'url': '/register',
		'view': Register,
		'endpoint': 'register'
	},
	{
		'url': '/download',
		'view': Download,
		'endpoint': 'download'
	},
]

index_controller = Controller('index', url_map)
app.load_controller(index_controller)

app.run()