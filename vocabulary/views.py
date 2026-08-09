from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from .models import Word, UserWord
import json

def get_word_of_day(request):
    """Get the current word of the day"""
    today = timezone.now().date()
    
    try:
        wotd = Word.objects.get(is_word_of_day=True, word_of_day_date=today)
    except Word.DoesNotExist:
        wotd = Word.objects.first()
        if wotd:
            wotd.is_word_of_day = True
            wotd.word_of_day_date = today
            wotd.save()
    
    if not wotd:
        return JsonResponse({'error': 'No words available'}, status=404)
    
    return JsonResponse({
        'word': wotd.word,
        'phonetic': wotd.phonetic,
        'pos': wotd.pos,
        'definition': wotd.definition,
        'level': wotd.level,
        'category': wotd.category,
        'examples': wotd.examples,
        'collocations': wotd.collocations,
        'synonyms': wotd.synonyms,
        'antonyms': wotd.antonyms,
        'mastery': wotd.mastery,
    })

def get_user_stats(request):
    """Get stats for the user (works for both authenticated and anonymous)"""
    if request.user.is_authenticated:
        user = request.user
        total_words = UserWord.objects.filter(user=user).count()
        mastered_words = UserWord.objects.filter(user=user, mastered=True).count()
        due_for_review = UserWord.objects.filter(user=user, mastered=False).count()
        xp = (mastered_words * 10) + ((total_words - mastered_words) * 5)
        
        from datetime import timedelta
        today = timezone.now().date()
        today_activity = UserWord.objects.filter(user=user, reviewed_at__date=today).exists()
        yesterday = today - timedelta(days=1)
        yesterday_activity = UserWord.objects.filter(user=user, reviewed_at__date=yesterday).exists()
        
        streak = 0
        if today_activity:
            streak = 1
            check_date = today - timedelta(days=1)
            while UserWord.objects.filter(user=user, reviewed_at__date=check_date).exists():
                streak += 1
                check_date -= timedelta(days=1)
        elif yesterday_activity:
            streak = 1
            check_date = yesterday - timedelta(days=1)
            while UserWord.objects.filter(user=user, reviewed_at__date=check_date).exists():
                streak += 1
                check_date -= timedelta(days=1)
        
        return JsonResponse({
            'streak': streak,
            'known': mastered_words,
            'total': total_words,
            'due': due_for_review,
            'xp': xp,
        })
    else:
        # For anonymous users, return stats from localStorage
        # The frontend will handle this
        return JsonResponse({
            'streak': 0,
            'known': 0,
            'total': 0,
            'due': 0,
            'xp': 0,
        })

@login_required
@csrf_exempt
def sync_local_words(request):
    """Sync local words from localStorage to the database"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        local_words = data.get('words', [])
        local_stats = data.get('stats', {})
        
        if not local_words:
            return JsonResponse({'success': True, 'message': 'No words to sync', 'synced': 0})
        
        user = request.user
        synced_count = 0
        
        for word_data in local_words:
            word_text = word_data.get('word', '').strip().lower()
            if not word_text:
                continue
            
            word, created = Word.objects.get_or_create(
                word=word_text,
                defaults={
                    'phonetic': word_data.get('phonetic', ''),
                    'pos': word_data.get('pos', ''),
                    'definition': word_data.get('def', 'Recently added — definition will be filled in'),
                    'examples': word_data.get('examples', []),
                    'collocations': word_data.get('collocations', []),
                    'synonyms': word_data.get('synonyms', []),
                    'antonyms': word_data.get('antonyms', []),
                    'mastery': word_data.get('mastery', 1),
                }
            )
            
            user_word, created = UserWord.objects.get_or_create(
                user=user,
                word=word,
                defaults={
                    'mastered': word_data.get('known', False),
                    'mastery_level': word_data.get('mastery', 0),
                }
            )
            
            if not created:
                if word_data.get('mastery', 0) > user_word.mastery_level:
                    user_word.mastery_level = word_data.get('mastery', 0)
                    user_word.mastered = word_data.get('known', False)
                    user_word.save()
                    synced_count += 1
            else:
                synced_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully synced {synced_count} words',
            'synced': synced_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_word_data(request, word_text):
    """Get detailed data for a specific word (works for all users)"""
    try:
        word = Word.objects.get(word=word_text.lower())
        return JsonResponse({
            'word': word.word,
            'phonetic': word.phonetic,
            'pos': word.pos,
            'definition': word.definition,
            'level': word.level,
            'category': word.category,
            'examples': word.examples,
            'collocations': word.collocations,
            'synonyms': word.synonyms,
            'antonyms': word.antonyms,
            'mastery': word.mastery,
        })
    except Word.DoesNotExist:
        return JsonResponse({'error': 'Word not found'}, status=404)

@csrf_exempt
def mark_word_known(request):
    """Mark a word as known/mastered (works for all users)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        word_text = data.get('word', '').strip().lower()
        
        if not word_text:
            return JsonResponse({'error': 'Word is required'}, status=400)
        
        # If user is authenticated, save to database
        if request.user.is_authenticated:
            word, created = Word.objects.get_or_create(
                word=word_text,
                defaults={'definition': 'Recently added — definition will be filled in'}
            )
            
            user_word, created = UserWord.objects.get_or_create(
                user=request.user,
                word=word,
                defaults={'mastered': True, 'mastery_level': 4}
            )
            
            if not created:
                user_word.mastered = True
                user_word.mastery_level = 4
                user_word.save()
        
        return JsonResponse({
            'success': True,
            'message': f'"{word_text}" marked as known',
            'word': word_text
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_review_words(request):
    """Get words that the user needs to review (works for all users)"""
    if request.user.is_authenticated:
        user = request.user
        mastered_words = UserWord.objects.filter(user=user, mastered=True).values_list('word__word', flat=True)
        learning_words = UserWord.objects.filter(user=user, mastered=False).values_list('word__word', flat=True)
        user_word_ids = UserWord.objects.filter(user=user).values_list('word_id', flat=True)
        unseen_words = Word.objects.exclude(id__in=user_word_ids).values_list('word', flat=True)[:10]
        review_words = list(learning_words) + list(unseen_words)
        
        return JsonResponse({
            'words': review_words,
            'total': len(review_words),
            'mastered_count': mastered_words.count()
        })
    else:
        # For anonymous users, return all words from the Word model
        # The frontend will filter based on localStorage
        all_words = Word.objects.values_list('word', flat=True)
        return JsonResponse({
            'words': list(all_words),
            'total': all_words.count(),
            'mastered_count': 0
        })

def get_user_words(request):
    """Get all words for the user (works for all users)"""
    if request.user.is_authenticated:
        user = request.user
        user_words = UserWord.objects.filter(user=user).select_related('word')
        
        words_data = []
        for uw in user_words:
            words_data.append({
                'word': uw.word.word,
                'definition': uw.word.definition,
                'mastered': uw.mastered,
                'mastery_level': uw.mastery_level
            })
        return JsonResponse({'words': words_data})
    else:
        # For anonymous users, return all words from the Word model
        # The frontend will handle which words are mastered via localStorage
        all_words = Word.objects.all()
        words_data = []
        for word in all_words:
            words_data.append({
                'word': word.word,
                'definition': word.definition,
                'mastered': False,  # Anonymous users track mastery in localStorage
                'mastery_level': 0
            })
        return JsonResponse({'words': words_data})

@csrf_exempt
def save_word(request):
    """Save a word for the user (works for all users)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        word_text = data.get('word', '').strip().lower()
        context = data.get('context', '')
        
        if not word_text:
            return JsonResponse({'error': 'Word is required'}, status=400)
        
        # Get or create the word in the database
        word, created = Word.objects.get_or_create(
            word=word_text,
            defaults={'definition': context or 'Recently added — definition will be filled in'}
        )
        
        # If user is authenticated, save to their account
        if request.user.is_authenticated:
            user_word, created = UserWord.objects.get_or_create(
                user=request.user,
                word=word,
                defaults={'mastered': False, 'mastery_level': 0}
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Word "{word_text}" saved',
            'created': created
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)