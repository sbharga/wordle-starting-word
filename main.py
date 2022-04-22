import string
import pandas as pd

VOWELS = ['a', 'e', 'i', 'o', 'u']

with open("words.txt", 'r') as file:
    RAW_WORDS = [line.strip('\n') for line in file.readlines()]

LETTERS = {}
for letter in string.ascii_lowercase:
    LETTERS[letter] = [0, 0, 0, 0, 0]

for word in RAW_WORDS:
    for index, char in enumerate(word):
        LETTERS[char][index] += 1

WORDS = {}
for word in RAW_WORDS:
    contains_multiple = False
    green_score = 0
    yellow_score = 0
    vow = 0
    for index, char in enumerate(word):
        if word.count(char) > 1:
            contains_multiple = True
        if LETTERS[char][index] == max(LETTERS[char]):
            green_score += LETTERS[char][index]
        else:
            yellow_score += LETTERS[char][index]
        if char in VOWELS:
            vow += 1
    WORDS[word] = {
		"Contains Multiple?": contains_multiple,
        "Vowels": vow,
        "Green Score": green_score,
        "Yellow Score": yellow_score
    }

df = pd.DataFrame.from_dict(WORDS, orient='index')
df.index.name = "Word"
df.to_csv("words.csv")
