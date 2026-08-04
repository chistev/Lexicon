from django.db import models
from django.contrib.auth.models import User

class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    phonetic = models.CharField(max_length=100, blank=True)
    pos = models.CharField(max_length=50, blank=True)  # Part of speech
    definition = models.TextField()
    level = models.CharField(max_length=10, blank=True)  # C1, B2, etc.
    category = models.CharField(max_length=50, blank=True)  # Academic, Business, etc.
    examples = models.JSONField(default=list)
    collocations = models.JSONField(default=list)
    synonyms = models.JSONField(default=list)
    antonyms = models.JSONField(default=list)
    mastery = models.IntegerField(default=1)  # 1-4
    created_at = models.DateTimeField(auto_now_add=True)
    is_word_of_day = models.BooleanField(default=False)
    word_of_day_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.word

    class Meta:
        ordering = ['word']


class UserWord(models.Model):
    """Track which words a user has learned"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learned_words')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='learned_by')
    mastered = models.BooleanField(default=False)  # True = word is known/mastered
    mastery_level = models.IntegerField(default=0)  # 0-4
    reviewed_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'word']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.word.word} ({'Mastered' if self.mastered else 'Learning'})"