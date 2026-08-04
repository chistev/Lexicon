from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import Word

def get_word_of_day(request):
    """Get the current word of the day"""
    today = timezone.now().date()
    
    # Try to get today's word of the day
    try:
        wotd = Word.objects.get(is_word_of_day=True, word_of_day_date=today)
    except Word.DoesNotExist:
        # If no word for today, get the first word or set one
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