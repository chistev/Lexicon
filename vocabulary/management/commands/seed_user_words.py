from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vocabulary.models import Word, UserWord

class Command(BaseCommand):
    help = 'Seed user words for testing'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='User email to seed words for')

    def handle(self, *args, **kwargs):
        email = kwargs.get('email')
        
        if not email:
            self.stdout.write(self.style.ERROR('Please provide --email'))
            return
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email {email} not found'))
            return
        
        # Get all words
        words = Word.objects.all()
        
        if not words.exists():
            self.stdout.write(self.style.ERROR('No words found in database. Run seed_words first.'))
            return
        
        # Seed some words for the user
        for i, word in enumerate(words[:5]):
            mastered = i < 3  # First 3 are mastered
            UserWord.objects.get_or_create(
                user=user,
                word=word,
                defaults={
                    'mastered': mastered,
                    'mastery_level': 4 if mastered else 1
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Seeded words for {user.email}'))