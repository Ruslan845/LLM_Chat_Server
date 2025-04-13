import json
from django.http import JsonResponse

def getrequest(request):
    if request.content_type == 'application/json':
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        body = request.POST
        if not body:
            return JsonResponse({'error': 'No data provided'}, status=400)
    return body