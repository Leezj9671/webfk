import os
from werkzeug.serving import run_simple
from werkzeug.wrappers import Response
import json

import sylfk.exceptions as exceptions
from sylfk.wsgi_adapter import wsgi_app
from sylfk.helper import parse_static_key
from sylfk.route import Route
from sylfk.template_engine import replace_template
from sylfk.session import create_session_id, session

# 定义常见服务异常的响应体
ERROR_MAP = {
    '401': Response('<h1>401 Unknown or unsupported method</h1>', content_type='text/html; charset=UTF-8', status=401),
    '404': Response('<h1>404 Source Not Found<h1>', content_type='text/html; charset=UTF-8', status=404),
    '503': Response('<h1>503 Unknown function type</h1>', content_type='text/html; charset=UTF-8',  status=503)
}

# 定义文件类型
TYPE_MAP = {
    'css':  'text/css',
    'js': 'text/js',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg'
}

class ExecFunc:

    def __init__(self, func, func_type, **options):
        self.func = func
        self.options = options
        self.func_type = func_type

class SYLFk:

    template_folder = None

    # 实例化方法
    def __init__(self, static_folder='static', template_folder='template', session_path=".session"):
        self.host = '127.0.0.1'
        self.port = 8080
        self.url_map = {}
        self.static_map = {}
        self.function_map = {}
        self.static_folder = static_folder
        self.route = Route(self)
        self.template_folder = template_folder
        self.session_path = session_path
        SYLFk.template_folder = self.template_folder

    # 框架被 WSGI 调用入口的方法
    def __call__(self, environ, start_response):
        return wsgi_app(self, environ, start_response)

  # 启动入口
    def run(self, host=None, port=None, **options):

        for key, value in options.items():
            if value:
                self.__setattr__(key, value)

        if host:
            self.host = host

        if port:
            self.port = port

        # !!!self.add_static_rule(self.static_folder)
        # static sources
        self.function_map['static'] = ExecFunc(func=self.dispatch_static, func_type='static')

        if not os.path.exists(self.session_path):
            os.mkdir(self.session_path)

        session.set_storage_path(self.session_path)
        session.load_local_session()

        run_simple(hostname=self.host, port=self.port, application=self, **options)
        
    def add_url_rule(self, url, func, func_type, endpoint=None, **options):

        if endpoint is None:
            endpoint = func.__name__

        if url in self.url_map:
            raise exceptions.URLExistsError

        if endpoint in self.function_map and func_type != 'static':
            raise exceptions.EndpointExistsError

        self.url_map[url] = endpoint

        self.function_map[endpoint] = ExecFunc(func, func_type, **options)

    def dispatch_static(self, static_path):
        # 判断资源文件是否在静态资源规则中，如果不存在，返回 404 状态页
        if os.path.exists(static_path):
            # 获取资源文件后缀
            key = parse_static_key(static_path)

            # 获取文件类型
            doc_type = TYPE_MAP.get(key, 'text/plain')

            # 获取文件内容
            with open(static_path, 'rb') as f:
                rep = f.read()

            # 封装并返回响应体
            return Response(rep, content_type=doc_type)
        else:
            # 返回 404 页面为找到对应的响应体
            return ERROR_MAP['404']

    def dispatch_request(self, request):
        # 去掉 URL 中 域名部分，也就从 http://xxx.com/path/file?xx=xx 中提取 path/file 这部分
        url = "/" + "/".join(request.url.split("/")[3:]).split("?")[0]
        # 通过 URL 寻找节点名
        if url.find(self.static_folder) == 1 and url.index(self.static_folder) == 1:
            # 如果 URL 以静态资源文件夹名首目录，则资源为静态资源，节点定义为 static
            endpoint = self.static_folder
            url = url[1:]
        else:  
            # 若不以 static 为首，则从 URL 与 节点的映射表中获取节点
            endpoint = self.url_map.get(url, None)

        # 定义响应报头，Server 参数的值表示运行的服务名，通常有 IIS， Apache，Tomcat，Nginx等，这里自定义为 SYL Web 0.1
        cookies = request.cookies

        if 'session_id' not in cookies:
            headers = {
                'Set-Cookie': 'session_id=%s' % create_session_id(),
                'Server': 'AWEB Framework'
            }

        else:
            headers = {
                'Server': 'AWEB Framework'
            }

        # 如果节点为空 返回 404
        if endpoint is None:
            return ERROR_MAP['404']

        # 获取节点对应的执行函数
        exec_function = self.function_map[endpoint]

        # 判断执行函数类型
        if exec_function.func_type == 'route':
            """ 路由处理 """

            # 判断请求方法是否支持
            if request.method in exec_function.options.get('methods'):
                """ 路由处理结果 """

                # 判断路由的执行函数是否需要请求体进行内部处理
                argcount = exec_function.func.__code__.co_argcount

                if argcount > 0:
                    # 需要附带请求体进行结果处理
                    rep = exec_function.func(request)
                else:
                    # 不需要附带请求体进行结果处理
                    rep = exec_function.func()
            else:
                """ 未知请求方法 """

                # 返回 401 错误响应体
                return ERROR_MAP['401']
    
        elif exec_function.func_type == 'view':
            """ 视图处理结果 """

            # 所有视图处理函数都需要附带请求体来获取处理结果
            rep = exec_function.func(request)

        elif exec_function.func_type == 'static':
            """ 静态逻辑处理 """

            # 静态资源返回的是一个预先封装好的响应体，所以直接返回
            return exec_function.func(url)

        else:
            """ 未知类型处理 """
    
            # 返回 503 错误响应体
            return ERROR_MAP['503']

        # 定义 200 状态码表示成功
        status = 200
        # 定义响应体类型
        content_type = 'text/html'

        if isinstance(rep, Response):
            return rep

        # 返回响应体
        return Response(rep, content_type='%s; charset=UTF-8' % content_type, headers=headers, status=status)

    def bind_view(self, url, view_class, endpoint):
        self.add_url_rule(url, func=view_class.get_func(endpoint), func_type='view')

    # 控制器加载
    def load_controller(self, controller):
        name = controller.__name__()
        for rule in controller.url_map:
            # 绑定 URL 与 视图对象，最后的节点名格式为 `控制器名` + "." + 定义的节点名
            self.bind_view(rule['url'], rule['view'], name + '.' + rule['endpoint'])

def simple_template(path, **options):
    return replace_template(SYLFk, path, **options)

def redirect(url, status_code=302):
    response = Response('', status=status_code)
    response.headers['Location'] = url
    return response

def render_json(data):
    content_type = "text/plain"

    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)
        content_type = "application/json"

    return Response(data, content_type="%s; charset=UTF-8" % content_type, status=200)


# 返回让客户端保存文件到本地的响应体
def render_file(file_path, file_name=None):

    # 判断服务器是否有该文件，没有则返回 404 错误
    if os.path.exists(file_path):

        # 读取文件内容
        with open(file_path, "rb") as f:
            content = f.read()

        # 如果没有设置文件名，则以 “/” 分割路径取最后一项最为文件名
        if file_name is None:
            file_name = file_path.split("/")[-1]

        # 封装响应报头，指定为附件类型，并定义下载的文件名
        headers = {
            'Content-Disposition': 'attachment; filename="%s"' % file_name
        }

        # 返回响应体
        return Response(content, headers=headers, status=200)

    # 如果不存在该文件，返回 404 错误
    return ERROR_MAP['404']