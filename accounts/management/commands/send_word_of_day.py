import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import NewsletterSubscription
from vocabulary.models import Word
from accounts.views import send_word_of_day_brevo
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send Word of the Day email to all newsletter subscribers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Send to test email only',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Send to specific email address (for testing)',
        )

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting Word of the Day email send...')
        
        # Get today's word of the day
        try:
            today = timezone.now().date()
            wotd = Word.objects.get(is_word_of_day=True, word_of_day_date=today)
        except Word.DoesNotExist:
            # If no word for today, get the first word and set it
            wotd = Word.objects.first()
            if wotd:
                wotd.is_word_of_day = True
                wotd.word_of_day_date = today
                wotd.save()
            else:
                self.stdout.write(self.style.ERROR('No words available in database!'))
                return
        
        # Prepare word data for email
        word_data = {
            'word': wotd.word,
            'phonetic': wotd.phonetic,
            'pos': wotd.pos,
            'definition': wotd.definition,
            'level': wotd.level,
            'examples': wotd.examples[:2] if wotd.examples else [],
            'synonyms': wotd.synonyms[:4] if wotd.synonyms else [],
            'antonyms': wotd.antonyms[:4] if wotd.antonyms else [],
        }
        
        # Get subscribers
        if kwargs.get('email'):
            # Send to specific email
            emails = [kwargs['email']]
        elif kwargs.get('test'):
            # Send to test email from settings
            test_email = os.environ.get('TEST_EMAIL', 'test@example.com')
            emails = [test_email]
        else:
            # Get all subscribed users from Django database
            subscriptions = NewsletterSubscription.objects.filter(
                is_subscribed=True,
                confirmed_at__isnull=False
            ).select_related('user')
            emails = [sub.email for sub in subscriptions]
        
        if not emails:
            self.stdout.write(self.style.WARNING('No subscribers found.'))
            return
        
        success_count = 0
        fail_count = 0
        
        for email in emails:
            try:
                self.stdout.write(f'Sending to {email}...')
                send_word_of_day_brevo(email, word_data)
                success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send to {email}: {str(e)}'))
                fail_count += 1
                logger.error(f'Failed to send WOTD to {email}: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(
            f'Word of the Day email send complete! '
            f'Success: {success_count}, Failed: {fail_count}'
        ))