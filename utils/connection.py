import requests
import json
from b3_exceptions import BitshareStatusCodeError


class JsonRpc(object):
    def __init__(self, uri):
        self.id = 0
        self.uri = uri

    def send_request(self, method, *arguments, **kwargs):
        expected_code = kwargs.get('expected_code', 200)

        push_json = {
            "jsonrpc": "2.0",
            "method": method,
            "params": list(*arguments),
            "id": self.id
        }

        response = requests.post(self.uri, json=push_json)

        result = json.loads(response.content)
        status_code = response.status_code
        response.close()

        assert result["id"] == -1 or result["id"] == self.id

        del result["id"]

        self.id += 1

        if expected_code is None:
            pass
        elif status_code != expected_code:
            raise BitshareStatusCodeError(result)

        return result
