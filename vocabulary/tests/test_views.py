import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from vocabulary.models import Word, UserWord


class GetWordOfDayTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('word_of_day')
        
        # Clear any existing WOTD entries
        Word.objects.all().delete()
        
        # Create test words
        self.word1 = Word.objects.create(
            word='test1',
            phonetic='/test1/',
            pos='noun',
            definition='Test word 1',
            level='B2',
            category='Test',
            examples=['Example 1'],
            collocations=['collocation 1'],
            synonyms=['synonym 1'],
            antonyms=['antonym 1'],
            mastery=1,
            is_word_of_day=False,
            word_of_day_date=None
        )
        self.word2 = Word.objects.create(
            word='test2',
            phonetic='/test2/',
            pos='verb',
            definition='Test word 2',
            level='C1',
            category='Test',
            examples=['Example 2'],
            collocations=['collocation 2'],
            synonyms=['synonym 2'],
            antonyms=['antonym 2'],
            mastery=2,
            is_word_of_day=False,
            word_of_day_date=None
        )

    def test_get_existing_word_of_day(self):
        """Test getting today's word of the day when it exists"""
        today = timezone.now().date()
        # Clear any existing WOTD first
        Word.objects.all().update(is_word_of_day=False, word_of_day_date=None)
        self.word1.is_word_of_day = True
        self.word1.word_of_day_date = today
        self.word1.save()
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['word'], 'test1')
        self.assertEqual(data['definition'], 'Test word 1')
        self.assertEqual(data['phonetic'], '/test1/')
        self.assertEqual(data['pos'], 'noun')
        self.assertEqual(data['level'], 'B2')
        self.assertEqual(data['category'], 'Test')
        self.assertEqual(data['examples'], ['Example 1'])
        self.assertEqual(data['collocations'], ['collocation 1'])
        self.assertEqual(data['synonyms'], ['synonym 1'])
        self.assertEqual(data['antonyms'], ['antonym 1'])
        self.assertEqual(data['mastery'], 1)

    def test_get_new_word_of_day_when_none_exists(self):
        """Test that a new word is selected when no WOTD exists for today"""
        # Ensure no WOTD exists
        Word.objects.all().update(is_word_of_day=False, word_of_day_date=None)
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have selected a word (either word1 or word2)
        self.assertIn(data['word'], ['test1', 'test2'])
        
        # Verify the word was marked as WOTD
        wotd = Word.objects.get(word=data['word'])
        self.assertTrue(wotd.is_word_of_day)
        self.assertEqual(wotd.word_of_day_date, timezone.now().date())

    def test_cycle_through_all_words(self):
        """Test that the system cycles through all words before repeating"""
        # Clear WOTD flags first
        Word.objects.all().update(is_word_of_day=False, word_of_day_date=None)
        
        # Mark all words as used
        Word.objects.all().update(is_word_of_day=True, word_of_day_date=timezone.now().date())
        
        # Create a third word that hasn't been used
        word3 = Word.objects.create(
            word='test3',
            definition='Test word 3',
            is_word_of_day=False,
            word_of_day_date=None
        )
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['word'], 'test3')
        
        # Verify word3 is now WOTD
        word3.refresh_from_db()
        self.assertTrue(word3.is_word_of_day)
        self.assertEqual(word3.word_of_day_date, timezone.now().date())

    def test_reset_when_all_words_used(self):
        """Test that all words are reset when all have been used"""
        # Clear WOTD flags first
        Word.objects.all().update(is_word_of_day=False, word_of_day_date=None)
        
        # Mark all words as used
        Word.objects.all().update(is_word_of_day=True, word_of_day_date=timezone.now().date())
        
        # Now there should be no unused words
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should pick a word (either word1 or word2)
        self.assertIn(data['word'], ['test1', 'test2'])
        
        # Verify WOTD flags were reset
        wotd_count = Word.objects.filter(is_word_of_day=True).count()
        self.assertEqual(wotd_count, 1)  # Only one should be marked as WOTD

    def test_no_words_available(self):
        """Test error response when no words exist"""
        Word.objects.all().delete()
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data['error'], 'No words available')


class GetUserStatsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('user_stats')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create words
        self.word1 = Word.objects.create(
            word='apple',
            definition='A fruit',
            category='Food'
        )
        self.word2 = Word.objects.create(
            word='dog',
            definition='An animal',
            category='Animals'
        )
        self.word3 = Word.objects.create(
            word='car',
            definition='A vehicle',
            category='Transport'
        )

    def test_anonymous_user_stats(self):
        """Test stats for anonymous user"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['streak'], 0)
        self.assertEqual(data['known'], 0)
        self.assertEqual(data['total'], 0)
        self.assertEqual(data['due'], 0)
        self.assertEqual(data['xp'], 0)
        self.assertEqual(data['level'], 1)
        self.assertEqual(data['level_xp'], 0)
        self.assertEqual(data['next_level_xp'], 200)
        self.assertEqual(data['level_percent'], 0)
        self.assertEqual(data['topics'], [])
        self.assertEqual(data['recent_activity'], [])
        self.assertEqual(
            data['insight'],
            'Sign in to track your real progress and vocabulary by topic.'
        )

    def test_authenticated_user_with_no_words(self):
        """Test stats for authenticated user with no learned words"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['streak'], 0)
        self.assertEqual(data['known'], 0)
        self.assertEqual(data['total'], 0)
        self.assertEqual(data['due'], 0)
        self.assertEqual(data['xp'], 0)
        self.assertEqual(data['level'], 1)
        self.assertEqual(data['level_xp'], 0)
        self.assertEqual(data['next_level_xp'], 200)
        self.assertEqual(data['level_percent'], 0)
        
        # Should show categories from all words even if user has none
        self.assertGreater(len(data['topics']), 0)
        self.assertEqual(data['recent_activity'], [])
        self.assertEqual(
            data['insight'],
            'Start learning words to unlock insights about your progress.'
        )

    def test_authenticated_user_with_words(self):
        """Test stats for authenticated user with learned words"""
        self.client.login(username='testuser', password='password123')
        
        # Create UserWord entries
        UserWord.objects.create(
            user=self.user,
            word=self.word1,
            mastered=True,
            mastery_level=4,
            reviewed_at=timezone.now()
        )
        UserWord.objects.create(
            user=self.user,
            word=self.word2,
            mastered=False,
            mastery_level=1,
            reviewed_at=timezone.now()
        )
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['known'], 1)
        self.assertEqual(data['total'], 2)
        self.assertEqual(data['due'], 1)
        self.assertEqual(data['xp'], (1 * 10) + (1 * 5))  # 10 + 5 = 15
        
        # Check topics
        self.assertGreater(len(data['topics']), 0)
        food_topic = next((t for t in data['topics'] if t['category'] == 'Food'), None)
        self.assertIsNotNone(food_topic)
        self.assertEqual(food_topic['count'], 1)
        self.assertEqual(food_topic['mastered'], 1)

    def test_user_streak_calculation(self):
        """Test streak calculation for authenticated user"""
        self.client.login(username='testuser', password='password123')
        
        # Clear existing UserWord entries
        UserWord.objects.filter(user=self.user).delete()
        
        # Create activity for today, yesterday, and day before
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)
        
        # Day before yesterday's activity
        word1 = Word.objects.create(word='word1')
        uw1 = UserWord.objects.create(
            user=self.user,
            word=word1,
            mastered=True
        )
        UserWord.objects.filter(pk=uw1.pk).update(
            reviewed_at=timezone.now() - timedelta(days=2)
        )
        
        # Yesterday's activity
        word2 = Word.objects.create(word='word2')
        uw2 = UserWord.objects.create(
            user=self.user,
            word=word2,
            mastered=True
        )
        UserWord.objects.filter(pk=uw2.pk).update(
            reviewed_at=timezone.now() - timedelta(days=1)
        )
        
        # Today's activity
        word3 = Word.objects.create(word='word3')
        uw3 = UserWord.objects.create(
            user=self.user,
            word=word3,
            mastered=True
        )
        # uw3 already has today's timestamp because of auto_now=True
        
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['streak'], 3)  # 3 consecutive days

    def test_level_calculation(self):
        """Test that levels are calculated correctly based on XP"""
        self.client.login(username='testuser', password='password123')
        
        # Clear existing UserWord entries
        UserWord.objects.filter(user=self.user).delete()
        
        # Create many mastered words to get XP
        for i in range(30):
            word = Word.objects.create(
                word=f'word_{i}',
                definition=f'Definition {i}'
            )
            UserWord.objects.create(
                user=self.user,
                word=word,
                mastered=True,
                mastery_level=4
            )
        
        response = self.client.get(self.url)
        data = response.json()
        
        # Should be at least level 2 with 30 words (300 XP)
        self.assertGreaterEqual(data['level'], 2)
        self.assertGreater(data['xp'], 200)


class SyncLocalWordsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('sync_local_words')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

    def test_unauthenticated_user_redirected(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.post(self.url, data=json.dumps({'words': []}), content_type='application/json')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_sync_no_words(self):
        """Test syncing with empty word list"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(self.url, data=json.dumps({'words': []}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['synced'], 0)

    def test_sync_new_words(self):
        """Test syncing new words from localStorage"""
        self.client.login(username='testuser', password='password123')
        
        local_words = [
            {
                'word': 'new_word1',
                'phonetic': '/njuː/',
                'pos': 'noun',
                'def': 'A new word',
                'known': False,
                'mastery': 1,
                'examples': ['Example'],
                'collocations': ['Collocation'],
                'synonyms': ['Synonym'],
                'antonyms': ['Antonym']
            },
            {
                'word': 'new_word2',
                'phonetic': '/njuː/',
                'pos': 'verb',
                'def': 'Another new word',
                'known': True,
                'mastery': 4,
                'examples': ['Example 2'],
                'collocations': ['Collocation 2'],
                'synonyms': ['Synonym 2'],
                'antonyms': ['Antonym 2']
            }
        ]
        
        response = self.client.post(
            self.url,
            data=json.dumps({'words': local_words}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['synced'], 2)
        
        # Verify words were created in database
        word1 = Word.objects.get(word='new_word1')
        word2 = Word.objects.get(word='new_word2')
        self.assertEqual(word1.definition, 'A new word')
        self.assertEqual(word2.definition, 'Another new word')
        
        # Verify UserWord entries
        uw1 = UserWord.objects.get(user=self.user, word=word1)
        uw2 = UserWord.objects.get(user=self.user, word=word2)
        self.assertFalse(uw1.mastered)
        self.assertTrue(uw2.mastered)
        self.assertEqual(uw1.mastery_level, 1)
        self.assertEqual(uw2.mastery_level, 4)

    def test_sync_existing_words_updates_mastery(self):
        """Test that syncing existing words updates mastery levels"""
        self.client.login(username='testuser', password='password123')
        
        # Create existing word and UserWord
        word = Word.objects.create(
            word='existing_word',
            definition='Original definition'
        )
        uw = UserWord.objects.create(
            user=self.user,
            word=word,
            mastered=False,
            mastery_level=1
        )
        
        # Sync with higher mastery
        local_words = [
            {
                'word': 'existing_word',
                'known': True,
                'mastery': 4
            }
        ]
        
        response = self.client.post(
            self.url,
            data=json.dumps({'words': local_words}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        uw.refresh_from_db()
        self.assertTrue(uw.mastered)
        self.assertEqual(uw.mastery_level, 4)

    def test_sync_invalid_json(self):
        """Test syncing with invalid JSON"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(
            self.url,
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid JSON', response.json()['error'])

    def test_sync_wrong_method(self):
        """Test that GET requests are rejected"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class GetWordDataTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.word = Word.objects.create(
            word='testword',
            phonetic='/test/',
            pos='noun',
            definition='A test word',
            level='B2',
            category='Test',
            examples=['Example'],
            collocations=['Collocation'],
            synonyms=['Synonym'],
            antonyms=['Antonym'],
            mastery=3
        )

    def test_get_existing_word(self):
        """Test getting data for an existing word"""
        # Use the URL pattern from your urls.py
        # Assuming the pattern is something like: path('api/word/<str:word_text>/', get_word_data, name='get_word_data')
        response = self.client.get(f'/vocabulary/api/word/{self.word.word}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['word'], 'testword')
        self.assertEqual(data['phonetic'], '/test/')
        self.assertEqual(data['pos'], 'noun')
        self.assertEqual(data['definition'], 'A test word')
        self.assertEqual(data['level'], 'B2')
        self.assertEqual(data['category'], 'Test')
        self.assertEqual(data['examples'], ['Example'])
        self.assertEqual(data['collocations'], ['Collocation'])
        self.assertEqual(data['synonyms'], ['Synonym'])
        self.assertEqual(data['antonyms'], ['Antonym'])
        self.assertEqual(data['mastery'], 3)

    def test_get_nonexistent_word(self):
        """Test getting data for a non-existent word"""
        response = self.client.get('/vocabulary/api/word/nonexistent/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Word not found')

    def test_get_word_case_insensitive(self):
        """Test that word lookup is case-insensitive"""
        response = self.client.get(f'/vocabulary/api/word/TESTWORD/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['word'], 'testword')


class MarkWordKnownTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('mark_word_known')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.word = Word.objects.create(
            word='testword',
            definition='A test word'
        )

    def test_mark_word_known_unauthenticated(self):
        """Test marking word as known without authentication (should work without DB save)"""
        response = self.client.post(
            self.url,
            data=json.dumps({'word': 'testword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['word'], 'testword')
        
        # Should NOT create UserWord for unauthenticated user
        self.assertFalse(UserWord.objects.filter(word=self.word).exists())

    def test_mark_word_known_authenticated(self):
        """Test marking word as known when authenticated"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(
            self.url,
            data=json.dumps({'word': 'testword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify UserWord was created
        uw = UserWord.objects.get(user=self.user, word=self.word)
        self.assertTrue(uw.mastered)
        self.assertEqual(uw.mastery_level, 4)

    def test_mark_word_known_creates_new_word(self):
        """Test that marking a new word creates it if it doesn't exist"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(
            self.url,
            data=json.dumps({'word': 'newword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify word was created
        word = Word.objects.get(word='newword')
        self.assertEqual(word.definition, 'Recently added — definition will be filled in')
        
        # Verify UserWord was created
        uw = UserWord.objects.get(user=self.user, word=word)
        self.assertTrue(uw.mastered)

    def test_mark_word_known_missing_word(self):
        """Test error when word is missing"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Word is required')

    def test_mark_word_known_invalid_json(self):
        """Test error with invalid JSON"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(
            self.url,
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid JSON')

    def test_mark_word_known_wrong_method(self):
        """Test that GET requests are rejected"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class GetReviewWordsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Use the URL pattern from your urls.py
        self.url = '/vocabulary/api/review-words/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create words
        self.word1 = Word.objects.create(word='apple', definition='A fruit')
        self.word2 = Word.objects.create(word='dog', definition='An animal')
        self.word3 = Word.objects.create(word='car', definition='A vehicle')
        self.word4 = Word.objects.create(word='house', definition='A building')

    def test_anonymous_user_review_words(self):
        """Test review words for anonymous user"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['total'], 4)  # All words
        self.assertEqual(data['mastered_count'], 0)
        self.assertEqual(set(data['words']), {'apple', 'dog', 'car', 'house'})

    def test_authenticated_user_with_learning_words(self):
        """Test review words for authenticated user with some learned words"""
        self.client.login(username='testuser', password='password123')
        
        # Mark apple as mastered
        UserWord.objects.create(
            user=self.user,
            word=self.word1,
            mastered=True
        )
        # Mark dog as learning (not mastered)
        UserWord.objects.create(
            user=self.user,
            word=self.word2,
            mastered=False
        )
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should include learning words + unseen words
        self.assertIn('dog', data['words'])
        self.assertIn('car', data['words'])
        self.assertIn('house', data['words'])
        self.assertNotIn('apple', data['words'])  # Mastered words should be excluded
        
        self.assertEqual(data['mastered_count'], 1)

    def test_authenticated_user_all_words_learned(self):
        """Test when all words are learned"""
        self.client.login(username='testuser', password='password123')
        
        # Mark all words as mastered
        for word in [self.word1, self.word2, self.word3, self.word4]:
            UserWord.objects.create(
                user=self.user,
                word=word,
                mastered=True
            )
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should return no review words
        self.assertEqual(len(data['words']), 0)
        self.assertEqual(data['total'], 0)
        self.assertEqual(data['mastered_count'], 4)


class GetUserWordsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Use the URL pattern from your urls.py
        self.url = '/vocabulary/api/user-words/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create words
        self.word1 = Word.objects.create(word='apple', definition='A fruit')
        self.word2 = Word.objects.create(word='dog', definition='An animal')
        self.word3 = Word.objects.create(word='car', definition='A vehicle')

    def test_anonymous_user_words(self):
        """Test getting all words for anonymous user"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(len(data['words']), 3)
        for word_data in data['words']:
            self.assertFalse(word_data['mastered'])
            self.assertEqual(word_data['mastery_level'], 0)

    def test_authenticated_user_words(self):
        """Test getting words with mastery status for authenticated user"""
        self.client.login(username='testuser', password='password123')
        
        # Create UserWord entries
        UserWord.objects.create(
            user=self.user,
            word=self.word1,
            mastered=True,
            mastery_level=4
        )
        UserWord.objects.create(
            user=self.user,
            word=self.word2,
            mastered=False,
            mastery_level=1
        )
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(len(data['words']), 3)
        
        # Check each word's mastery status
        for word_data in data['words']:
            if word_data['word'] == 'apple':
                self.assertTrue(word_data['mastered'])
                self.assertEqual(word_data['mastery_level'], 4)
            elif word_data['word'] == 'dog':
                self.assertFalse(word_data['mastered'])
                self.assertEqual(word_data['mastery_level'], 1)
            else:  # car
                self.assertFalse(word_data['mastered'])
                self.assertEqual(word_data['mastery_level'], 0)


class SaveWordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('save_word')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

    def test_save_word_unauthenticated(self):
        """Test saving word without authentication"""
        response = self.client.post(
            self.url,
            data=json.dumps({'word': 'testword', 'context': 'Test context'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('testword', data['message'])
        
        # Word should be created in database
        word = Word.objects.get(word='testword')
        self.assertEqual(word.definition, 'Test context')
        
        # But UserWord should NOT be created
        self.assertFalse(UserWord.objects.filter(word=word).exists())

    def test_save_word_authenticated(self):
        """Test saving word when authenticated"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(
            self.url,
            data=json.dumps({'word': 'testword', 'context': 'Test context'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])
        
        # Verify UserWord was created
        word = Word.objects.get(word='testword')
        uw = UserWord.objects.get(user=self.user, word=word)
        self.assertFalse(uw.mastered)
        self.assertEqual(uw.mastery_level, 0)

    def test_save_word_existing_word(self):
        """Test saving an existing word"""
        self.client.login(username='testuser', password='password123')
        
        # Create existing word
        word = Word.objects.create(
            word='existingword',
            definition='Original definition'
        )
        
        response = self.client.post(
            self.url,
            data=json.dumps({'word': 'existingword', 'context': 'New context'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Note: get_or_create returns created=False when it finds existing
        # The view passes 'created' from get_or_create
        self.assertFalse(data['created'])
        
        # Word definition should be updated
        word.refresh_from_db()
        self.assertEqual(word.definition, 'New context')

    def test_save_word_without_context(self):
        """Test saving a word without context"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(
            self.url,
            data=json.dumps({'word': 'testword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        word = Word.objects.get(word='testword')
        self.assertEqual(word.definition, 'Recently added — definition will be filled in')

    def test_save_word_missing_word(self):
        """Test error when word is missing"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Word is required')

    def test_save_word_invalid_json(self):
        """Test error with invalid JSON"""
        self.client.login(username='testuser', password='password123')
        
        response = self.client.post(
            self.url,
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid JSON')

    def test_save_word_wrong_method(self):
        """Test that GET requests are rejected"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class IntegrationTests(TestCase):
    """Integration tests that test multiple views together"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        # Clear any existing WOTD entries
        Word.objects.all().delete()
        self.word = Word.objects.create(
            word='integration_test',
            definition='Integration test word'
        )
        # Ensure only one WOTD exists
        Word.objects.all().update(is_word_of_day=False, word_of_day_date=None)

    def test_full_word_learning_flow(self):
        """Test the complete flow of learning a word"""
        # 1. Get word of the day
        wotd_response = self.client.get(reverse('word_of_day'))
        self.assertEqual(wotd_response.status_code, 200)
        wotd_data = wotd_response.json()
        
        # 2. Get word details - use direct URL path
        detail_response = self.client.get(f'/vocabulary/api/word/{wotd_data["word"]}/')
        self.assertEqual(detail_response.status_code, 200)
        
        # 3. Login
        self.client.login(username='testuser', password='password123')
        
        # 4. Mark word as known
        mark_response = self.client.post(
            reverse('mark_word_known'),
            data=json.dumps({'word': wotd_data['word']}),
            content_type='application/json'
        )
        self.assertEqual(mark_response.status_code, 200)
        
        # 5. Check user stats
        stats_response = self.client.get(reverse('user_stats'))
        self.assertEqual(stats_response.status_code, 200)
        stats_data = stats_response.json()
        self.assertEqual(stats_data['known'], 1)

    def test_sync_and_stats_flow(self):
        """Test syncing words and then checking stats"""
        self.client.login(username='testuser', password='password123')
        
        # 1. Sync words from localStorage
        local_words = [
            {'word': 'sync_word1', 'known': True, 'mastery': 4},
            {'word': 'sync_word2', 'known': False, 'mastery': 1}
        ]
        
        sync_response = self.client.post(
            reverse('sync_local_words'),
            data=json.dumps({'words': local_words}),
            content_type='application/json'
        )
        self.assertEqual(sync_response.status_code, 200)
        
        # 2. Get user words - use direct URL path
        words_response = self.client.get('/vocabulary/api/user-words/')
        self.assertEqual(words_response.status_code, 200)
        words_data = words_response.json()
        
        # Verify mastery status
        for word_data in words_data['words']:
            if word_data['word'] == 'sync_word1':
                self.assertTrue(word_data['mastered'])
                self.assertEqual(word_data['mastery_level'], 4)
            elif word_data['word'] == 'sync_word2':
                self.assertFalse(word_data['mastered'])
                self.assertEqual(word_data['mastery_level'], 1)
        
        # 3. Get stats
        stats_response = self.client.get(reverse('user_stats'))
        self.assertEqual(stats_response.status_code, 200)
        stats_data = stats_response.json()
        self.assertEqual(stats_data['total'], 2)
        self.assertEqual(stats_data['known'], 1)