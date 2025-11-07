import string
import pandas as pd

VOWELS = ['a', 'e', 'i', 'o', 'u']

with open("words.txt", 'r') as file:
    RAW_WORDS = [line.strip('\n') for line in file.readlines()]

# Build position-specific letter frequencies
LETTERS = {letter: [0, 0, 0, 0, 0] for letter in string.ascii_lowercase}
for word in RAW_WORDS:
    for index, char in enumerate(word):
        LETTERS[char][index] += 1

# Build overall letter frequencies (for better scoring)
LETTER_FREQ = {letter: 0 for letter in string.ascii_lowercase}
for word in RAW_WORDS:
    for char in word:
        LETTER_FREQ[char] += 1

WORDS = {}
for word in RAW_WORDS:
    # Use set for O(1) duplicate detection instead of O(n) count()
    unique_chars = set(word)
    contains_multiple = len(unique_chars) < len(word)
    unique_letter_count = len(unique_chars)

    green_score = 0
    yellow_score = 0
    position_score = 0
    frequency_score = 0
    vow = 0

    # Track which letters we've already scored (for unique letter bonus)
    seen_chars = set()

    for index, char in enumerate(word):
        # Position-based scoring
        char_position_freq = LETTERS[char][index]
        max_position_freq = max(LETTERS[char])

        if char_position_freq == max_position_freq:
            green_score += char_position_freq
        else:
            yellow_score += char_position_freq

        position_score += char_position_freq

        # Only count frequency once per unique letter (avoid duplicate letter penalty)
        if char not in seen_chars:
            frequency_score += LETTER_FREQ[char]
            seen_chars.add(char)

        if char in VOWELS:
            vow += 1

    # Calculate a comprehensive total score
    # Prioritize: unique letters > position frequency > letter frequency
    total_score = (
        unique_letter_count * 1000 +  # Strong preference for unique letters
        position_score * 2 +            # Position frequency matters
        frequency_score +                # Overall letter frequency
        vow * 50                         # Slight vowel bonus
    )

    # Penalty for duplicate letters
    if contains_multiple:
        total_score -= 500

    WORDS[word] = {
        "Contains Multiple?": contains_multiple,
        "Unique Letters": unique_letter_count,
        "Vowels": vow,
        "Green Score": green_score,
        "Yellow Score": yellow_score,
        "Position Score": position_score,
        "Frequency Score": frequency_score,
        "Total Score": total_score
    }

# Create DataFrame and sort by total score
df = pd.DataFrame.from_dict(WORDS, orient='index')
df.index.name = "Word"
df = df.sort_values('Total Score', ascending=False)

# Display top 20 words
print("\n" + "="*80)
print("TOP 20 WORDLE STARTING WORDS")
print("="*80)
print(df.head(20).to_string())
print("\n" + "="*80)
print(f"\nBest starting word: {df.index[0]}")
print(f"Total Score: {df.iloc[0]['Total Score']:.0f}")
print(f"Unique Letters: {df.iloc[0]['Unique Letters']}")
print(f"Position Score: {df.iloc[0]['Position Score']}")
print("="*80 + "\n")

# Save full results to CSV
df.to_csv("words.csv")
