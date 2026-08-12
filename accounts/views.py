from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.utils import timezone
from .models import NewsletterSubscription
from .utils import generate_confirmation_token, verify_confirmation_token, send_brevo_email

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

# Newsletter Views

def get_site_url(request=None):
    """Get the site URL dynamically"""
    if request:
        current_site = get_current_site(request)
        protocol = 'https' if request.is_secure() else 'http'
        return f"{protocol}://{current_site.domain}"
    return getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')

@csrf_exempt
def newsletter_subscribe(request):
    """Subscribe a user to the newsletter - no login required"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    email = request.POST.get('email', '').strip()
    
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)
    
    # Check if user is authenticated
    if request.user.is_authenticated:
        # Logged in user - link to their account
        subscription, created = NewsletterSubscription.objects.get_or_create(
            user=request.user,
            defaults={'email': email}
        )
        if subscription.email != email:
            subscription.email = email
    else:
        # Logged out user - create subscription without user association
        # First check if there's already a subscription with this email
        existing = NewsletterSubscription.objects.filter(email=email).first()
        if existing:
            # If user is not authenticated but email exists, we can still use it
            subscription = existing
            # If this subscription is already confirmed, return success
            if subscription.is_subscribed and subscription.confirmed_at:
                return JsonResponse({
                    'success': True,
                    'message': 'This email is already subscribed!',
                    'is_subscribed': True
                })
        else:
            # Create a new subscription with no user
            subscription = NewsletterSubscription.objects.create(
                email=email,
                is_subscribed=False
            )
    
    # If already subscribed, return success
    if subscription.is_subscribed and subscription.confirmed_at:
        return JsonResponse({
            'success': True,
            'message': 'You are already subscribed!',
            'is_subscribed': True
        })
    
    # Generate confirmation token
    token = generate_confirmation_token(email)
    subscription.confirmation_token = token
    subscription.save()
    
    # Send confirmation email via Brevo
    try:
        send_confirmation_email(email, token, request.user if request.user.is_authenticated else None, request)
        return JsonResponse({
            'success': True,
            'message': 'Confirmation email sent! Please check your inbox.',
            'is_subscribed': False,
            'requires_confirmation': True
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to send confirmation email: {str(e)}'
        }, status=500)

@login_required
def newsletter_status(request):
    """Get the current newsletter subscription status for the user"""
    try:
        subscription = NewsletterSubscription.objects.get(user=request.user)
        return JsonResponse({
            'is_subscribed': subscription.is_subscribed and subscription.confirmed_at is not None,
            'email': subscription.email,
            'confirmed_at': subscription.confirmed_at,
            'subscribed_at': subscription.subscribed_at,
            'requires_confirmation': subscription.confirmation_token and not subscription.confirmed_at
        })
    except NewsletterSubscription.DoesNotExist:
        return JsonResponse({
            'is_subscribed': False,
            'email': request.user.email,
            'confirmed_at': None,
            'subscribed_at': None,
            'requires_confirmation': False
        })

def confirm_newsletter(request, token):
    """Confirm newsletter subscription via email link"""
    # Verify token (valid for 24 hours = 86400 seconds)
    email = verify_confirmation_token(token, max_age=86400)
    
    if not email:
        return JsonResponse({'error': 'Invalid or expired confirmation link'}, status=400)
    
    try:
        subscription = NewsletterSubscription.objects.get(email=email, confirmation_token=token)
        
        # Check if already confirmed
        if subscription.confirmed_at:
            return JsonResponse({
                'success': True,
                'message': 'Subscription already confirmed!'
            })
        
        subscription.is_subscribed = True
        subscription.confirmed_at = timezone.now()
        subscription.subscribed_at = timezone.now()
        subscription.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Newsletter subscription confirmed successfully!'
        })
    except NewsletterSubscription.DoesNotExist:
        return JsonResponse({'error': 'Invalid confirmation link'}, status=400)

@csrf_exempt
@login_required
def newsletter_unsubscribe(request):
    """Unsubscribe a user from the newsletter"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        subscription = NewsletterSubscription.objects.get(user=request.user)
        subscription.is_subscribed = False
        subscription.unsubscribed_at = timezone.now()
        subscription.save()
        
        return JsonResponse({
            'success': True,
            'message': 'You have been unsubscribed from the newsletter.',
            'is_subscribed': False
        })
    except NewsletterSubscription.DoesNotExist:
        return JsonResponse({
            'error': 'You are not subscribed to the newsletter.'
        }, status=400)

def newsletter_unsubscribe_by_email(request, email):
    """Unsubscribe a user from the newsletter via email link"""
    try:
        subscription = NewsletterSubscription.objects.get(email=email)
        subscription.is_subscribed = False
        subscription.unsubscribed_at = timezone.now()
        subscription.save()
        
        return JsonResponse({
            'success': True,
            'message': 'You have been unsubscribed from the newsletter.'
        })
    except NewsletterSubscription.DoesNotExist:
        return JsonResponse({
            'error': 'Email not found in our newsletter list.'
        }, status=400)

# Email Functions

def send_confirmation_email(email, token, user=None, request=None):
    """Send a confirmation email for newsletter subscription using Brevo"""
    site_url = get_site_url(request)
    confirm_url = f"{site_url}/newsletter/confirm/{token}/"
    
    user_name = "there"
    if user and user.is_authenticated:
        user_name = user.first_name or user.username
    
    html_message = f"""
    <html>
    <body>
        <h1>Lexicon Newsletter</h1>
        <p>Hi {user_name}!</p>
        <p>Thank you for subscribing to the Lexicon Word of the Day newsletter.</p>
        <p>You'll receive one advanced vocabulary word every morning to help you expand your vocabulary.</p>
        <p>
            <a href="{confirm_url}">Confirm Subscription</a>
        </p>
        <p>If you didn't request this, you can safely ignore this email.</p>
        
        <p>Lexicon · Vocabulary that sticks</p>
        <p><a href="{confirm_url}">Confirm Subscription</a></p>
    </body>
    </html>
    """
    
    plain_message = f"""
    Lexicon Newsletter
    
    Hi {user_name}!
    
    Thank you for subscribing to the Lexicon Word of the Day newsletter.
    You'll receive one advanced vocabulary word every morning.
    
    Confirm your subscription here: {confirm_url}
    
    If you didn't request this, you can safely ignore this email.
    
    IMPORTANT: To ensure you receive your daily word, please add noreply@lexicon.com to your address book and check your Spam/Junk folder. If you find our emails there, mark them as "Not Spam" so they go to your inbox.
    
    Lexicon · Vocabulary that sticks
    """
    
    send_brevo_email(
        to_email=email,
        subject='Confirm your Lexicon Newsletter Subscription',
        html_content=html_message,
        plain_text_content=plain_message
    )

def send_word_of_day_brevo(email, word_data):
    """Send the Word of the Day email via Brevo API"""
    site_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')
    unsubscribe_url = f"{site_url}/newsletter/unsubscribe/{email}/"
    learn_more_url = f"{site_url}/learn/?word={word_data['word']}"
    
    html_message = f"""
    <html>
    <body>
        <h1>📖 Word of the Day</h1>
        
        <p>Today's word is:</p>
        <h2>{word_data['word']}</h2>
        
        <p>
            <a href="{learn_more_url}">Click here to learn more about this word</a>
        </p>
        
        <hr>
        
        <p><strong>💡 Tip:</strong> To ensure you never miss a word, add <strong>noreply@lexicon.com</strong> to your address book and check your <strong>Spam/Junk</strong> folder daily. If you find our emails there, mark them as <strong>"Not Spam"</strong>.</p>
        
        <hr>
        
        <p>
            <a href="{unsubscribe_url}">Unsubscribe</a> · 
            You're receiving this because you subscribed to the Lexicon Word of the Day newsletter.
        </p>
    </body>
    </html>
    """
    
    plain_message = f"""
    Word of the Day: {word_data['word']}
    
    Learn more about this word at: {learn_more_url}
    
    Tip: To ensure you never miss a word, add noreply@lexicon.com to your address book and check your Spam/Junk folder daily. If you find our emails there, mark them as "Not Spam".
    
    Unsubscribe: {unsubscribe_url}
    """
    
    send_brevo_email(
        to_email=email,
        subject=f"Word of the Day: {word_data['word']}",
        html_content=html_message,
        plain_text_content=plain_message
    )
