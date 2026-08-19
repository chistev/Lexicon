from django.db.models import Count, Q
from datetime import timedelta
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from .models import Word, UserWord
import json

def get_word_of_day(request):
    """Get the current word of the day - same for all users."""
    today = timezone.now().date()

    # ---------------------------------------------------------
    # 1. Check for a valid existing WOTD for today.
    # ---------------------------------------------------------
    todays_wotds = Word.objects.filter(
        is_word_of_day=True,
        word_of_day_date=today
    ).order_by('id')

    # Only trust the current WOTD if there is exactly one.
    if todays_wotds.count() == 1:
        wotd = todays_wotds.first()

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

    # ---------------------------------------------------------
    # 2. Find a word that has never been used as WOTD.
    #
    # is_word_of_day=True is also our historical "used" flag.
    # ---------------------------------------------------------
    used_word_ids = Word.objects.filter(
        is_word_of_day=True
    ).values_list('id', flat=True)

    available_word = (
        Word.objects
        .exclude(id__in=used_word_ids)
        .order_by('id')
        .first()
    )

    if available_word:
        # Clear any broken/duplicate current-day WOTD state.
        Word.objects.filter(
            is_word_of_day=True,
            word_of_day_date=today
        ).update(
            is_word_of_day=False,
            word_of_day_date=None
        )

        available_word.is_word_of_day = True
        available_word.word_of_day_date = today
        available_word.save(
            update_fields=[
                'is_word_of_day',
                'word_of_day_date'
            ]
        )

        wotd = available_word

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

    # ---------------------------------------------------------
    # 3. All words have been used.
    #    Start a completely new cycle.
    # ---------------------------------------------------------

    # IMPORTANT:
    # Clear BOTH flags, not just word_of_day_date.
    Word.objects.all().update(
        is_word_of_day=False,
        word_of_day_date=None
    )

    # Pick the first word in the new cycle.
    wotd = Word.objects.order_by('id').first()

    if not wotd:
        return JsonResponse(
            {'error': 'No words available'},
            status=404
        )

    wotd.is_word_of_day = True
    wotd.word_of_day_date = today
    wotd.save(
        update_fields=[
            'is_word_of_day',
            'word_of_day_date'
        ]
    )

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

        # ---- Streak ----
        from django.db.models.functions import TruncDate

        today = timezone.now().date()

        activity_dates = list(
            UserWord.objects
            .filter(user=user)
            .annotate(day=TruncDate('reviewed_at'))
            .values_list('day', flat=True)
            .distinct()
            .order_by('-day')
        )

        streak = 0
        if activity_dates:
            if activity_dates[0] == today:
                expected = today
            elif activity_dates[0] == today - timedelta(days=1):
                expected = today - timedelta(days=1)
            else:
                expected = None

            if expected is not None:
                for day in activity_dates:
                    if day == expected:
                        streak += 1
                        expected -= timedelta(days=1)
                    else:
                        break

        # ---- Vocabulary by topic (category) ----
        topic_qs = (
            UserWord.objects
            .filter(user=user)
            .values('word__category')
            .annotate(
                total=Count('id'),
                mastered=Count('id', filter=Q(mastered=True))
            )
            .order_by('-total')
        )
        topics = []
        max_count = 1
        for row in topic_qs:
            cat = row['word__category'] or 'Uncategorized'
            count = row['total']
            max_count = max(max_count, count)
            topics.append({
                'category': cat,
                'count': count,
                'mastered': row['mastered'],
            })

        for t in topics:
            t['percent'] = round((t['count'] / max_count) * 100) if max_count else 0

        if not topics:
            all_cats = (
                Word.objects
                .exclude(category='')
                .values('category')
                .annotate(total=Count('id'))
                .order_by('-total')[:8]
            )
            for row in all_cats:
                topics.append({
                    'category': row['category'],
                    'count': 0,
                    'mastered': 0,
                    'percent': 0,
                })

        # ---- Level calculation ----
        level_thresholds = [0, 200, 500, 1000, 2000, 3500, 5500, 8000]
        level = 1
        next_level_xp = 200
        for i, thresh in enumerate(level_thresholds):
            if xp >= thresh:
                level = i + 1
                next_level_xp = level_thresholds[i + 1] if i + 1 < len(level_thresholds) else thresh + 2000
            else:
                break

        current_level_xp = level_thresholds[level - 1] if level > 1 else 0
        progress_in_level = xp - current_level_xp
        needed_for_next = next_level_xp - current_level_xp
        level_percent = round((progress_in_level / needed_for_next) * 100) if needed_for_next else 100

        # ---- Recent activity ----
        recent = (
            UserWord.objects
            .filter(user=user)
            .select_related('word')
            .order_by('-reviewed_at')[:8]
        )
        recent_activity = []
        for uw in recent:
            if uw.mastered:
                recent_activity.append(f'Marked <strong>{uw.word.word}</strong> as known')
            else:
                recent_activity.append(f'Reviewed / learning <strong>{uw.word.word}</strong>')

        insight_pct = min(15, max(1, round(mastered_words * 0.4))) if mastered_words else 0
        insight = (
            f"You've learned enough this week to understand roughly <strong>{insight_pct}% more</strong> of a typical newspaper article."
            if mastered_words else
            "Start learning words to unlock insights about your progress."
        )

        return JsonResponse({
            'streak': streak,
            'known': mastered_words,
            'total': total_words,
            'due': due_for_review,
            'xp': xp,
            'level': level,
            'level_xp': xp,
            'next_level_xp': next_level_xp,
            'level_percent': level_percent,
            'topics': topics,
            'recent_activity': recent_activity,
            'insight': insight,
        })
    else:
        return JsonResponse({
            'streak': 0,
            'known': 0,
            'total': 0,
            'due': 0,
            'xp': 0,
            'level': 1,
            'level_xp': 0,
            'next_level_xp': 200,
            'level_percent': 0,
            'topics': [],
            'recent_activity': [],
            'insight': 'Sign in to track your real progress and vocabulary by topic.',
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
    """
    Always return the full word list.
    For authenticated users, attach their personal mastery status from UserWord.
    For anonymous users, mastery stays False (frontend uses localStorage).
    """
    # Build a quick lookup of the current user's mastery (if logged in)
    mastery_map = {}  # word_id -> (mastered, mastery_level)
    if request.user.is_authenticated:
        for uw in UserWord.objects.filter(user=request.user).select_related('word'):
            mastery_map[uw.word_id] = (uw.mastered, uw.mastery_level)

    words_data = []
    for word in Word.objects.all():
        if word.id in mastery_map:
            mastered, mastery_level = mastery_map[word.id]
        else:
            mastered, mastery_level = False, 0

        words_data.append({
            'word': word.word,
            'definition': word.definition,
            'mastered': mastered,
            'mastery_level': mastery_level,
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

        # Try to get the existing word
        try:
            word = Word.objects.get(word=word_text)
            word_created = False
            # Update definition if a new context was provided
            if context:
                word.definition = context
                word.save()
        except Word.DoesNotExist:
            word = Word.objects.create(
                word=word_text,
                definition=context or 'Recently added — definition will be filled in'
            )
            word_created = True

        # If user is authenticated, also create the UserWord link
        if request.user.is_authenticated:
            UserWord.objects.get_or_create(
                user=request.user,
                word=word,
                defaults={'mastered': False, 'mastery_level': 0}
            )

        return JsonResponse({
            'success': True,
            'message': f'Word "{word_text}" saved',
            'created': word_created
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)