import requests
from django.conf import settings
from django.http import JsonResponse
from .models import User
import json
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.middleware.csrf import get_token
from .serializers import UserSerializer

@ensure_csrf_cookie
def set_csrf_cookie(request):
    csrf_token = get_token(request)
    response = JsonResponse({"message": "CSRF cookie set", "X-CSRFToken": csrf_token})
    return response

# Google Authentication@csrf_exempt
def google_auth_view(request):
    token = "token"
    if request.content_type == 'application/json':
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        body = request.POST
        if not body:
            return JsonResponse({'error': 'No data provided'}, status=400)

    token = body.get('token')
    google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
    
    # Verify the token with Google
    response = requests.get(google_verify_url)
    if response.status_code == 200:
        user_data = response.json()
        email = user_data.get('email')
        name = user_data.get('name')
        
        # Save or retrieve user in the database
        user = User.objects(email=email).first()
        if not user:
            user = User(
                username=name,
                email=email,
                social_auth={'provider': 'google', 'id': user_data.get('sub')},
                avatar=user_data.get('picture'),
                is_admin=False,
            )
            user.save()
        
        # Serialize the user object using UserSerializer
        user_serialized = UserSerializer.serialize_one(user)
        
        return JsonResponse({'message': 'Google login successful', 'user': user_serialized}, status=200)
    else:
        return JsonResponse({'error': 'Invalid Google token'}, status=400)


# LinkedIn Authentication
def linkedin_auth_view(request):
    code = request.POST.get('code')
    redirect_uri = "http://localhost:8000/auth/linkedin/"  # Your redirect URI
    client_id = settings.SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY
    client_secret = settings.SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET
    
    # Step 1: Exchange authorization code for access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    token_response = requests.post(token_url, data=token_data)
    if token_response.status_code == 200:
        access_token = token_response.json().get('access_token')
        
        # Step 2: Use access token to fetch user information
        user_info_url = "https://api.linkedin.com/v2/me"
        email_info_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        user_info_response = requests.get(user_info_url, headers=headers)
        email_info_response = requests.get(email_info_url, headers=headers)
        
        if user_info_response.status_code == 200 and email_info_response.status_code == 200:
            user_info = user_info_response.json()
            email_info = email_info_response.json()
            
            name = user_info.get('localizedFirstName') + " " + user_info.get('localizedLastName')
            email = email_info['elements'][0]['handle~']['emailAddress']
            
            # Save or retrieve user in the database
            user = User.objects(email=email).first()
            if not user:
                user = User(
                    username=name,
                    email=email,
                    social_auth={'provider': 'linkedin', 'id': user_info.get('id')}
                )
                user.save()
            
            return JsonResponse({'message': 'LinkedIn login successful', 'email': email, 'name': name})
        else:
            return JsonResponse({'error': 'Failed to fetch LinkedIn user info'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid LinkedIn authorization code'}, status=400)

# Facebook Authentication
def facebook_auth_view(request):
    token = request.POST.get('token')
    facebook_verify_url = f"https://graph.facebook.com/me?fields=id,name,email&access_token={token}"
    
    # Verify the token with Facebook
    response = requests.get(facebook_verify_url)
    if response.status_code == 200:
        user_data = response.json()
        email = user_data.get('email')
        name = user_data.get('name')
        
        # Save or retrieve user in the database
        user = User.objects(email=email).first()
        if not user:
            user = User(
                username=name,
                email=email,
                social_auth={'provider': 'facebook', 'id': user_data.get('id')}
            )
            user.save()
        
        return JsonResponse({'message': 'Facebook login successful', 'email': email, 'name': name})
    else:
        return JsonResponse({'error': 'Invalid Facebook token'}, status=400)