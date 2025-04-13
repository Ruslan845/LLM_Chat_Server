from django.http import JsonResponse
from auth_app.models import User
from auth_app.serializers import UserSerializer
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .permissions import IsAdminOrReadOnly

# Get one user by ID
@csrf_exempt
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def get_one_user(request, user_id):
    if request.method == 'GET':
        try:
            # Fetch the user by ID
            user = User.objects.get(id=user_id)
            # Serialize the user data
            user_data = UserSerializer.serialize_one(user)
            return JsonResponse(user_data, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

# Get all users
@csrf_exempt
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def get_all_users(request):
    if request.method == 'GET':
        # Fetch all users
        users = User.objects.all()
        # Serialize the list of users
        users_data = UserSerializer.serialize_many(users)

        return JsonResponse(users_data, safe=False, status=200)
    
@csrf_exempt
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def delete_user(request, user_id):
    if request.method == 'DELETE':
        try:
            # Fetch the user by ID
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

@csrf_exempt
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def update_user(request, user_id):
    if request.method == 'POST':  # Change to accept POST requests
        try:
            # Fetch the user by ID
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        try:
            # Parse the request body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Validate and update the user
        updated_user, errors = UserSerializer.validate_and_update(user, data)
        if errors:
            return JsonResponse({'error': 'Validation failed', 'details': errors}, status=400)

        # Serialize the updated user data
        updated_user_data = UserSerializer.serialize_one(updated_user)

        # Return the updated user data
        return JsonResponse({'message': 'User updated successfully', 'user': updated_user_data}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)