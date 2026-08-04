from django.core.management.base import BaseCommand
from vocabulary.models import Word
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seed initial vocabulary words'

    def handle(self, *args, **kwargs):
        words_data = [
            {
                'word': 'ephemeral',
                'phonetic': '/ɪˈfem.ər.əl/',
                'pos': 'adjective',
                'definition': 'Lasting for a very short time; fleeting or transitory.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'Fame in the digital age can be ephemeral — here today, forgotten tomorrow.',
                    'The beauty of cherry blossoms is ephemeral, lasting only a few days each spring.',
                    'He preferred ephemeral pleasures to long-term commitments.'
                ],
                'collocations': ['ephemeral beauty', 'ephemeral nature', 'ephemeral moment', 'ephemeral fame'],
                'synonyms': ['fleeting', 'transitory', 'momentary', 'short-lived'],
                'antonyms': ['permanent', 'lasting', 'enduring', 'eternal'],
                'mastery': 1,
                'is_word_of_day': True,
                'word_of_day_date': timezone.now().date()
            },
            {
                'word': 'ubiquitous',
                'phonetic': '/juːˈbɪk.wɪ.təs/',
                'pos': 'adjective',
                'definition': 'Present, appearing, or found everywhere.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'Smartphones have become ubiquitous in modern life.',
                    'The company aims to make its brand ubiquitous across the region.'
                ],
                'collocations': ['ubiquitous presence', 'become ubiquitous'],
                'synonyms': ['omnipresent', 'pervasive', 'universal', 'ever-present'],
                'antonyms': ['rare', 'scarce', 'uncommon', 'limited'],
                'mastery': 2,
                'is_word_of_day': False,
                'word_of_day_date': None
            },
            {
                'word': 'paradigm',
                'phonetic': '/ˈpær.ə.daɪm/',
                'pos': 'noun',
                'definition': 'A typical example or pattern of something; a model of how things work.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The discovery shifted the scientific paradigm.',
                    'She offered a new paradigm for understanding motivation.'
                ],
                'collocations': ['paradigm shift', 'dominant paradigm'],
                'synonyms': ['model', 'framework', 'pattern', 'archetype'],
                'antonyms': ['anomaly', 'exception'],
                'mastery': 3,
                'is_word_of_day': False,
                'word_of_day_date': None
            },
            {
                'word': 'resilient',
                'phonetic': '/rɪˈzɪl.i.ənt/',
                'pos': 'adjective',
                'definition': 'Able to recover quickly from difficulties; tough and adaptable.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'Children are often remarkably resilient.',
                    'A resilient economy can withstand external shocks.'
                ],
                'collocations': ['resilient community', 'emotionally resilient'],
                'synonyms': ['tough', 'adaptable', 'durable', 'buoyant'],
                'antonyms': ['fragile', 'brittle', 'vulnerable'],
                'mastery': 2,
                'is_word_of_day': False,
                'word_of_day_date': None
            },
            {
                'word': 'nuanced',
                'phonetic': '/ˈnjuː.ɑːnst/',
                'pos': 'adjective',
                'definition': 'Characterized by subtle differences or distinctions; not black-and-white.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'Her analysis of the issue was far more nuanced than the headlines suggested.',
                    'He gave a nuanced performance that avoided cliché.'
                ],
                'collocations': ['nuanced understanding', 'nuanced approach'],
                'synonyms': ['subtle', 'refined', 'sophisticated'],
                'antonyms': ['blunt', 'simplistic', 'crude'],
                'mastery': 1,
                'is_word_of_day': False,
                'word_of_day_date': None
            },
            {
                'word': 'pragmatic',
                'phonetic': '/præɡˈmæt.ɪk/',
                'pos': 'adjective',
                'definition': 'Dealing with things sensibly and realistically; focused on practical results.',
                'level': 'B2',
                'category': 'Business',
                'examples': [
                    'We need a pragmatic solution, not an idealistic one.',
                    'Her style of leadership is calm and pragmatic.'
                ],
                'collocations': ['pragmatic approach', 'pragmatic reasons'],
                'synonyms': ['practical', 'realistic', 'sensible'],
                'antonyms': ['idealistic', 'impractical', 'theoretical'],
                'mastery': 3,
                'is_word_of_day': False,
                'word_of_day_date': None
            },
            {
                'word': 'meticulous',
                'phonetic': '/məˈtɪk.jə.ləs/',
                'pos': 'adjective',
                'definition': 'Showing great attention to detail; very careful and precise.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'He kept meticulous records of every experiment.',
                    'The restoration was carried out with meticulous care.'
                ],
                'collocations': ['meticulous attention', 'meticulous planning'],
                'synonyms': ['careful', 'precise', 'thorough', 'fastidious'],
                'antonyms': ['careless', 'sloppy', 'haphazard'],
                'mastery': 1,
                'is_word_of_day': False,
                'word_of_day_date': None
            },
            {
                'word': 'candid',
                'phonetic': '/ˈkæn.dɪd/',
                'pos': 'adjective',
                'definition': 'Truthful and straightforward; frank.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'She gave a candid assessment of the project\'s weaknesses.',
                    'I appreciate your candid feedback.'
                ],
                'collocations': ['candid conversation', 'candid opinion'],
                'synonyms': ['frank', 'honest', 'straightforward', 'blunt'],
                'antonyms': ['evasive', 'guarded', 'diplomatic'],
                'mastery': 4,
                'is_word_of_day': False,
                'word_of_day_date': None
            }
        ]

        for word_data in words_data:
            word, created = Word.objects.get_or_create(
                word=word_data['word'],
                defaults=word_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created word: {word.word}'))
            else:
                self.stdout.write(self.style.WARNING(f'Word already exists: {word.word}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded words!'))