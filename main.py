# -*- coding:utf-8 -*-
import tornado.web
import tornado.ioloop
from tornado.options import options, define
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
    ]
    app = tornado.web.Application(
        handlers,
        **settings
    )
    # 绑定一个监听端口
    app.listen(8088)
    # 启动web程序，开始监听端口的连接
    tornado.ioloop.IOLoop.current().start()
