class CrossOriginPolicyMiddleware:
    def __init__(self, get_repsonse):
        self.get_response = get_repsonse

    def __call__(self, request):
        response = self.get_response(request)
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Embedder-Policy'] = 'same-origin'
        return response
    