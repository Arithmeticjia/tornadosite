# -*- coding:utf-8 -*-
import tornado.web
import tornado.ioloop
from tornado.options import options, define
from tornado.web import Application, RequestHandler, url
from tornado_basic_auth import basic_auth
import base64
import os
import pymysql
import datetime
import json

mysqldb = pymysql.Connection(host='127.0.0.1', database='MyBlog', user='root', password='D980612ssj$', charset='utf8')


class BasicAuthHandler(tornado.web.RequestHandler):

    def initialize(self, db):
        self.db = db

    def create_auth_header(self):
        self.set_status(401)
        self.set_header('WWW-Authenticate', 'Basic realm=Restricted')
        self._transforms = []
        self.finish()

    def get(self):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        # Authorization: Basic base64("user:passwd")
        auth_header = self.request.headers.get('Authorization', None)
        if auth_header is not None:
            # Basic Zm9vOmJhcg==
            auth_mode, auth_base64 = auth_header.split(' ', 1)
            assert auth_mode == 'Basic'
            # Zm9vOmJhcg解码
            auth_info = base64.b64decode(auth_base64)
            # byte转str
            auth_username, auth_password = auth_info.decode('utf-8').split(":")
            try:
                name = auth_username
                cursor.execute(
                    "SELECT * FROM blog_bloguser WHERE name='{}'".format(name)
                )
                # [{},{},...,{}]字典形式
                result = cursor.fetchone()
                if result is not None:
                    password = result['password']
                    if auth_password == password:
                        self.create_auth_header()
                    else:
                        self.create_auth_header()
                else:
                    self.create_auth_header()
            except Exception as e:
                return self.write(e)
        else:
            self.create_auth_header()


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')

        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")

        else:
            return json.JSONEncoder.default(self, obj)


# 定义处理类型
class IndexHandler(tornado.web.RequestHandler):
    # 添加一个处理get请求方式的方法
    def get(self):
        # 向响应中，添加数据
        self.write('你都如何回忆我，带着笑或是很沉默')


class HelloTornado(tornado.web.RequestHandler):

    def get(self):
        self.render("HelloTornado.html")


def basic_auth_valid(user, pwd):
    cursor = mysqldb.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute(
            "SELECT * FROM blog_bloguser WHERE name='{}'".format(user)
        )
        # [{},{},...,{}]字典形式
        result = cursor.fetchone()
        if result is not None:
            password = result['password']
            if pwd == password:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        return False


@basic_auth(basic_auth_valid)
class GetALlBlog(tornado.web.RequestHandler):

    def initialize(self, db):
        self.db = db
        print("db is ok")

    def get(self):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(
                "SELECT A.id, A.title, A.`timestamp`, A.views, A.greats, A.comments,U.name as 'authorname' FROM blog_articles A, blog_bloguser U WHERE A.authorname_id = U.id AND A.STATUS = '有效'LIMIT 10"
            )
            # [{},{},...,{}]字典形式
            result = cursor.fetchall()
            return_data = {}
            return_data["code"] = 200
            return_data["message"] = "success"
            return_data["data"] = result
            self.finish(json.dumps(return_data, cls=DateEncoder))
        except Exception as e:
            return self.write(e)
        db.commit()
        cursor.close()


@basic_auth(basic_auth_valid)
class GetBlogByCategory(tornado.web.RequestHandler):

    def initialize(self, db):
        self.db = db
        print("db is ok")

    def get(self, category):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(
                "SELECT A.id, A.title, A.`timestamp`, A.views, A.greats, A.comments,U.name as 'authorname' FROM blog_articles A, blog_bloguser U WHERE A.authorname_id = U.id AND A.STATUS = '有效'LIMIT 10"
            )
        except Exception as e:
            self.write(e)
        self.write(category)


# 响应用户/api/tornado请求
class TornadoHandler(RequestHandler):
    # 重写ＲｅｑｕｅｓｔＨａｎｄｌｅｒ中initialize方法
    # 获取动态设置的参数(greeting,info)
    def initialize(self, greeting, info):  # 动态参数要与url路由中设置的参数必须一样
        self.greeting = greeting
        self.info = info

    def get(self, *args, **kwargs):
        # ｗｒｉｔｅ方法只能接受一个字符串类型的参数，但可以通过字符串的拼接实现一个参数
        self.write(self.greeting + ',' + self.info)

    def post(self, *args, **kwargs):
        pass


class GetPython(RequestHandler):

    def get(self, age, name):
        self.write('name:%s age:%s' % (name, age))


# url:http://127.0.0.1:8088/api/getblogbyany/?category=Django&authorname=ArithmeticJia
class GetBlogByAny(RequestHandler):

    def get(self):
        category = self.get_query_argument('category')
        authorname = self.get_query_argument('authorname')
        print(category, authorname)


settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "statics"),
    debug=True,
)

if __name__ == '__main__':
    # 创建一个应用对象
    define("port", default=8088, type=int, help="run server on the given port.")
    handlers = [
        (r'/', IndexHandler),
        (r'/index', HelloTornado),
        (r'/api/getallblog', GetALlBlog, dict(db=mysqldb)),
        (r'/api/testbasicauth', BasicAuthHandler, dict(db=mysqldb)),
        # 适合页面请求
        (r'/api/getblogbycategory/(?P<category>.+)', GetBlogByCategory, dict(db=mysqldb)),
        (r'/api/python/(?P<name>.+)/(?P<age>[0-9]+)', GetPython),
        # 适合API请求
        (r'/api/getblogbyany/', GetBlogByAny),
        # 个人感觉这种场景很少用
        url('/api/tornado', TornadoHandler, {'greeting': '你好', 'info': 'Tornado'}, name='tornado_url'),
    ]
    app = tornado.web.Application(
        handlers,
        **settings
    )
    # 绑定一个监听端口
    app.listen(8088)
    # 启动web程序，开始监听端口的连接
    tornado.ioloop.IOLoop.current().start()
