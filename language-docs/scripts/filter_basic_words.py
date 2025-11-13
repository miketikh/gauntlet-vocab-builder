#!/usr/bin/env python3
"""
Filter out basic function words and elementary vocabulary from grade-level files.
Keep only substantive vocabulary worth recommending for learning.
"""

import json

# Comprehensive list of basic words to remove
BASIC_WORDS_TO_REMOVE = {
    # Articles & Determiners
    'the', 'a', 'an', 'this', 'that', 'these', 'those', 'some', 'any', 'all',
    'each', 'every', 'both', 'either', 'neither', 'much', 'many', 'more', 'most',

    # Pronouns
    'i', 'me', 'my', 'mine', 'myself', 'you', 'your', 'yours', 'yourself',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
    'it', 'its', 'itself', 'we', 'us', 'our', 'ours', 'ourselves',
    'they', 'them', 'their', 'theirs', 'themselves',
    'who', 'whom', 'whose', 'what', 'which', 'where', 'when', 'why', 'how',

    # Prepositions
    'in', 'on', 'at', 'to', 'from', 'by', 'with', 'about', 'for', 'of',
    'off', 'up', 'down', 'into', 'onto', 'over', 'under', 'through',
    'between', 'among', 'after', 'before', 'during', 'until', 'since',
    'above', 'below', 'across', 'along', 'around', 'behind', 'beside',
    'near', 'next', 'against', 'within', 'without', 'toward', 'towards',

    # Conjunctions
    'and', 'but', 'or', 'so', 'yet', 'for', 'nor', 'because', 'if',
    'when', 'while', 'although', 'though', 'unless', 'than', 'as',

    # Basic Verbs (too elementary)
    'be', 'am', 'is', 'are', 'was', 'were', 'been', 'being',
    'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'done',
    'go', 'goes', 'went', 'gone', 'going',
    'come', 'comes', 'came', 'coming',
    'make', 'makes', 'made', 'making',
    'get', 'gets', 'got', 'gotten', 'getting',
    'take', 'takes', 'took', 'taken', 'taking',
    'give', 'gives', 'gave', 'given', 'giving',
    'know', 'knows', 'knew', 'known', 'knowing',
    'see', 'sees', 'saw', 'seen', 'seeing',
    'look', 'looks', 'looked', 'looking',
    'think', 'thinks', 'thought', 'thinking',
    'want', 'wants', 'wanted', 'wanting',
    'use', 'uses', 'used', 'using',
    'find', 'finds', 'found', 'finding',
    'tell', 'tells', 'told', 'telling',
    'ask', 'asks', 'asked', 'asking',
    'work', 'works', 'worked', 'working',
    'seem', 'seems', 'seemed', 'seeming',
    'feel', 'feels', 'felt', 'feeling',
    'try', 'tries', 'tried', 'trying',
    'leave', 'leaves', 'left', 'leaving',
    'call', 'calls', 'called', 'calling',
    'keep', 'keeps', 'kept', 'keeping',
    'put', 'puts', 'putting',
    'let', 'lets', 'letting',
    'say', 'says', 'said', 'saying',
    'need', 'needs', 'needed', 'needing',
    'help', 'helps', 'helped', 'helping',
    'show', 'shows', 'showed', 'shown', 'showing',
    'hear', 'hears', 'heard', 'hearing',
    'play', 'plays', 'played', 'playing',
    'run', 'runs', 'ran', 'running',
    'move', 'moves', 'moved', 'moving',
    'live', 'lives', 'lived', 'living',
    'bring', 'brings', 'brought', 'bringing',
    'sit', 'sits', 'sat', 'sitting',
    'stand', 'stands', 'stood', 'standing',
    'turn', 'turns', 'turned', 'turning',
    'start', 'starts', 'started', 'starting',
    'stop', 'stops', 'stopped', 'stopping',
    'follow', 'follows', 'followed', 'following',
    'stay', 'stays', 'stayed', 'staying',
    'talk', 'talks', 'talked', 'talking',
    'speak', 'speaks', 'spoke', 'spoken', 'speaking',
    'write', 'writes', 'wrote', 'written', 'writing',
    'read', 'reads', 'reading',
    'walk', 'walks', 'walked', 'walking',
    'watch', 'watches', 'watched', 'watching',
    'wait', 'waits', 'waited', 'waiting',
    'change', 'changes', 'changed', 'changing',
    'open', 'opens', 'opened', 'opening',
    'close', 'closes', 'closed', 'closing',
    'begin', 'begins', 'began', 'begun', 'beginning',
    'end', 'ends', 'ended', 'ending',
    'win', 'wins', 'won', 'winning',
    'lose', 'loses', 'lost', 'losing',
    'pay', 'pays', 'paid', 'paying',
    'meet', 'meets', 'met', 'meeting',
    'cut', 'cuts', 'cutting',
    'fall', 'falls', 'fell', 'fallen', 'falling',
    'eat', 'eats', 'ate', 'eaten', 'eating',
    'drink', 'drinks', 'drank', 'drunk', 'drinking',
    'sleep', 'sleeps', 'slept', 'sleeping',
    'buy', 'buys', 'bought', 'buying',
    'sell', 'sells', 'sold', 'selling',
    'send', 'sends', 'sent', 'sending',
    'wear', 'wears', 'wore', 'worn', 'wearing',
    'die', 'dies', 'died', 'dying',
    'happen', 'happens', 'happened', 'happening',

    # Basic Adjectives
    'good', 'bad', 'big', 'small', 'little', 'large', 'great',
    'new', 'old', 'young', 'long', 'short', 'tall', 'high', 'low',
    'hot', 'cold', 'warm', 'cool', 'right', 'wrong', 'true', 'false',
    'same', 'different', 'next', 'last', 'first', 'second', 'third',
    'other', 'another', 'such', 'own', 'few', 'several', 'whole',
    'sure', 'able', 'ready', 'early', 'late', 'easy', 'hard',
    'happy', 'sad', 'nice', 'kind', 'mean', 'best', 'better', 'worse', 'worst',
    'full', 'empty', 'clean', 'dirty', 'dark', 'light', 'heavy',
    'free', 'busy', 'clear', 'close', 'open', 'safe', 'sorry',
    'fine', 'okay', 'simple', 'real', 'quick', 'slow', 'fast',
    'red', 'blue', 'green', 'white', 'black', 'brown', 'yellow',

    # Basic Adverbs
    'very', 'really', 'quite', 'too', 'so', 'just', 'only', 'also',
    'even', 'still', 'already', 'yet', 'always', 'never', 'often',
    'sometimes', 'usually', 'here', 'there', 'now', 'then', 'soon',
    'again', 'once', 'well', 'back', 'together', 'away', 'far',
    'however', 'perhaps', 'maybe', 'almost', 'enough', 'less',

    # Numbers & Basic Time
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'first', 'second', 'third', 'fourth', 'fifth',
    'day', 'week', 'month', 'year', 'time', 'hour', 'minute',
    'today', 'tomorrow', 'yesterday', 'morning', 'night', 'evening', 'afternoon',

    # Basic Nouns (too elementary)
    'yes', 'no', 'ok', 'okay', 'please', 'thank', 'thanks', 'sorry',
    'hello', 'hi', 'hey', 'goodbye', 'bye',
    'thing', 'things', 'way', 'ways', 'place', 'places',
    'man', 'men', 'woman', 'women', 'person', 'people',
    'child', 'children', 'boy', 'boys', 'girl', 'girls',
    'eye', 'eyes', 'hand', 'hands', 'face', 'head', 'body',
    'life', 'world', 'house', 'home', 'room', 'door', 'window',
    'car', 'road', 'street', 'city', 'town', 'country',
    'water', 'food', 'air', 'fire', 'tree', 'dog', 'cat',
    'book', 'paper', 'pen', 'table', 'chair', 'bed',
    'school', 'class', 'teacher', 'student',
    'friend', 'family', 'mother', 'father', 'mom', 'dad',
    'name', 'word', 'number', 'part', 'side', 'top', 'bottom',
    'problem', 'question', 'answer', 'idea',

    # Auxiliary/Modal verbs
    'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must',

    # Common contractions/informal
    "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "couldn't",
    "shouldn't", "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
    "hadn't", "i'm", "you're", "he's", "she's", "it's", "we're", "they're",
}

def is_substantive_word(word):
    """
    Determine if a word is substantive (worth learning).
    Returns True if word should be kept, False if it should be removed.
    """
    word_lower = word.lower()

    # Remove if in basic words list
    if word_lower in BASIC_WORDS_TO_REMOVE:
        return False

    # Remove very short words (likely function words)
    if len(word_lower) <= 2:
        return False

    # Keep the word
    return True

def filter_grade_file(grade):
    """Filter a single grade file and return statistics."""
    filepath = f"../final/grade-{grade}.json"

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_count = len(data['words'])

    # Filter words
    filtered_words = [
        word_entry for word_entry in data['words']
        if is_substantive_word(word_entry['word'])
    ]

    # Update data
    data['words'] = filtered_words
    data['metadata']['total_words'] = len(filtered_words)

    # Save back
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    removed_count = original_count - len(filtered_words)

    return {
        'grade': grade,
        'original': original_count,
        'kept': len(filtered_words),
        'removed': removed_count,
        'removal_pct': (removed_count / original_count * 100) if original_count > 0 else 0
    }

def main():
    """Filter all grade files."""
    print("Filtering basic/function words from vocabulary lists...\n")
    print("=" * 70)

    results = []
    total_original = 0
    total_kept = 0
    total_removed = 0

    for grade in range(6, 13):
        result = filter_grade_file(grade)
        results.append(result)

        total_original += result['original']
        total_kept += result['kept']
        total_removed += result['removed']

        print(f"Grade {grade:2d}: {result['original']:4d} → {result['kept']:4d} words "
              f"({result['removed']:4d} removed, {result['removal_pct']:5.1f}%)")

    print("=" * 70)
    print(f"TOTAL:     {total_original:4d} → {total_kept:4d} words "
          f"({total_removed:4d} removed, {total_removed/total_original*100:5.1f}%)")
    print("\n✓ Filtering complete!")
    print("\nRemaining words are substantive vocabulary worth recommending.")

    # Warnings
    low_count_grades = [r for r in results if r['kept'] < 100]
    if low_count_grades:
        print("\n⚠️  Warning: These grades have fewer than 100 words:")
        for r in low_count_grades:
            print(f"   Grade {r['grade']}: {r['kept']} words")
        print("   Consider adding more advanced vocabulary from full AWL or other sources.")

if __name__ == "__main__":
    main()
