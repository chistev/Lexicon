from django.core.management.base import BaseCommand
from vocabulary.models import Word
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Seed initial vocabulary words'

    def handle(self, *args, **kwargs):
        # ============================================
        # 1. DELETE ALL EXISTING WORDS
        # ============================================
        self.stdout.write(self.style.WARNING('Deleting all existing words...'))
        deleted_count, _ = Word.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✓ Deleted {deleted_count} existing words'))
        
        # ============================================
        # 2. DEFINE WORD DATA
        # ============================================
        words_data = [
            # A
            {
                'word': 'approbate',
                'phonetic': '/ˈæp.rə.beɪt/',
                'pos': 'verb',
                'definition': 'To approve, sanction, or ratify officially.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The committee will approbate the new policy at the next meeting.',
                    'The board approbated the merger after extensive review.'
                ],
                'collocations': ['approbate officially', 'approbate a decision'],
                'synonyms': ['approve', 'sanction', 'ratify', 'endorse'],
                'antonyms': ['reject', 'condemn', 'disapprove'],
                'mastery': 1
            },
            {
                'word': 'abeyance',
                'phonetic': '/əˈbeɪ.əns/',
                'pos': 'noun',
                'definition': 'A state of temporary disuse or suspension.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The project was held in abeyance until funding was secured.',
                    'The matter remains in abeyance pending further investigation.'
                ],
                'collocations': ['in abeyance', 'held in abeyance', 'fall into abeyance'],
                'synonyms': ['suspension', 'dormancy', 'deferral', 'postponement'],
                'antonyms': ['continuation', 'activation', 'progression'],
                'mastery': 1
            },
            {
                'word': 'assiduous',
                'phonetic': '/əˈsɪd.ju.əs/',
                'pos': 'adjective',
                'definition': 'Showing great care, attention, and perseverance; diligent.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'She was assiduous in her research, leaving no stone unturned.',
                    'The assiduous student spent hours perfecting every assignment.'
                ],
                'collocations': ['assiduous efforts', 'assiduous attention', 'assiduous work'],
                'synonyms': ['diligent', 'persevering', 'meticulous', 'conscientious'],
                'antonyms': ['negligent', 'careless', 'lax', 'slipshod'],
                'mastery': 1
            },
            {
                'word': 'astute',
                'phonetic': '/əˈstjuːt/',
                'pos': 'adjective',
                'definition': 'Having or showing an ability to accurately assess situations and turn them to one\'s advantage.',
                'level': 'B2',
                'category': 'Business',
                'examples': [
                    'He made an astute observation that changed the direction of the project.',
                    'An astute businesswoman, she spotted the opportunity immediately.'
                ],
                'collocations': ['astute observation', 'astute businessman', 'astute move'],
                'synonyms': ['shrewd', 'perceptive', 'acute', 'sharp-witted'],
                'antonyms': ['obtuse', 'dull-witted', 'naive'],
                'mastery': 1
            },
            {
                'word': 'axiomatic',
                'phonetic': '/ˌæk.si.əˈmæt.ɪk/',
                'pos': 'adjective',
                'definition': 'Self-evident or unquestionable; based on axioms.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'It is axiomatic that hard work is necessary for success.',
                    'The rules of the game are based on axiomatic principles.'
                ],
                'collocations': ['axiomatic truth', 'axiomatic principle'],
                'synonyms': ['self-evident', 'undeniable', 'incontrovertible', 'manifest'],
                'antonyms': ['questionable', 'unproven', 'dubious'],
                'mastery': 2
            },
            # B
            {
                'word': 'bespeak',
                'phonetic': '/bɪˈspiːk/',
                'pos': 'verb',
                'definition': 'To be evidence of; indicate or suggest.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'His carefully chosen words bespeak a profound understanding of the topic.',
                    'The elegant design bespeaks a commitment to quality.'
                ],
                'collocations': ['bespeak quality', 'bespeak confidence'],
                'synonyms': ['indicate', 'evidence', 'reveal', 'denote'],
                'antonyms': ['conceal', 'obscure', 'mask'],
                'mastery': 1
            },
            {
                'word': 'blase',
                'phonetic': '/blɑːˈzeɪ/',
                'pos': 'adjective',
                'definition': 'Unimpressed or indifferent to something because of overfamiliarity; unenthusiastic.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'He was blasé about the award, having won many before.',
                    'Her blasé attitude toward the crisis surprised everyone.'
                ],
                'collocations': ['blasé attitude', 'worldly and blasé'],
                'synonyms': ['indifferent', 'unimpressed', 'unconcerned', 'jaded'],
                'antonyms': ['impressed', 'excited', 'enthusiastic'],
                'mastery': 1
            },
            {
                'word': 'blithely',
                'phonetic': '/ˈblaɪð.li/',
                'pos': 'adverb',
                'definition': 'In a casual, carefree, or unconcerned manner, often ignoring important matters.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'She blithely ignored the warnings and proceeded with the plan.',
                    'He blithely spent money he didn\'t have.'
                ],
                'collocations': ['blithely ignore', 'blithely assume'],
                'synonyms': ['carelessly', 'nonchalantly', 'casually', 'unconcernedly'],
                'antonyms': ['seriously', 'earnestly', 'cautiously'],
                'mastery': 1
            },
            {
                'word': 'bloviating',
                'phonetic': '/ˈbloʊ.vi.eɪ.tɪŋ/',
                'pos': 'verb',
                'definition': 'To speak or write at length in a pretentious or pompous manner.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'The politician spent hours bloviating about his achievements.',
                    'He had a tendency to bloviate during meetings.'
                ],
                'collocations': ['bloviate about', 'bloviate at length'],
                'synonyms': ['rant', 'spew', 'spout', 'orate'],
                'antonyms': ['concise', 'brief', 'laconic'],
                'mastery': 1
            },
            # C
            {
                'word': 'canard',
                'phonetic': '/kəˈnɑːrd/',
                'pos': 'noun',
                'definition': 'A false or baseless rumor or story.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The report dismissed the canard that the company was about to declare bankruptcy.',
                    'The canard spread quickly on social media.'
                ],
                'collocations': ['dismiss a canard', 'canard about'],
                'synonyms': ['rumor', 'falsehood', 'fabrication', 'hoax'],
                'antonyms': ['truth', 'fact', 'reality'],
                'mastery': 1
            },
            {
                'word': 'casus belli',
                'phonetic': '/ˌkeɪ.səs ˈbel.i/',
                'pos': 'noun',
                'definition': 'An event or action that justifies or provokes a war or conflict.',
                'level': 'C2',
                'category': 'Academic',
                'examples': [
                    'The border dispute became the casus belli for the two nations.',
                    'They sought a casus belli to justify military intervention.'
                ],
                'collocations': ['provide a casus belli', 'constitute a casus belli'],
                'synonyms': ['justification', 'provocation', 'pretext'],
                'antonyms': ['peace', 'accord', 'truce'],
                'mastery': 1
            },
            {
                'word': 'churlish',
                'phonetic': '/ˈtʃɜːr.lɪʃ/',
                'pos': 'adjective',
                'definition': 'Rude in a mean-spirited and surly way; lacking civility.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'It would be churlish to refuse such a generous offer.',
                    'His churlish remarks alienated his colleagues.'
                ],
                'collocations': ['churlish behavior', 'churlish remark'],
                'synonyms': ['rude', 'surly', 'curt', 'discourteous'],
                'antonyms': ['polite', 'courteous', 'gracious', 'civil'],
                'mastery': 1
            },
            {
                'word': 'commoditize',
                'phonetic': '/kəˈmɒd.ɪ.taɪz/',
                'pos': 'verb',
                'definition': 'To turn a product or service into a generic commodity, often losing its distinctiveness.',
                'level': 'C1',
                'category': 'Business',
                'examples': [
                    'The company feared that competitors would commoditize their innovative product.',
                    'When luxury goods are commoditized, they lose their exclusive appeal.'
                ],
                'collocations': ['commoditize products', 'commoditize services'],
                'synonyms': ['standardize', 'mass-produce', 'commercialize'],
                'antonyms': ['differentiate', 'personalize', 'customize'],
                'mastery': 1
            },
            {
                'word': 'complaisant',
                'phonetic': '/kəmˈpleɪ.zənt/',
                'pos': 'adjective',
                'definition': 'Willing to please others; obliging and agreeable.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'She was complaisant and always agreed to help her friends.',
                    'His complaisant attitude made him popular with his boss.'
                ],
                'collocations': ['complaisant manner', 'complaisant nature'],
                'synonyms': ['obliging', 'accommodating', 'agreeable', 'deferential'],
                'antonyms': ['obstinate', 'stubborn', 'uncooperative'],
                'mastery': 1
            },
            {
                'word': 'corollary',
                'phonetic': '/kəˈrɒl.ə.ri/',
                'pos': 'noun',
                'definition': 'A direct or natural consequence or result.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'A corollary of the new law was increased tax revenue.',
                    'The idea of equality is a corollary of democratic principles.'
                ],
                'collocations': ['natural corollary', 'direct corollary', 'corollary to'],
                'synonyms': ['consequence', 'result', 'outcome', 'byproduct'],
                'antonyms': ['cause', 'premise', 'origin'],
                'mastery': 2
            },
            # D
            {
                'word': 'deplore',
                'phonetic': '/dɪˈplɔːr/',
                'pos': 'verb',
                'definition': 'To feel or express strong disapproval or condemnation.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'We deplore the violence that has occurred.',
                    'The statement deplores the use of child labor.'
                ],
                'collocations': ['deplore violence', 'deplore the situation'],
                'synonyms': ['condemn', 'lament', 'decry', 'denounce'],
                'antonyms': ['commend', 'praise', 'applaud', 'appreciate'],
                'mastery': 1
            },
            {
                'word': 'depredate',
                'phonetic': '/ˈdep.rə.deɪt/',
                'pos': 'verb',
                'definition': 'To plunder, pillage, or lay waste to.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'Invading armies depredated the countryside.',
                    'The locusts depredated the farmers\' crops.'
                ],
                'collocations': ['depredate the land'],
                'synonyms': ['plunder', 'pillage', 'ravage', 'devastate'],
                'antonyms': ['protect', 'preserve', 'conserve'],
                'mastery': 1
            },
            {
                'word': 'dilettante',
                'phonetic': '/ˌdɪl.ɪˈtæn.ti/',
                'pos': 'noun',
                'definition': 'A person who dabbles in a field of knowledge or art without serious commitment.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'He was a dilettante who dabbled in painting, music, and poetry.',
                    'She dismissed him as a dilettante with no real expertise.'
                ],
                'collocations': ['dilettante in', 'dilettante approach'],
                'synonyms': ['dabbler', 'amateur', 'non-professional'],
                'antonyms': ['expert', 'professional', 'specialist'],
                'mastery': 1
            },
            # E
            {
                'word': 'equability',
                'phonetic': '/ˌek.wəˈbɪl.ə.ti/',
                'pos': 'noun',
                'definition': 'The quality of being even-tempered, serene, and consistent.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'Her equability in the face of crises made her an excellent leader.',
                    'He was known for his equability and calm demeanor.'
                ],
                'collocations': ['equability of temper'],
                'synonyms': ['evenness', 'serenity', 'composure', 'constancy'],
                'antonyms': ['volatility', 'instability', 'irregularity'],
                'mastery': 1
            },
            {
                'word': 'expostulate',
                'phonetic': '/ɪkˈspɒs.tjə.leɪt/',
                'pos': 'verb',
                'definition': 'To argue, reason, or remonstrate earnestly, often with someone.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'She expostulated with him about the dangers of the plan.',
                    'The manager expostulated against the decision.'
                ],
                'collocations': ['expostulate about', 'expostulate with'],
                'synonyms': ['protest', 'remonstrate', 'reason', 'argue'],
                'antonyms': ['agree', 'concur', 'acquiesce'],
                'mastery': 1
            },
            {
                'word': 'extirpate',
                'phonetic': '/ˈek.stə.peɪt/',
                'pos': 'verb',
                'definition': 'To completely destroy or eradicate something.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'They aimed to extirpate corruption from the government.',
                    'The disease was finally extirpated through a global vaccination campaign.'
                ],
                'collocations': ['extirpate corruption', 'extirpate disease'],
                'synonyms': ['eradicate', 'exterminate', 'annihilate', 'abolish'],
                'antonyms': ['cultivate', 'foster', 'nurture'],
                'mastery': 1
            },
            {
                'word': 'edifying',
                'phonetic': '/ˈed.ɪ.faɪ.ɪŋ/',
                'pos': 'adjective',
                'definition': 'Instructive or enlightening in a way that improves the mind or character.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'It was an edifying experience that changed her perspective.',
                    'The documentary provided an edifying look at the culture.'
                ],
                'collocations': ['edifying experience', 'edifying lesson'],
                'synonyms': ['instructive', 'enlightening', 'educational', 'illuminating'],
                'antonyms': ['uninstructive', 'unenlightening', 'trivial'],
                'mastery': 1
            },
            # F
            {
                'word': 'facile',
                'phonetic': '/ˈfæs.aɪl/',
                'pos': 'adjective',
                'definition': 'Superficial, simplistic, or achieved with little effort but often lacking depth.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'He offered a facile explanation that failed to address the real issues.',
                    'The critic dismissed the novel as a facile attempt at literary fiction.'
                ],
                'collocations': ['facile explanation', 'facile answer'],
                'synonyms': ['superficial', 'glib', 'simplistic', 'shallow'],
                'antonyms': ['profound', 'insightful', 'thorough'],
                'mastery': 1
            },
            {
                'word': 'fait accompli',
                'phonetic': '/ˌfet əˈkɑːm.pli/',
                'pos': 'noun',
                'definition': 'Something that has already been done and is not open to debate or change.',
                'level': 'C2',
                'category': 'Academic',
                'examples': [
                    'The announcement was a fait accompli; no one had been consulted.',
                    'By the time we found out, the merger was already a fait accompli.'
                ],
                'collocations': ['present with a fait accompli'],
                'synonyms': ['done deal', 'irreversible fact'],
                'antonyms': ['negotiable', 'open to debate'],
                'mastery': 1
            },
            {
                'word': 'fatuous',
                'phonetic': '/ˈfætʃ.u.əs/',
                'pos': 'adjective',
                'definition': 'Silly and pointless; lacking intelligence or thought.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'The fatuous comments undermined the seriousness of the discussion.',
                    'He made a fatuous joke at an inappropriate moment.'
                ],
                'collocations': ['fatuous remark', 'fatuous idea'],
                'synonyms': ['foolish', 'inane', 'silly', 'vapid'],
                'antonyms': ['sensible', 'wise', 'intelligent', 'profound'],
                'mastery': 1
            },
            {
                'word': 'foibles',
                'phonetic': '/ˈfɔɪ.bəlz/',
                'pos': 'noun',
                'definition': 'Minor weaknesses or eccentricities in character.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'We all have our little foibles.',
                    'His foibles were tolerated because of his other qualities.'
                ],
                'collocations': ['human foibles', 'little foibles'],
                'synonyms': ['weakness', 'quirk', 'peculiarity', 'idiosyncrasy'],
                'antonyms': ['strength', 'virtue', 'asset'],
                'mastery': 1
            },
            {
                'word': 'fulminate',
                'phonetic': '/ˈfʊl.mɪ.neɪt/',
                'pos': 'verb',
                'definition': 'To loudly criticize or protest against something.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The editorial fulminated against government censorship.',
                    'He fulminated at the injustice of the decision.'
                ],
                'collocations': ['fulminate against', 'fulminate about'],
                'synonyms': ['thunder', 'rant', 'denounce', 'condemn'],
                'antonyms': ['praise', 'commend', 'applaud'],
                'mastery': 1
            },
            {
                'word': 'furtively',
                'phonetic': '/ˈfɜːr.tɪv.li/',
                'pos': 'adverb',
                'definition': 'In a secretive or stealthy manner, often to avoid detection.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'He furtively glanced around the room before opening the letter.',
                    'She furtively slipped the note into his pocket.'
                ],
                'collocations': ['furtively glance', 'furtively move'],
                'synonyms': ['surreptitiously', 'secretly', 'covertly', 'stealthily'],
                'antonyms': ['openly', 'overtly', 'publicly'],
                'mastery': 1
            },
            # H
            {
                'word': 'hausfrau',
                'phonetic': '/ˈhaʊs.fraʊ/',
                'pos': 'noun',
                'definition': 'A housewife (German origin), often implying traditional or conservative domesticity.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'She rejected the hausfrau role and pursued a demanding career.',
                    'The character was portrayed as a contented hausfrau.'
                ],
                'collocations': ['typical hausfrau'],
                'synonyms': ['housewife', 'homemaker', 'housekeeper'],
                'antonyms': ['career woman', 'professional'],
                'mastery': 1
            },
            {
                'word': 'huckstering',
                'phonetic': '/ˈhʌk.stər.ɪŋ/',
                'pos': 'noun',
                'definition': 'The practice of aggressively or deceptively selling or promoting something.',
                'level': 'C1',
                'category': 'Business',
                'examples': [
                    'The company\'s huckstering gave them a bad reputation.',
                    'He was accused of huckstering unnecessary products to vulnerable customers.'
                ],
                'collocations': ['huckstering tactics'],
                'synonyms': ['hawking', 'peddling', 'salesmanship', 'mercenary selling'],
                'antonyms': ['ethical sales', 'fair dealing'],
                'mastery': 1
            },
            # I
            {
                'word': 'improvident',
                'phonetic': '/ɪmˈprɒv.ɪ.dənt/',
                'pos': 'adjective',
                'definition': 'Lacking foresight or care for the future; wasteful or rash.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'His improvident spending left him deeply in debt.',
                    'The improvident decision to ignore climate warnings led to disaster.'
                ],
                'collocations': ['improvident spending', 'improvident decision'],
                'synonyms': ['wasteful', 'profligate', 'spendthrift', 'rash'],
                'antonyms': ['provident', 'prudent', 'frugal', 'careful'],
                'mastery': 1
            },
            {
                'word': 'imputation',
                'phonetic': '/ˌɪm.pjʊˈteɪ.ʃən/',
                'pos': 'noun',
                'definition': 'The act of attributing or ascribing something to someone, often something negative.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The imputation of dishonesty damaged her reputation.',
                    'The imputation that he was lazy was entirely unfair.'
                ],
                'collocations': ['imputation of', 'false imputation'],
                'synonyms': ['attribution', 'ascription', 'allegation', 'charge'],
                'antonyms': ['denial', 'exoneration', 'acquittal'],
                'mastery': 1
            },
            {
                'word': 'inanition',
                'phonetic': '/ˌɪn.əˈnɪʃ.ən/',
                'pos': 'noun',
                'definition': 'Emptiness or exhaustion, especially from lack of nourishment or energy.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The captives suffered from inanition after weeks without proper food.',
                    'His work was marked by intellectual inanition.'
                ],
                'collocations': ['inanition of'],
                'synonyms': ['exhaustion', 'emptiness', 'vacancy', 'depletion'],
                'antonyms': ['abundance', 'plenitude', 'vitality'],
                'mastery': 1
            },
            {
                'word': 'indissoluble',
                'phonetic': '/ˌɪn.dɪˈsɒl.jə.bəl/',
                'pos': 'adjective',
                'definition': 'Permanent, impossible to dissolve or break apart.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The bond between them was indissoluble.',
                    'Indissoluble ties connected the two families.'
                ],
                'collocations': ['indissoluble bond', 'indissoluble union'],
                'synonyms': ['indestructible', 'inseparable', 'permanent', 'eternal'],
                'antonyms': ['dissoluble', 'breakable', 'temporary'],
                'mastery': 1
            },
            {
                'word': 'inimitable',
                'phonetic': '/ɪˈnɪm.ɪ.tə.bəl/',
                'pos': 'adjective',
                'definition': 'So unique or exceptional that it cannot be imitated or copied.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'She had an inimitable style that set her apart.',
                    'His performance was inimitable and deeply moving.'
                ],
                'collocations': ['inimitable style', 'inimitable quality'],
                'synonyms': ['unique', 'unmatched', 'unequalled', 'peerless'],
                'antonyms': ['commonplace', 'mediocre', 'average'],
                'mastery': 2
            },
            # L
            {
                'word': 'lampoon',
                'phonetic': '/læmˈpuːn/',
                'pos': 'noun',
                'definition': 'A scathing, satirical public attack or mockery, often in writing.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'The magazine published a lampoon of the celebrity\'s life.',
                    'His political lampoons were both hilarious and biting.'
                ],
                'collocations': ['lampoon of', 'political lampoon'],
                'synonyms': ['satire', 'parody', 'mockery', 'caricature'],
                'antonyms': ['praise', 'homage', 'tribute'],
                'mastery': 1
            },
            {
                'word': 'lampshade',
                'phonetic': '/ˈlæmp.ʃeɪd/',
                'pos': 'noun',
                'definition': 'A cover for a lamp that diffuses or directs light, often used figuratively for concealment.',
                'level': 'B1',
                'category': 'Daily use',
                'examples': [
                    'She chose a colorful lampshade for her reading lamp.',
                    'The lampshade cast a warm glow over the room.'
                ],
                'collocations': ['lampshade on', 'lampshade style'],
                'synonyms': ['lamp cover', 'light shade'],
                'antonyms': [],
                'mastery': 1
            },
            # M
            {
                'word': 'monopsonies',
                'phonetic': '/məˈnɒp.sə.niz/',
                'pos': 'noun (plural)',
                'definition': 'Market conditions where there is only one buyer for many sellers.',
                'level': 'C1',
                'category': 'Business',
                'examples': [
                    'Monopsonies give buyers significant power over prices.',
                    'The labor market functioned as a series of monopsonies.'
                ],
                'collocations': ['monopsony power', 'monopsony market'],
                'synonyms': ['buyer\'s monopoly', 'single buyer market'],
                'antonyms': ['monopoly', 'seller\'s market'],
                'mastery': 1
            },
            {
                'word': 'mortification',
                'phonetic': '/ˌmɔːr.tɪ.fɪˈkeɪ.ʃən/',
                'pos': 'noun',
                'definition': 'A feeling of great embarrassment, shame, or humiliation.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'She flushed with mortification when she realized her mistake.',
                    'The mortification he felt was overwhelming.'
                ],
                'collocations': ['great mortification', 'feel mortification'],
                'synonyms': ['embarrassment', 'humiliation', 'shame', 'chagrin'],
                'antonyms': ['pride', 'dignity', 'honor'],
                'mastery': 1
            },
            # N
            {
                'word': 'navel-gazing',
                'phonetic': '/ˈneɪ.vəl ˌɡeɪ.zɪŋ/',
                'pos': 'noun',
                'definition': 'Excessive self-contemplation or introspection, often viewed as self-indulgent.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'The group\'s navel-gazing prevented them from taking meaningful action.',
                    'He was criticized for his navel-gazing memoirs.'
                ],
                'collocations': ['navel-gazing introspection'],
                'synonyms': ['self-absorbed', 'introspective', 'self-contemplating'],
                'antonyms': ['action-oriented', 'engaged'],
                'mastery': 1
            },
            {
                'word': 'nota bene',
                'phonetic': '/ˈnoʊ.tə ˈbeɪ.neɪ/',
                'pos': 'phrase',
                'definition': 'A Latin phrase meaning "note well," used to draw attention to important information.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'Nota bene: all submissions must be received by Friday.',
                    'The instructions included a nota bene about the formatting.'
                ],
                'collocations': ['nota bene:'],
                'synonyms': ['take note', 'attention', 'important'],
                'antonyms': [],
                'mastery': 1
            },
            # O
            {
                'word': 'obviate',
                'phonetic': '/ˈɒb.vi.eɪt/',
                'pos': 'verb',
                'definition': 'To remove a need for something; to make unnecessary.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The new software obviates the need for manual data entry.',
                    'Good planning can obviate many problems.'
                ],
                'collocations': ['obviate the need for'],
                'synonyms': ['preclude', 'avert', 'remove', 'prevent'],
                'antonyms': ['require', 'demand', 'necessitate'],
                'mastery': 1
            },
            {
                'word': 'omakase',
                'phonetic': '/oʊˈmɑː.kə.seɪ/',
                'pos': 'noun',
                'definition': 'A Japanese dining style where the chef selects and serves the dishes.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'They ordered the omakase menu and were delighted by the surprise courses.',
                    'The restaurant specializes in omakase sushi.'
                ],
                'collocations': ['omakase dinner', 'omakase experience'],
                'synonyms': ['chef\'s choice', 'tasting menu'],
                'antonyms': ['à la carte', 'set menu'],
                'mastery': 1
            },
            {
                'word': 'otiose',
                'phonetic': '/ˈəʊ.ti.əʊs/',
                'pos': 'adjective',
                'definition': 'Serving no practical purpose; useless or pointless.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'His otiose remarks wasted valuable time.',
                    'The committee\'s work was largely otiose.'
                ],
                'collocations': ['otiose remarks', 'otiose work'],
                'synonyms': ['useless', 'pointless', 'superfluous', 'futile'],
                'antonyms': ['useful', 'valuable', 'productive', 'practical'],
                'mastery': 1
            },
            # P
            {
                'word': 'panopticon',
                'phonetic': '/pænˈɒp.tɪ.kɒn/',
                'pos': 'noun',
                'definition': 'A prison design where all inmates can be observed from a single central point.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The panopticon model has been used to analyze surveillance in society.',
                    'The prison was designed as a panopticon.'
                ],
                'collocations': ['panopticon prison', 'panopticon design'],
                'synonyms': ['surveillance system', 'observatory'],
                'antonyms': ['private space', 'privacy'],
                'mastery': 1
            },
            {
                'word': 'perfunctorily',
                'phonetic': '/pəˈfʌŋk.tər.ɪ.li/',
                'pos': 'adverb',
                'definition': 'Carried out with minimal effort, interest, or enthusiasm; routinely.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'She perfunctorily checked the documents without reading them carefully.',
                    'He perfunctorily nodded, not really paying attention.'
                ],
                'collocations': ['perfunctorily check', 'perfunctorily perform'],
                'synonyms': ['cursorily', 'half-heartedly', 'mechanically', 'carelessly'],
                'antonyms': ['thoroughly', 'meticulously', 'diligently'],
                'mastery': 1
            },
            {
                'word': 'perforation',
                'phonetic': '/ˌpɜːr.fəˈreɪ.ʃən/',
                'pos': 'noun',
                'definition': 'A small hole or series of holes, often used to separate or tear.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'The perforations made it easy to tear the paper.',
                    'The stamp had a line of perforation.'
                ],
                'collocations': ['perforation holes', 'line of perforation'],
                'synonyms': ['puncture', 'hole', 'piercing'],
                'antonyms': ['solid', 'unbroken'],
                'mastery': 1
            },
            {
                'word': 'perspicuity',
                'phonetic': '/ˌpɜːr.spɪˈkjuː.ə.ti/',
                'pos': 'noun',
                'definition': 'The quality of being clear, lucid, and easily understood.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'Her writing was praised for its perspicuity and grace.',
                    'The lawyer argued with remarkable perspicuity.'
                ],
                'collocations': ['perspicuity of thought', 'perspicuity in writing'],
                'synonyms': ['clarity', 'lucidity', 'intelligibility', 'transparency'],
                'antonyms': ['obscurity', 'confusion', 'ambiguity'],
                'mastery': 1
            },
            {
                'word': 'piquant',
                'phonetic': '/ˈpiː.kənt/',
                'pos': 'adjective',
                'definition': 'Pleasantly pungent or sharp in taste or flavor; stimulating.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'The piquant sauce added perfect flavor to the dish.',
                    'The book contained piquant details that kept readers intrigued.'
                ],
                'collocations': ['piquant flavor', 'piquant details'],
                'synonyms': ['tangy', 'zesty', 'spicy', 'stimulating'],
                'antonyms': ['bland', 'flavorless', 'dull'],
                'mastery': 1
            },
            {
                'word': 'piteous',
                'phonetic': '/ˈpɪt.i.əs/',
                'pos': 'adjective',
                'definition': 'Deserving or arousing pity; pathetic or mournful.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'She let out a piteous cry for help.',
                    'The piteous scene brought tears to everyone\'s eyes.'
                ],
                'collocations': ['piteous cry', 'piteous sight'],
                'synonyms': ['pitiful', 'heartrending', 'woeful', 'lamentable'],
                'antonyms': ['cheerful', 'joyful', 'heartening'],
                'mastery': 1
            },
            {
                'word': 'polemics',
                'phonetic': '/pəˈlem.ɪks/',
                'pos': 'noun',
                'definition': 'The art or practice of engaging in disputation or controversial argument.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'His polemics on the subject alienated some readers.',
                    'The debate descended into polemics rather than constructive discussion.'
                ],
                'collocations': ['political polemics', 'engage in polemics'],
                'synonyms': ['argument', 'disputation', 'debate', 'controversy'],
                'antonyms': ['agreement', 'consensus', 'harmony'],
                'mastery': 1
            },
            {
                'word': 'portend',
                'phonetic': '/pɔːrˈtend/',
                'pos': 'verb',
                'definition': 'To serve as an omen or sign of a future event, often something ominous.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The dark clouds portended a coming storm.',
                    'The economic indicators portend a recession.'
                ],
                'collocations': ['portend danger', 'portend doom'],
                'synonyms': ['foreshadow', 'presage', 'augur', 'betoken'],
                'antonyms': ['prevent', 'avert', 'forestall'],
                'mastery': 1
            },
            {
                'word': 'prudence',
                'phonetic': '/ˈpruː.dəns/',
                'pos': 'noun',
                'definition': 'The quality of being cautious, wise, and careful in practical matters.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'Financial prudence requires careful planning.',
                    'She showed remarkable prudence in handling the crisis.'
                ],
                'collocations': ['financial prudence', 'show prudence'],
                'synonyms': ['caution', 'wisdom', 'foresight', 'judiciousness'],
                'antonyms': ['imprudence', 'recklessness', 'rashness'],
                'mastery': 1
            },
            {
                'word': 'pugnacious',
                'phonetic': '/pʌɡˈneɪ.ʃəs/',
                'pos': 'adjective',
                'definition': 'Combative, quarrelsome, or eager to fight.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'His pugnacious attitude made him difficult to work with.',
                    'The lawyer had a pugnacious style in the courtroom.'
                ],
                'collocations': ['pugnacious attitude', 'pugnacious style'],
                'synonyms': ['combative', 'belligerent', 'aggressive', 'quarrelsome'],
                'antonyms': ['peaceable', 'conciliatory', 'gentle'],
                'mastery': 1
            },
            # R
            {
                'word': 'rapacious',
                'phonetic': '/rəˈpeɪ.ʃəs/',
                'pos': 'adjective',
                'definition': 'Aggressively greedy or grasping, especially for money or power.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The rapacious landlord raised rents every year.',
                    'His rapacious business practices destroyed competitors.'
                ],
                'collocations': ['rapacious greed', 'rapacious behavior'],
                'synonyms': ['voracious', 'predatory', 'grasping', 'avaricious'],
                'antonyms': ['generous', 'altruistic', 'philanthropic'],
                'mastery': 1
            },
            {
                'word': 'redolent',
                'phonetic': '/ˈred.ə.lənt/',
                'pos': 'adjective',
                'definition': 'Strongly reminiscent or suggestive of something, or fragrant with an aroma.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'The room was redolent of fresh flowers.',
                    'His writing is redolent of classic literature.'
                ],
                'collocations': ['redolent of', 'redolent with'],
                'synonyms': ['reminiscent', 'suggestive', 'evocative', 'fragrant'],
                'antonyms': ['unreminiscent', 'odorless'],
                'mastery': 1
            },
            {
                'word': 'reproving',
                'phonetic': '/rɪˈpruː.vɪŋ/',
                'pos': 'adjective',
                'definition': 'Expressing criticism or disapproval, often gently.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'She gave him a reproving glance.',
                    'His reproving words made her reconsider her actions.'
                ],
                'collocations': ['reproving glance', 'reproving tone'],
                'synonyms': ['critical', 'disapproving', 'admonishing', 'reprimanding'],
                'antonyms': ['approving', 'commending', 'praising'],
                'mastery': 1
            },
            {
                'word': 'riposte',
                'phonetic': '/rɪˈpoʊst/',
                'pos': 'noun',
                'definition': 'A quick, sharp, and witty reply or retort.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'She was known for her clever ripostes.',
                    'His quick riposte left everyone laughing.'
                ],
                'collocations': ['quick riposte', 'clever riposte'],
                'synonyms': ['retort', 'rejoinder', 'comeback', 'wisecrack'],
                'antonyms': ['inaudible murmur', 'silence'],
                'mastery': 1
            },
            {
                'word': 'risibility',
                'phonetic': '/ˌrɪz.əˈbɪl.ə.ti/',
                'pos': 'noun',
                'definition': 'The tendency to laugh; being easily amused.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'Her risibility made her popular at parties.',
                    'The comedian capitalized on the audience\'s risibility.'
                ],
                'collocations': ['risibility of'],
                'synonyms': ['laughing', 'amusement', 'humor'],
                'antonyms': ['solemnity', 'gravity', 'seriousness'],
                'mastery': 1
            },
            # S
            {
                'word': 'sardonic',
                'phonetic': '/sɑːrˈdɒn.ɪk/',
                'pos': 'adjective',
                'definition': 'Grimly mocking or cynical, often with a hint of dark humor.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'He gave a sardonic smile at the suggestion.',
                    'Her sardonic wit kept the conversation lively.'
                ],
                'collocations': ['sardonic humor', 'sardonic smile'],
                'synonyms': ['cynical', 'satirical', 'mordant', 'ironic'],
                'antonyms': ['optimistic', 'hopeful', 'cheerful'],
                'mastery': 1
            },
            {
                'word': 'shoo-in',
                'phonetic': '/ˈʃuː.ɪn/',
                'pos': 'noun',
                'definition': 'A person or thing that is certain to succeed, win, or be elected.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'She is a shoo-in for the position.',
                    'The team was a shoo-in to win the championship.'
                ],
                'collocations': ['shoo-in for', 'shoo-in candidate'],
                'synonyms': ['sure bet', 'certainty', 'frontrunner'],
                'antonyms': ['underdog', 'long shot', 'dark horse'],
                'mastery': 1
            },
            {
                'word': 'singular',
                'phonetic': '/ˈsɪŋ.ɡjə.lər/',
                'pos': 'adjective',
                'definition': 'Exceptionally good, remarkable, or unusual.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'She has a singular talent for negotiation.',
                    'The painting was of singular beauty.'
                ],
                'collocations': ['singular beauty', 'singular talent'],
                'synonyms': ['remarkable', 'exceptional', 'extraordinary', 'uncommon'],
                'antonyms': ['ordinary', 'commonplace', 'unexceptional'],
                'mastery': 1
            },
            {
                'word': 'solipsistic',
                'phonetic': '/ˌsɒl.ɪpˈsɪs.tɪk/',
                'pos': 'adjective',
                'definition': 'Characterized by the belief that only one\'s own mind is certain to exist.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'His solipsistic philosophy left him isolated.',
                    'The protagonist\'s solipsistic worldview was challenged by events.'
                ],
                'collocations': ['solipsistic view', 'solipsistic philosophy'],
                'synonyms': ['egoistic', 'self-absorbed', 'narcissistic'],
                'antonyms': ['altruistic', 'empathetic', 'worldly'],
                'mastery': 1
            },
            {
                'word': 'syllogism',
                'phonetic': '/ˈsɪl.ə.dʒɪ.zəm/',
                'pos': 'noun',
                'definition': 'A logical argument using deductive reasoning, consisting of a major premise, minor premise, and conclusion.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'The syllogism "All men are mortal; Socrates is a man; therefore Socrates is mortal" is classic.',
                    'He constructed a logical syllogism to prove his point.'
                ],
                'collocations': ['logical syllogism', 'construct a syllogism'],
                'synonyms': ['logical argument', 'deduction', 'inference'],
                'antonyms': ['fallacy', 'illogical argument'],
                'mastery': 1
            },
            # V
            {
                'word': 'vacillate',
                'phonetic': '/ˈvæs.ɪ.leɪt/',
                'pos': 'verb',
                'definition': 'To waver between different opinions or actions; be indecisive.',
                'level': 'C1',
                'category': 'Daily use',
                'examples': [
                    'He vacillated between taking the job and staying in school.',
                    'The government vacillated on the policy for months.'
                ],
                'collocations': ['vacillate between', 'vacillate on'],
                'synonyms': ['waver', 'hesitate', 'oscillate', 'dither'],
                'antonyms': ['decide', 'resolve', 'determine'],
                'mastery': 1
            },
            {
                'word': 'vicissitudes',
                'phonetic': '/vɪˈsɪs.ɪ.tjuːdz/',
                'pos': 'noun (plural)',
                'definition': 'Changes or fluctuations, especially in fortune or life circumstances.',
                'level': 'C1',
                'category': 'Academic',
                'examples': [
                    'Life is full of vicissitudes.',
                    'He weathered the vicissitudes of a long career.'
                ],
                'collocations': ['vicissitudes of life', 'vicissitudes of fortune'],
                'synonyms': ['fluctuations', 'changes', 'alterations', 'shifts'],
                'antonyms': ['stability', 'constancy', 'uniformity'],
                'mastery': 1
            },
            {
                'word': 'vim',
                'phonetic': '/vɪm/',
                'pos': 'noun',
                'definition': 'Energy, vitality, and enthusiasm.',
                'level': 'B2',
                'category': 'Daily use',
                'examples': [
                    'She approached the task with vim and vigor.',
                    'The young team played with vim and determination.'
                ],
                'collocations': ['vim and vigor', 'full of vim'],
                'synonyms': ['energy', 'vitality', 'vigor', 'enthusiasm'],
                'antonyms': ['lethargy', 'listlessness', 'apathy'],
                'mastery': 1
            }
        ]

        # ============================================
        # 3. SET WORD OF THE DAY
        # ============================================
        today = timezone.now().date()
        
        if words_data:
            # Pick a random word from the list
            random_word_data = random.choice(words_data)
            random_word_data['is_word_of_day'] = True
            random_word_data['word_of_day_date'] = today
            self.stdout.write(self.style.SUCCESS(f'✓ Setting "{random_word_data["word"]}" as Word of the Day for {today}'))

        # ============================================
        # 4. SEED THE DATABASE
        # ============================================
        created_count = 0
        
        for word_data in words_data:
            word = Word.objects.create(**word_data)
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created word: {word.word}'))

        # ============================================
        # 5. VERIFY DATABASE STATE
        # ============================================
        total_words = Word.objects.count()
        wotd_count = Word.objects.filter(is_word_of_day=True).count()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('SEED COMPLETE - SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'  📝 Total words in database: {total_words}')
        self.stdout.write(f'  ✨ Created: {created_count}')
        self.stdout.write(f'  📅 Word of the Day entries: {wotd_count}')
        
        if wotd_count == 0:
            self.stdout.write(self.style.ERROR('  ⚠️  WARNING: No Word of the Day set!'))
        elif wotd_count == 1:
            wotd_word = Word.objects.filter(is_word_of_day=True).first()
            self.stdout.write(self.style.SUCCESS(f'  ✅ Word of the Day: "{wotd_word.word}" for {wotd_word.word_of_day_date}'))
        else:
            self.stdout.write(self.style.ERROR(f'  ⚠️  ERROR: Multiple Word of the Day entries found ({wotd_count})!'))
            # Fix: Keep only the first one
            first_wotd = Word.objects.filter(is_word_of_day=True).first()
            Word.objects.filter(is_word_of_day=True).exclude(id=first_wotd.id).update(is_word_of_day=False, word_of_day_date=None)
            self.stdout.write(self.style.SUCCESS(f'  ✅ Fixed: Kept "{first_wotd.word}" as Word of the Day'))
        
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('✓ Seeding complete!'))