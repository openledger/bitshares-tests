from connection import JsonRpc


class WitnessNode(object):
    def __init__(self, uri):
        self.rpc = JsonRpc(uri)

    def send_request(self, method, *arguments, **kwargs):
        return self.rpc.send_request(method, *arguments, **kwargs)


host_port = 'localhost', 12010
uri = 'http://%s:%s/' % host_port
WITNESS_NODE = WitnessNode(uri)
