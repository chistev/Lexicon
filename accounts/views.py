from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

def index(request):
    """Main page view"""
    return render(request, 'index.html', {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
    })

@csrf_exempt
def signup(request):
    """Handle user registration with email and password"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()
    
    # Validation
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)
    
    if not password:
        return JsonResponse({'error': 'Password is required'}, status=400)
    
    if len(password) > 128:
        return JsonResponse({'error': 'Password must be 128 characters or less'}, status=400)
    
    # Check if user exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'A user with this email already exists'}, status=400)
    
    try:
        # Create username from email
        username = email.split('@')[0]
        # Make username unique if needed
        if User.objects.filter(username=username).exists():
            username = f"{username}_{User.objects.count() + 1}"
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Log the user in
        login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'email': user.email,
                'username': user.username,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=400)

@csrf_exempt
def signin(request):
    """Handle user login with email and password"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()
    
    if not email or not password:
        return JsonResponse({'error': 'Email and password are required'}, status=400)
    
    try:
        # Get user by email
        user = User.objects.get(email=email)
        # Authenticate with username
        user = authenticate(request, username=user.username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Signed in successfully',
                'user': {
                    'email': user.email,
                    'username': user.username,
                }
            })
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=400)
            
    except User.DoesNotExist:
        return JsonResponse({'error': 'No account found with this email'}, status=400)

@csrf_exempt
def signout(request):
    """Handle user logout"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Signed out successfully'
    })