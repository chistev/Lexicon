import requests
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core.signing import TimestampSigner
from accounts.utils import (
    generate_confirmation_token,
    verify_confirmation_token,
    send_brevo_email,
)


class GenerateConfirmationTokenTests(TestCase):
    def test_returns_string(self):
        token = generate_confirmation_token("user@example.com")
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_different_emails_produce_different_tokens(self):
        t1 = generate_confirmation_token("a@example.com")
        t2 = generate_confirmation_token("b@example.com")
        self.assertNotEqual(t1, t2)

    def test_same_email_produces_verifiable_token(self):
        email = "same@example.com"
        token = generate_confirmation_token(email)
        # The token should unsign back to the original email
        recovered = TimestampSigner().unsign(token)
        self.assertEqual(recovered, email)


class VerifyConfirmationTokenTests(TestCase):
    def test_valid_token_returns_email(self):
        email = "valid@example.com"
        token = generate_confirmation_token(email)
        result = verify_confirmation_token(token, max_age=3600)
        self.assertEqual(result, email)

    def test_invalid_token_returns_none(self):
        result = verify_confirmation_token("this-is-not-a-valid-token")
        self.assertIsNone(result)

    def test_empty_token_returns_none(self):
        result = verify_confirmation_token("")
        self.assertIsNone(result)

    def test_expired_token_returns_none(self):
        email = "expired@example.com"
        token = generate_confirmation_token(email)
        # max_age=0 forces immediate expiry
        result = verify_confirmation_token(token, max_age=0)
        self.assertIsNone(result)

    def test_tampered_token_returns_none(self):
        token = generate_confirmation_token("good@example.com")
        # Flip one character
        bad_token = token[:-1] + ("x" if token[-1] != "x" else "y")
        result = verify_confirmation_token(bad_token)
        self.assertIsNone(result)


@override_settings(
    BREVO_API_KEY="test-api-key-123",
    BREVO_SENDER_EMAIL="noreply@lexicon.test",
    BREVO_SENDER_NAME="Lexicon Test",
    BREVO_REPLY_TO="reply@lexicon.test",
)
class SendBrevoEmailTests(TestCase):
    @patch("accounts.utils.requests.post")
    def test_successful_send(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"messageId": "abc-123"}
        mock_post.return_value = mock_response

        result = send_brevo_email(
            to_email="user@example.com",
            subject="Test Subject",
            html_content="<p>Hello</p>",
            plain_text_content="Hello",
        )

        self.assertEqual(result, {"messageId": "abc-123"})
        mock_post.assert_called_once()

        # Inspect the call
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.brevo.com/v3/smtp/email")
        self.assertIn("data", kwargs)

        import json
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["to"][0]["email"], "user@example.com")
        self.assertEqual(payload["subject"], "Test Subject")
        self.assertEqual(payload["htmlContent"], "<p>Hello</p>")
        self.assertEqual(payload["textContent"], "Hello")
        self.assertEqual(payload["sender"]["email"], "noreply@lexicon.test")
        self.assertEqual(payload["sender"]["name"], "Lexicon Test")
        self.assertEqual(payload["replyTo"]["email"], "reply@lexicon.test")

        headers = kwargs["headers"]
        self.assertEqual(headers["api-key"], "test-api-key-123")
        self.assertEqual(headers["Content-Type"], "application/json")

    @patch("accounts.utils.requests.post")
    def test_send_without_plain_text(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"messageId": "xyz"}
        mock_post.return_value = mock_response

        send_brevo_email(
            to_email="user@example.com",
            subject="No plain",
            html_content="<p>Hi</p>",
        )

        import json
        payload = json.loads(mock_post.call_args.kwargs["data"])
        self.assertNotIn("textContent", payload)

    def test_missing_api_key_raises(self):
        with override_settings(BREVO_API_KEY=None):
            with self.assertRaises(ValueError) as cm:
                send_brevo_email(
                    to_email="user@example.com",
                    subject="Fail",
                    html_content="<p>x</p>",
                )
            self.assertIn("BREVO_API_KEY", str(cm.exception))

    @patch("accounts.utils.requests.post")
    def test_api_error_raises(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")
        mock_post.return_value = mock_response

        with self.assertRaises(requests.exceptions.HTTPError):
            send_brevo_email(
                to_email="user@example.com",
                subject="Error",
                html_content="<p>x</p>",
            )