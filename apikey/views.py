import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from backend.getrequest import getrequest
from auth_app.models import APIKey
from auth_app.serializers import APIKeySerializer
from django.http import JsonResponse


# Create your views here.
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_all(request):
    try:
        keys = APIKey.objects()
        key_list = []
        for key in keys:
            key_list.append({"name": key.name, "value": key.value})
        s_key_list = APIKeySerializer.serialize_all(key_list)
        return JsonResponse({"keys": s_key_list}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_one(name):
    try:
        key = APIKey.objects(name=name).first()
        return key.value
    except Exception as e:
        return None
    
@csrf_exempt
# @permission_classes([IsAuthenticated])
def set_key(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        name = body.get("name")
        value = body.get("value")

        if not name or not value:
            return JsonResponse({"error": "Missing 'name' or 'value'"}, status=400)

        key = APIKey.objects(name=name).first()
        if key:
            key.value = value
            key.save()
            return JsonResponse({"message": "API key updated successfully"}, status=200)
        else:
            key = APIKey(name=name, value=value)
            key.save()
            return JsonResponse({"message": "API key created successfully"}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)