class ConfigurationErrorException(Exception):

    def __init__(self, value):
        self.message = "Invalid crazyhourse.config: {0}".format(value)


class DuplicateRouteNameException(Exception):

    def __init__(self, route_name):
        self.message = "Route name already exists: {0}".format(route_name)

class InvalidRouteNameException(Exception):

    def __init__(self, route_name):
        self.message = "Invalid route unable to locate existing route with name: {0}".format(route_name)

class InvalidRoutePathException(Exception):

    def __init__(self, path):
        self.message = "Invalid route unable to locate existing route for path: {0}".format(path)

class RouteExecutionException(Exception):

    def __init__(self, path, message):
        self.message  = "Executing route for {0} failed: {1}".format(path, message)

