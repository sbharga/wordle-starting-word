"""
Wordle Starting Word Analyzer
Analyzes word list to find the best starting word for Wordle using multiple metrics.
"""

import string
import pandas as pd
from math import log2
from collections import Counter

# Constants
VOWELS = set('aeiou')
CONSONANTS = set(string.ascii_lowercase) - VOWELS


class WordListAnalyzer:
    """Analyzes a word list and computes various frequency statistics."""

    def __init__(self, words):
        self.words = words
        self.position_freq = self._calculate_position_frequencies()
        self.letter_freq = self._calculate_letter_frequencies()
        self.letter_pair_freq = self._calculate_letter_pair_frequencies()
        self.total_words = len(words)

    def _calculate_position_frequencies(self):
        """Calculate how often each letter appears at each position."""
        freq = {letter: [0, 0, 0, 0, 0] for letter in string.ascii_lowercase}
        for word in self.words:
            for index, char in enumerate(word):
                freq[char][index] += 1
        return freq

    def _calculate_letter_frequencies(self):
        """Calculate overall frequency of each letter."""
        freq = {letter: 0 for letter in string.ascii_lowercase}
        for word in self.words:
            for char in word:
                freq[char] += 1
        return freq

    def _calculate_letter_pair_frequencies(self):
        """Calculate frequency of consecutive letter pairs."""
        freq = Counter()
        for word in self.words:
            for i in range(len(word) - 1):
                pair = word[i:i+2]
                freq[pair] += 1
        return freq


class WordScorer:
    """Scores individual words using various metrics."""

    def __init__(self, analyzer):
        self.analyzer = analyzer

    def score_word(self, word):
        """Calculate all metrics for a given word."""
        metrics = {}

        # Basic properties
        unique_chars = set(word)
        metrics['unique_letters'] = len(unique_chars)
        metrics['contains_multiple'] = len(unique_chars) < len(word)
        metrics['vowel_count'] = sum(1 for char in word if char in VOWELS)
        metrics['consonant_count'] = 5 - metrics['vowel_count']

        # Position-based scoring
        green_score, yellow_score, position_score = self._calculate_position_scores(word)
        metrics['green_score'] = green_score
        metrics['yellow_score'] = yellow_score
        metrics['position_score'] = position_score

        # Frequency-based scoring
        metrics['frequency_score'] = self._calculate_frequency_score(word, unique_chars)

        # Advanced metrics
        metrics['entropy_score'] = self._calculate_entropy_score(word)
        metrics['positional_uniqueness'] = self._calculate_positional_uniqueness(word)
        metrics['letter_pair_score'] = self._calculate_letter_pair_score(word)
        metrics['consonant_clustering'] = self._calculate_consonant_clustering(word)
        metrics['letter_diversity'] = self._calculate_letter_diversity(word)

        # Calculate total score
        metrics['total_score'] = self._calculate_total_score(metrics)

        return metrics

    def _calculate_position_scores(self, word):
        """Calculate green, yellow, and total position scores."""
        green_score = 0
        yellow_score = 0
        position_score = 0

        for index, char in enumerate(word):
            char_position_freq = self.analyzer.position_freq[char][index]
            max_position_freq = max(self.analyzer.position_freq[char])

            if char_position_freq == max_position_freq:
                green_score += char_position_freq
            else:
                yellow_score += char_position_freq

            position_score += char_position_freq

        return green_score, yellow_score, position_score

    def _calculate_frequency_score(self, word, unique_chars):
        """Calculate score based on overall letter frequency (count each unique letter once)."""
        return sum(self.analyzer.letter_freq[char] for char in unique_chars)

    def _calculate_entropy_score(self, word):
        """
        Calculate information entropy - measures how much information each letter provides.
        Higher entropy = more information gained per letter.
        """
        entropy = 0
        for index, char in enumerate(word):
            char_freq = self.analyzer.position_freq[char][index]
            if char_freq > 0:
                probability = char_freq / self.analyzer.total_words
                entropy -= probability * log2(probability)
        return entropy * 1000  # Scale for readability

    def _calculate_positional_uniqueness(self, word):
        """
        Measure how rare each letter is in its specific position.
        Lower frequency = more unique/valuable position.
        """
        uniqueness = 0
        for index, char in enumerate(word):
            # Inverse of frequency = uniqueness
            char_freq = self.analyzer.position_freq[char][index]
            if char_freq > 0:
                uniqueness += (self.analyzer.total_words - char_freq)
        return uniqueness

    def _calculate_letter_pair_score(self, word):
        """Score based on common letter pairs (bigrams)."""
        score = 0
        for i in range(len(word) - 1):
            pair = word[i:i+2]
            score += self.analyzer.letter_pair_freq.get(pair, 0)
        return score

    def _calculate_consonant_clustering(self, word):
        """
        Analyze consonant clustering. Words with too many consecutive consonants
        are less typical in English and may be less optimal.
        Returns penalty (higher = worse clustering).
        """
        max_cluster = 0
        current_cluster = 0

        for char in word:
            if char in CONSONANTS:
                current_cluster += 1
                max_cluster = max(max_cluster, current_cluster)
            else:
                current_cluster = 0

        # Penalty: 0 for clusters ≤2, increasing for larger clusters
        if max_cluster <= 2:
            return 0
        else:
            return (max_cluster - 2) * 100

    def _calculate_letter_diversity(self, word):
        """
        Measure how spread out the letters are in the alphabet.
        More diverse = better coverage of potential letters.
        """
        if len(word) == 0:
            return 0

        unique_chars = sorted(set(word))
        if len(unique_chars) == 1:
            return 0

        # Calculate average distance between consecutive unique letters in alphabet
        total_distance = 0
        for i in range(len(unique_chars) - 1):
            distance = ord(unique_chars[i+1]) - ord(unique_chars[i])
            total_distance += distance

        avg_distance = total_distance / (len(unique_chars) - 1)
        return avg_distance * 100  # Scale for readability

    def _calculate_total_score(self, metrics):
        """
        Calculate comprehensive total score using weighted combination of all metrics.
        Weights are tuned based on what makes a good Wordle starting word.
        """
        score = (
            metrics['unique_letters'] * 1500 +        # Most important: unique letters
            metrics['position_score'] * 2 +            # Position frequency matters
            metrics['frequency_score'] * 1 +           # Overall letter frequency
            metrics['vowel_count'] * 100 +             # Vowels are important
            metrics['entropy_score'] * 5 +             # Information value
            metrics['letter_pair_score'] * 0.5 +       # Common pairs bonus
            metrics['letter_diversity'] * 2 +          # Alphabet coverage
            metrics['positional_uniqueness'] * 0.1 -   # Uniqueness bonus
            metrics['consonant_clustering']            # Clustering penalty
        )

        # Strong penalty for duplicate letters
        if metrics['contains_multiple']:
            score -= 800

        return score


def load_words(filename='words.txt'):
    """Load words from file."""
    with open(filename, 'r') as file:
        return [line.strip('\n') for line in file.readlines()]


def analyze_words(words):
    """Analyze all words and return scored results."""
    analyzer = WordListAnalyzer(words)
    scorer = WordScorer(analyzer)

    results = {}
    for word in words:
        results[word] = scorer.score_word(word)

    return results


def display_results(df, top_n=20):
    """Display formatted results."""
    print("\n" + "="*100)
    print(f"TOP {top_n} WORDLE STARTING WORDS")
    print("="*100)

    # Select columns to display
    display_cols = [
        'total_score', 'unique_letters', 'vowel_count',
        'position_score', 'entropy_score', 'letter_pair_score',
        'letter_diversity', 'consonant_clustering', 'contains_multiple'
    ]

    print(df[display_cols].head(top_n).to_string())

    print("\n" + "="*100)
    print(f"\n🎯 BEST STARTING WORD: {df.index[0].upper()}")
    print(f"   Total Score: {df.iloc[0]['total_score']:.0f}")
    print(f"   Unique Letters: {df.iloc[0]['unique_letters']}")
    print(f"   Vowels: {df.iloc[0]['vowel_count']}")
    print(f"   Position Score: {df.iloc[0]['position_score']:.0f}")
    print(f"   Entropy Score: {df.iloc[0]['entropy_score']:.2f}")
    print(f"   Letter Diversity: {df.iloc[0]['letter_diversity']:.2f}")
    print("="*100 + "\n")


def main():
    """Main execution flow."""
    # Load and analyze words
    print("Loading words...")
    words = load_words()
    print(f"Loaded {len(words)} words")

    print("Analyzing words...")
    results = analyze_words(words)

    # Create DataFrame
    df = pd.DataFrame.from_dict(results, orient='index')
    df.index.name = "word"

    # Sort by total score
    df = df.sort_values('total_score', ascending=False)

    # Display results
    display_results(df)

    # Save to CSV
    print("Saving results to words.csv...")
    df.to_csv("words.csv")
    print("Done!")


if __name__ == "__main__":
    main()
