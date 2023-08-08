import time
from django.utils.deprecation import MiddlewareMixin

class APIMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            response.data["processing_time"]  = time.time() - request._start_time
            response._is_rendered = False 
            response.render()
            return response

        return response

