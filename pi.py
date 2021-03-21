import json
import math
import redis
import tornado.ioloop
import tornado.web


class PiService(object):

    def __init__(self, cache):
        self.cache = cache
        self.key = "pis"

    def calc(self, n):
        s = self.cache.hget(self.key, str(n))
        if s:
            return float(s), True
        s = 0.0
        for i in range(n):
            s += 1.0 / (2 * i + 1) / (2 * i + 1)
        s = math.sqrt(s * 8)
        self.cache.hset(self.key, str(n), str(s))
        return s, False


class PiHandler(tornado.web.RequestHandler):

    def initialize(self, pi):
        self.pi = pi

    def get(self):
        n = int(self.get_argument("n") or 1)
        pi, cached = self.pi.calc(n)
        result = {
            "n": n,
            "pi": pi,
            "cached": cached
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))
