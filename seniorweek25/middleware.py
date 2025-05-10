from django.http import HttpResponsePermanentRedirect

class ForceHTTPSMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def process_request(self, request):
        # On Django<1.10 you use process_request, not __call__
        if not request.is_secure():
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace('http://', 'https://', 1)
            return HttpResponsePermanentRedirect(secure_url)
        # Returning None allows the request to continue
        return None