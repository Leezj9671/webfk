from sylfk import SYLFk
from sylfk.view import Controller
from core.base_view import BaseView

class Index(BaseView):
	def get(self, request):
		return 'get request HALO'

class Test(Index):
	def post(self, request):
		return 'post requet'

app = SYLFk()
url_map = [
	{
		'url': '/shiyanlou',
		'view': Index,
		'endpoint': 'index'
	},
	{
		'url': '/test',
		'view': Test,
		'endpoint': 'test'
	}

]

index_controller = Controller('index', url_map)
app.load_controller(index_controller)
# @app.route('/index', methods=['GET'])
# def index():
#     return '这是一个路由测试页面'


# @app.route('/test/js')
# def test_js():
#    return '<script src="/static/test.js"></script>'

app.run()