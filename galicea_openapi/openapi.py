# -*- coding: utf-8 -*-


import functools
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi



def custom_openapi():
    if oapi.openapi_schema:
        return oapi.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        description="This is a very custom OpenAPI schema",
        routes=oapi.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    oapi.openapi_schema = openapi_schema
    return oapi.openapi_schema

oapi = FastAPI()
oapi.openapi = custom_openapi

def apiroute(route=None, **kw):

    routing = kw.copy()
    def apidecorator(f):
        if route:
            if isinstance(route, list):
                routes = route
            else:
                routes = [route]
            routing['routes'] = routes

        @functools.wraps(f)
        def response_wrap(*args, **kw):
            response = f(*args, **kw)
            return response

        oapi.add_api_route(routes[0], f, include_in_schema=True)
        response_wrap.routing = routing
        response_wrap.original_func = f
        return response_wrap

    return apidecorator


#