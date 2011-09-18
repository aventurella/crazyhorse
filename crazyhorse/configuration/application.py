from __future__ import absolute_import
import glob
import os
import crazyhorse
import json
from crazyhorse.utils.tools import import_class
from crazyhorse.utils.tools import import_module
from crazyhorse.web.controller import CrazyHorseController
from crazyhorse.configuration.sections import ConfigurationSection
from crazyhorse.web import routing
from crazyhorse.web import exceptions

class ApplicationSection(ConfigurationSection):

    def initialize_system(self, section):
        self.initialize_default_view(section)
        self.initialize_controllers(section)

    def initialize_custom_errors(self, custom_errors):
        router = routing.application_router

        for error in custom_errors:
            controller = error["controller"]
            action     = error["action"]
            code       = str(error["code"])
            method     = error["method"]
            route      = None

            try:
                route  = router.routes_available[code]
            except:
                route = routing.Route()
                router.routes_available[code] = route

            if method == "*":
                route.register_action_for_method("*", controller, action)
            else:
                method_list = method.split(",")
                for target_method in method_list:
                    route.register_action_for_method(target_method, controller, action)

    def initialize_controllers(self, section):
        controllers = None
        try:
            controllers = section["controllers"]
        except KeyError:
            crazyhorse.get_logger().fatal("No controller array defined in config")
            raise exceptions.ConfigurationErrorException("No controllers array defined in application config")


        for controller in controllers:
            controllers_path = controller.replace(".", "/")

            #process controllers for any routes
            for file_path in glob.iglob("{0}/*.py".format(controllers_path)):
                if os.path.basename(file_path).startswith("__"): continue

                file_path     = os.path.splitext(file_path)[0]
                module_path   = file_path.replace("/", ".")
                crazyhorse.get_logger().debug("Processing routes within controller {0}".format(module_path))
                module = import_module(module_path)

        self.process_orphaned_routes()
        self.generate_route_json()

    def generate_route_json(self):
        router = routing.application_router
        output = {}
        
        for key in router.routes_available:
            route   = router.routes_available[key]
            meta    = {"name":key}
            actions = {}
            
            for method in route.actions:
                target = route.actions[method]
                actions[method] = "::".join(target)
            
            meta["constraints"] = None;
            
            if route.constraints != None:
                meta["constraints"] = {}
                for constraint in route.constraints:
                    meta["constraints"][constraint] = route.constraints[constraint]

            output[route.path] = {"actions":actions, "meta":meta}
        
        with open("routes.json", "wb") as target:
            target.write(json.dumps(output, sort_keys=True, indent=4))


    def process_orphaned_routes(self):
        router = routing.application_router
        if len(routing.temp_routes) > 0:
            for route_name in routing.temp_routes:
                try:
                    route = router.route_with_name(route_name)
                    for method in routing.temp_routes[route_name]:
                        controller, action  = routing.temp_routes[route_name][method]
                        route.register_action_for_method(method, controller, action)
                except:
                    temp_route = routing.temp_routes[route_name]
                    for key in temp_route.iterkeys():
                        crazyhorse.get_logger().warning("Failed to register route for with name: {0} for {1}::{2}".format(route_name, temp_route[key][0], temp_route[key][1]))

        del routing.temp_routes

    #views should contain their content-type definition for the response
    def initialize_default_view(self, section):

        view_path = None
        try:
            view_path        = section["default_view"]
        except KeyError:
            crazyhorse.get_logger().warning("No default_view specified in config. Calling MyController.view() will throw error")
            return

        crazyhorse.get_logger().debug("Registering default view: {0}".format(view_path))

        cls = import_class(view_path)

        if cls:
            CrazyHorseController.view_class = cls
            return

        crazyhorse.get_logger().fatal("Failed to import specified default view: {0}. Calling MyController.view() will throw error".format(view_path))
        raise exceptions.ConfigurationErrorException("Failed to import specified default view")


    def __call__(self, section):
        crazyhorse.get_logger().debug("Processing Application Configuration")
        settings = None

        try:
            self.initialize_system(section["system"])
        except KeyError:
            crazyhorse.get_logger().fatal("No system section defined in application config")
            raise exceptions.ConfigurationErrorException("No system section defined in application config")

        if "custom_errors" in section:
            self.initialize_custom_errors(section["custom_errors"])

        if "settings" in section:
            settings = section["settings"]

        return settings