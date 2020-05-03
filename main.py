# -*- coding:utf-8 -*-
import tornado.web
import tornado.ioloop
from tornado.options import options, define
import os
import pymysql
import json

mysqldb = pymysql.Connection(host='127.0.0.1', database='MyBlog', user='root', password='D980612ssj$', charset='utf8')

import datetime


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


class GetALlBlog(tornado.web.RequestHandler):

    def initialize(self, db):
        self.db = db
        print("db is ok")

    def get(self):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(
                "select * from blog_articles where status = '有效' limit 10"
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
        print("success")
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
    ]
    app = tornado.web.Application(
        handlers,
        **settings
    )
    # 绑定一个监听端口
    app.listen(8088)
    # 启动web程序，开始监听端口的连接
    tornado.ioloop.IOLoop.current().start()
