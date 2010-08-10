"""
* /open -- This will open a channel and declare a queue.
* /get -- Will display the incoming messages.
* /publish?msg=abc -- Will publish 'abc'.

Everything's unblocking, so you can keep /get open while /publish-ing messages.
"""

import sys
from tornado import httpserver, ioloop, web
import pika

conn = pika.TornadoConnection(pika.ConnectionParameters(
    (len(sys.argv) > 1) and sys.argv[1] or '127.0.0.1',
    credentials=pika.PlainCredentials('guest', 'guest')))
qname = (len(sys.argv) > 2) and sys.argv[2] or 'test'
server_port = (len(sys.argv) > 3) and int(sys.argv[3]) or 8000
channel = None


class OpenHandler(web.RequestHandler):

    @web.asynchronous
    def get(self):
        global channel
        self.write('Opening channel... ')
        channel = conn.channel(self.queue_declare)

    def queue_declare(self):
        self.write('Done<br>Declaring queue... ')
        channel.queue_declare(
            queue='test', durable=False, exclusive=False, auto_delete=True,
            callback=self.queue_declared)

    def queue_declared(self):
        self.write('Done')
        self.finish()


class PublishHandler(web.RequestHandler):

    @web.asynchronous
    def get(self):
        msg = self.get_argument('msg').encode('utf-8')
        self.write('Publishing: %r... ' % msg)
        channel.basic_publish('', 'test', msg, callback=self.msg_published)

    def msg_published(self):
        self.write('Done')
        self.finish()


class GetHandler(web.RequestHandler):

    @web.asynchronous
    def get(self):
        self.write('Waiting...<br>')
        self.flush()
        channel.basic_consume(self.read_message, queue='test')

    def read_message(self, channel, method, header, body):
        self.write('Received: %r<br>' % body)
        self.flush()


app = web.Application((
    (r'^/open$', OpenHandler),
    (r'^/publish', PublishHandler),
    (r'^/get$', GetHandler),
))

if __name__ == '__main__':
    server = httpserver.HTTPServer(app)
    server.listen(server_port)
    ioloop.IOLoop.instance().start()
