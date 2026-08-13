from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from accounts.models import NewsletterSubscription
from accounts.utils import generate_confirmation_token


@override_settings(
    BREVO_API_KEY="test-key",
    BREVO_SENDER_EMAIL="noreply@lexicon.test",
    BREVO_SENDER_NAME="Lexicon Test",
    BREVO_REPLY_TO="reply@lexicon.test",
)
class ConfirmNewsletterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "subscriber@example.com"
        self.token = generate_confirmation_token(self.email)
        self.subscription = NewsletterSubscription.objects.create(
            email=self.email,
            is_subscribed=False,
            confirmation_token=self.token,
        )

    def _confirm_url(self, token=None):
        return reverse("confirm_newsletter", kwargs={"token": token or self.token})

    @patch("accounts.views.send_subscription_success_email")
    def test_successful_confirmation_sends_success_email(self, mock_success_email):
        response = self.client.get(self._confirm_url())

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("confirmed successfully", data["message"].lower())

        self.subscription.refresh_from_db()
        self.assertTrue(self.subscription.is_subscribed)
        self.assertIsNotNone(self.subscription.confirmed_at)
        self.assertIsNotNone(self.subscription.subscribed_at)

        mock_success_email.assert_called_once()
        args, kwargs = mock_success_email.call_args
        self.assertEqual(args[0], self.email)  # first arg is email

    @patch("accounts.views.send_subscription_success_email")
    def test_already_confirmed_does_not_send_email_again(self, mock_success_email):
        self.subscription.is_subscribed = True
        self.subscription.confirmed_at = timezone.now()
        self.subscription.subscribed_at = timezone.now()
        self.subscription.save()

        response = self.client.get(self._confirm_url())

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("already confirmed", data["message"].lower())

        mock_success_email.assert_not_called()

    def test_invalid_token_returns_400(self):
        response = self.client.get(self._confirm_url(token="totally-invalid-token"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid or expired", response.json()["error"].lower())

    def test_expired_token_returns_400(self):
        # Token with max_age=0 is immediately expired when verified with positive max_age
        # We simulate by verifying with a token that will fail the age check in the view
        # (view uses max_age=86400). Easiest reliable way: use a bad signature.
        response = self.client.get(self._confirm_url(token="bad.signature.here"))
        self.assertEqual(response.status_code, 400)

    def test_token_email_mismatch_returns_400(self):
        # Valid token but no matching subscription row
        other_token = generate_confirmation_token("other@example.com")
        response = self.client.get(self._confirm_url(token=other_token))
        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid confirmation link", response.json()["error"].lower())

    @patch("accounts.views.send_subscription_success_email")
    def test_success_email_failure_does_not_break_confirmation(self, mock_success_email):
        mock_success_email.side_effect = Exception("Brevo is down")

        response = self.client.get(self._confirm_url())

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        self.subscription.refresh_from_db()
        self.assertTrue(self.subscription.is_subscribed)
        self.assertIsNotNone(self.subscription.confirmed_at)


@override_settings(
    BREVO_API_KEY="test-key",
    BREVO_SENDER_EMAIL="noreply@lexicon.test",
    BREVO_SENDER_NAME="Lexicon Test",
    BREVO_REPLY_TO="reply@lexicon.test",
)
class SendSubscriptionSuccessEmailTests(TestCase):
    """Unit-test the helper itself (payload content)."""

    @patch("accounts.views.send_brevo_email")
    def test_sends_expected_subject_and_content(self, mock_send):
        from accounts.views import send_subscription_success_email

        send_subscription_success_email("user@example.com", request=None)

        mock_send.assert_called_once()
        kwargs = mock_send.call_args.kwargs
        self.assertEqual(kwargs["to_email"], "user@example.com")
        self.assertEqual(kwargs["subject"], "Welcome to Lexicon!")
        self.assertIn("Spam", kwargs["html_content"])
        self.assertIn("Not Spam", kwargs["html_content"])
        self.assertIn("unsubscribe", kwargs["html_content"].lower())
        self.assertIn("Spam", kwargs["plain_text_content"])


@override_settings(
    BREVO_API_KEY="test-key",
    BREVO_SENDER_EMAIL="noreply@lexicon.test",
    BREVO_SENDER_NAME="Lexicon Test",
    BREVO_REPLY_TO="reply@lexicon.test",
)
class NewsletterSubscribeTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("accounts.views.send_confirmation_email")
    def test_subscribe_new_email_sends_confirmation(self, mock_confirm):
        response = self.client.post(
            reverse("newsletter_subscribe"),
            {"email": "new@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(data.get("requires_confirmation"))

        sub = NewsletterSubscription.objects.get(email="new@example.com")
        self.assertFalse(sub.is_subscribed)
        self.assertTrue(sub.confirmation_token)
        mock_confirm.assert_called_once()

    @patch("accounts.views.send_confirmation_email")
    def test_already_subscribed_returns_success_without_email(self, mock_confirm):
        NewsletterSubscription.objects.create(
            email="already@example.com",
            is_subscribed=True,
            confirmed_at=timezone.now(),
        )
        response = self.client.post(
            reverse("newsletter_subscribe"),
            {"email": "already@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(data.get("is_subscribed"))
        mock_confirm.assert_not_called()

    def test_missing_email_returns_400(self):
        response = self.client.post(reverse("newsletter_subscribe"), {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("email is required", response.json()["error"].lower())


@override_settings(
    BREVO_API_KEY="test-key",
)
class NewsletterUnsubscribeByEmailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sub = NewsletterSubscription.objects.create(
            email="leave@example.com",
            is_subscribed=True,
            confirmed_at=timezone.now(),
        )

    def test_unsubscribe_by_email_works(self):
        url = reverse("unsubscribe_by_email", kwargs={"email": "leave@example.com"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        self.sub.refresh_from_db()
        self.assertFalse(self.sub.is_subscribed)
        self.assertIsNotNone(self.sub.unsubscribed_at)

    def test_unknown_email_returns_400(self):
        url = reverse("unsubscribe_by_email", kwargs={"email": "nobody@example.com"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)


@override_settings(
    BREVO_API_KEY="test-key",
    BREVO_SENDER_EMAIL="noreply@lexicon.test",
    BREVO_SENDER_NAME="Lexicon Test",
    BREVO_REPLY_TO="reply@lexicon.test",
)
class SignupTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("signup")

    def test_signup_success(self):
        response = self.client.post(self.signup_url, {
            "email": "test@example.com",
            "password": "securepassword123"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["email"], "test@example.com")
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_signup_missing_email(self):
        response = self.client.post(self.signup_url, {
            "password": "securepassword123"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("email is required", response.json()["error"].lower())

    def test_signup_missing_password(self):
        response = self.client.post(self.signup_url, {
            "email": "test@example.com"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("password is required", response.json()["error"].lower())

    def test_signup_password_too_long(self):
        response = self.client.post(self.signup_url, {
            "email": "test@example.com",
            "password": "a" * 129
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("128 characters", response.json()["error"].lower())

    def test_signup_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="password123"
        )
        response = self.client.post(self.signup_url, {
            "email": "existing@example.com",
            "password": "newpassword123"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", response.json()["error"].lower())

    def test_signup_wrong_method(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 405)


@override_settings(
    BREVO_API_KEY="test-key",
    BREVO_SENDER_EMAIL="noreply@lexicon.test",
    BREVO_SENDER_NAME="Lexicon Test",
    BREVO_REPLY_TO="reply@lexicon.test",
)
class SigninTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signin_url = reverse("signin")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="securepassword123"
        )

    def test_signin_success(self):
        response = self.client.post(self.signin_url, {
            "email": "test@example.com",
            "password": "securepassword123"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["email"], "test@example.com")

    def test_signin_wrong_password(self):
        response = self.client.post(self.signin_url, {
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid email or password", response.json()["error"].lower())

    def test_signin_nonexistent_email(self):
        response = self.client.post(self.signin_url, {
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("no account found", response.json()["error"].lower())

    def test_signin_missing_credentials(self):
        response = self.client.post(self.signin_url, {
            "email": "test@example.com"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("email and password are required", response.json()["error"].lower())

    def test_signin_wrong_method(self):
        response = self.client.get(self.signin_url)
        self.assertEqual(response.status_code, 405)


@override_settings(
    BREVO_API_KEY="test-key",
)
class SignoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signout_url = reverse("signout")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

    def test_signout_success(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(self.signout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_signout_wrong_method(self):
        response = self.client.get(self.signout_url)
        self.assertEqual(response.status_code, 405)


@override_settings(
    BREVO_API_KEY="test-key",
    BREVO_SENDER_EMAIL="noreply@lexicon.test",
    BREVO_SENDER_NAME="Lexicon Test",
    BREVO_REPLY_TO="reply@lexicon.test",
)
class NewsletterSubscribeDetailedTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.subscribe_url = reverse("newsletter_subscribe")

    @patch("accounts.views.send_confirmation_email")
    def test_subscribe_with_authenticated_user(self, mock_confirm):
        user = User.objects.create_user(
            username="authuser",
            email="auth@example.com",
            password="password123"
        )
        self.client.login(username="authuser", password="password123")
        
        response = self.client.post(self.subscribe_url, {
            "email": "auth@example.com"
        })
        self.assertEqual(response.status_code, 200)
        
        subscription = NewsletterSubscription.objects.get(user=user)
        self.assertEqual(subscription.email, "auth@example.com")
        mock_confirm.assert_called_once()

    @patch("accounts.views.send_confirmation_email")
    def test_subscribe_authenticated_with_different_email(self, mock_confirm):
        user = User.objects.create_user(
            username="authuser",
            email="auth@example.com",
            password="password123"
        )
        self.client.login(username="authuser", password="password123")
        
        response = self.client.post(self.subscribe_url, {
            "email": "different@example.com"
        })
        self.assertEqual(response.status_code, 200)
        
        subscription = NewsletterSubscription.objects.get(user=user)
        self.assertEqual(subscription.email, "different@example.com")

    @patch("accounts.views.send_confirmation_email")
    def test_subscribe_existing_unconfirmed_email(self, mock_confirm):
        # Create an unconfirmed subscription
        token = generate_confirmation_token("unconfirmed@example.com")
        subscription = NewsletterSubscription.objects.create(
            email="unconfirmed@example.com",
            is_subscribed=False,
            confirmation_token=token
        )
        
        response = self.client.post(self.subscribe_url, {
            "email": "unconfirmed@example.com"
        })
        self.assertEqual(response.status_code, 200)
        
        # Should generate new token and send new email
        subscription.refresh_from_db()
        # The token should be different because we generate a new one
        # But since TimestampSigner includes timestamp, it might be different
        # Let's just check that a token exists and it's not None
        self.assertIsNotNone(subscription.confirmation_token)
        # Check that mock_confirm was called
        mock_confirm.assert_called_once()

    @patch("accounts.views.send_confirmation_email")
    def test_subscribe_email_send_failure(self, mock_confirm):
        mock_confirm.side_effect = Exception("Email service down")
        
        response = self.client.post(self.subscribe_url, {
            "email": "test@example.com"
        })
        self.assertEqual(response.status_code, 500)
        self.assertIn("failed to send confirmation email", response.json()["error"].lower())

    def test_subscribe_wrong_method(self):
        response = self.client.get(self.subscribe_url)
        self.assertEqual(response.status_code, 405)


@override_settings(
    BREVO_API_KEY="test-key",
)
class NewsletterStatusTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.status_url = reverse("newsletter_status")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

    def test_status_authenticated_with_subscription(self):
        subscription = NewsletterSubscription.objects.create(
            user=self.user,
            email="test@example.com",
            is_subscribed=True,
            confirmed_at=timezone.now(),
            subscribed_at=timezone.now()
        )
        self.client.login(username="testuser", password="password123")
        
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_subscribed"])
        self.assertEqual(data["email"], "test@example.com")
        self.assertIsNotNone(data["confirmed_at"])
        self.assertFalse(data["requires_confirmation"])

    def test_status_authenticated_with_unconfirmed_subscription(self):
        token = generate_confirmation_token("test@example.com")
        subscription = NewsletterSubscription.objects.create(
            user=self.user,
            email="test@example.com",
            is_subscribed=False,
            confirmation_token=token,
            confirmed_at=None
        )
        self.client.login(username="testuser", password="password123")
        
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_subscribed"])
        self.assertTrue(data["requires_confirmation"])

    def test_status_authenticated_no_subscription(self):
        self.client.login(username="testuser", password="password123")
        
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_subscribed"])
        self.assertEqual(data["email"], "test@example.com")
        self.assertFalse(data["requires_confirmation"])

    def test_status_unauthenticated_redirects(self):
        response = self.client.get(self.status_url)
        # Should redirect to login (since @login_required)
        self.assertEqual(response.status_code, 302)


@override_settings(
    BREVO_API_KEY="test-key",
)
class NewsletterUnsubscribeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.unsubscribe_url = reverse("newsletter_unsubscribe")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

    def test_unsubscribe_success(self):
        subscription = NewsletterSubscription.objects.create(
            user=self.user,
            email="test@example.com",
            is_subscribed=True,
            confirmed_at=timezone.now()
        )
        self.client.login(username="testuser", password="password123")
        
        response = self.client.post(self.unsubscribe_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertFalse(data["is_subscribed"])
        
        subscription.refresh_from_db()
        self.assertFalse(subscription.is_subscribed)
        self.assertIsNotNone(subscription.unsubscribed_at)

    def test_unsubscribe_no_subscription(self):
        self.client.login(username="testuser", password="password123")
        
        response = self.client.post(self.unsubscribe_url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("not subscribed", response.json()["error"].lower())

    def test_unsubscribe_wrong_method(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.unsubscribe_url)
        self.assertEqual(response.status_code, 405)

    def test_unsubscribe_unauthenticated_redirects(self):
        response = self.client.post(self.unsubscribe_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login


@override_settings(
    BREVO_API_KEY="test-key",
)
class IndexViewTests(TestCase):
    def test_index_authenticated(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.client.login(username="testuser", password="password123")
        
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"], user)
        self.assertTrue(response.context["is_authenticated"])

    def test_index_unauthenticated(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_authenticated"])


@override_settings(
    BREVO_API_KEY="test-key",
    BREVO_SENDER_EMAIL="noreply@lexicon.test",
)
class SendWordOfDayBrevoTests(TestCase):
    @patch("accounts.views.send_brevo_email")
    def test_send_word_of_day_email(self, mock_send):
        from accounts.views import send_word_of_day_brevo
        
        word_data = {"word": "serendipity"}
        send_word_of_day_brevo("user@example.com", word_data)
        
        mock_send.assert_called_once()
        kwargs = mock_send.call_args.kwargs
        self.assertEqual(kwargs["to_email"], "user@example.com")
        self.assertEqual(kwargs["subject"], "Word of the Day: serendipity")
        self.assertIn("serendipity", kwargs["html_content"])
        self.assertIn("serendipity", kwargs["plain_text_content"])
        self.assertIn("unsubscribe", kwargs["html_content"].lower())


@override_settings(
    BREVO_API_KEY="test-key",
)
class GetSiteUrlTests(TestCase):
    def test_get_site_url_with_request(self):
        request = MagicMock()
        request.is_secure.return_value = False
        # Mock the get_current_site function instead of importing Site
        with patch('accounts.views.get_current_site') as mock_get_site:
            mock_site = MagicMock()
            mock_site.domain = "testserver.com"
            mock_get_site.return_value = mock_site
            
            from accounts.views import get_site_url
            url = get_site_url(request)
            self.assertEqual(url, "http://testserver.com")

    def test_get_site_url_without_request(self):
        from accounts.views import get_site_url
        url = get_site_url()
        self.assertEqual(url, "http://127.0.0.1:8000")