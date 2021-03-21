from abc import ABC

import json
import redis
import tornado.ioloop
import tornado.web


class FactorialService(object):

    def __init__(self, cache):
        self.cache = cache
        self.key = "factorials"

    def calc(self, n):
        s = self.cache.hget(self.key, str(n))  # 用hash结构保存计算结果
        if s:
            return int(s), True
        s = 1
        for i in range(1, n):
            s *= i
        self.cache.hset(self.key, str(n), str(s))  # 保存结果
        return s, False


class FactorialHandler(tornado.web.RequestHandler, ABC):

    def initialize(self, factorial):
        self.factorial = factorial

    def get(self):
        n = int(self.get_argument("n") or 1)  # 参数默认值
        fact, cached = self.factorial.calc(n)
        result = {
            "n": n,
            "fact": fact,
            "cached": cached
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

