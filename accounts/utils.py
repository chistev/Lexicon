import json
import requests
from django.core.signing import TimestampSigner
from django.conf import settings

signer = TimestampSigner()

def generate_confirmation_token(email):
    """Generate a signed token for email confirmation using Django's TimestampSigner"""
    return signer.sign(email)

def verify_confirmation_token(token, max_age=3600):
    """Verify a confirmation token, returns email if valid, None otherwise"""
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except:
        return None

def send_brevo_email(to_email, subject, html_content, plain_text_content=None):
    """Send email using Brevo API"""
    api_key = getattr(settings, 'BREVO_API_KEY', None)
    if not api_key:
        raise ValueError("BREVO_API_KEY not found in settings")
    
    api_url = 'https://api.brevo.com/v3/smtp/email'
    
    # Use consistent sender settings
    sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', 'stephen@rxjourney.net')
    sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'Chistev')
    reply_to_email = getattr(settings, 'BREVO_REPLY_TO', 'chistev12@gmail.com')
    
    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "replyTo": {
            "email": reply_to_email
        },
        "to": [
            {
                "email": to_email
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
    }
    
    if plain_text_content:
        payload["textContent"] = plain_text_content
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'api-key': api_key
    }
    
    response = requests.post(api_url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    return response.json()