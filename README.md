# Wordle-Starting-Word
 A simple python script to find the best wordle starting word.

# How it works
 There are 3 categories the words are rated on:
   - If it contains **multiple** of the same character.
   - The amount of **vowels**.
   - The number of **occurrences** where the character is **green/yellow** based on the words provided in `words.txt`.
<!--    -  -->
 Then it creates a new pandas dataframe with the data which is stored in the `words.csv` file where it can be sorted and rated.
