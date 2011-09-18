import wsgiref.headers
class Headers(object):
    """
        this class is basically a shell for wsgiref.headers.Headers
        Why? trying to keep the access consistent.
        For example to add a Cookie it's Cookies.add()
        So I wanted Headers.add() as well.  Using wsgiref though
        it would have been Headers.add_header. No bueno for me.
        values must compluy with PEP 333
    """
    def __init__(self, values=[]):

        self._headers = wsgiref.headers.Headers(values)

    def add(self, name, value, **_params):
        self._headers.add_header(name, value, **_params)

    def items(self):
        return self._headers.items()

    def __setitem__(self, key, value):
        self._headers[key] = value

    def __getitem__(self, key):
        return self._headers[key]

    def __delitem__(self, key):
        del self._headers[key]

    def __contains__(self, item):
        return item in self._headers