import requests

requests.packages.urllib3.disable_warnings()


class Credentials:

    def __init__(self, user, password):
        self.user = user
        self.password = password

    def __str__(self):
        return f"{self.user}:{self.password}"


class Host:

    def __init__(self, host, port=80, protocol='http'):
        self.protocol = protocol
        self.port = port
        self.host = host
        self._credentials = None
        self._uri = None

    def credentials(self, user, password):
        self._credentials = Credentials(user, password)
        return self

    def uri(self, uri):
        self._uri = uri
        return self

    def __str__(self):
        if self._credentials:
            url = f"{self.protocol}://{self._credentials}@{self.host}:{self.port}/"
        else:
            url = f"{self.protocol}://{self.host}:{self.port}/"

        if self._uri:
            url += self._uri

        return url


class RequestData:
    def __init__(self, uri, method, body):
        self.uri = uri
        self.method = method
        self.body = body


class Dispatcher:

    def __init__(self, host: Host):
        self._host = host
        self.expected_status = 200

    def fetch(self, query):
        _, uri, method, body, self.expected_status = query
        _host = str(self._host.uri(uri))

        if method == "GET":
            response = requests.get(_host, verify=False)
        elif method == "POST":
            response = requests.post(_host, json=body, verify=False)
        elif method == "DELETE":
            response = requests.delete(_host, json=body, verify=False)
        elif method == "PUT":
            response = requests.put(_host, json=body, verify=False)
        else:
            raise ValueError("Unknown method {}".format(method))

        return response, self.expected_status
