"""
My version of NYT's LetterBoxed puzzle solver.

This essentially borrows all of its functionality from three existing projects and combines their best features. The three projects are:

* https://calebrob.com/algorithms/2019/01/15/nytimes-letter-boxed.html
* https://github.com/dcbriccetti/letter-boxed-game-solver
* https://github.com/pmclaugh/LetterBoxedNYT
"""


from ast import Num
import sys

# The Trie data structure which'll hold our dictionaryof valid words.
class Trie(object):
    
    def __init__(self, words: list[str] = None) -> None:
        self.trie = dict()
        if words is not None:
            for word in words:
                self.add(word)

    def add(self, word: str) -> None:
        current_node = self.trie
        for letter in word:
            if letter not in current_node:
                current_node[letter] = dict()
            current_node = current_node[letter]
        # Indicate that this node represents a valid word starting from
        # the root, by adding the 'valid_word' key. Note: In this
        # implementation, only the existence of the key matters, not the
        # associated value.
        current_node['valid_word'] = True   # Or whatever!

    """
    Search the trie for a specified word.

    The query method will return:
    * -1 if word is not in our wordlist and is not a prefix of any word in our wordlist
    * 0 if word is a prefix of some words in our wordlist
    * 1 if word is a word in our wordlist (and possibly a prefix to a longer word!)
    """
    def query(self, word: str) -> int:
        current_node = self.trie
        for letter in word:
            if letter not in current_node:
                return -1
            current_node = current_node[letter]
        else:
            if 'valid_word' in current_node:
                return 1
            else:
                return 0

# The Puzzle class which'll hold puzzle-specific data and methods.
class Puzzle(object):

    def __init__(
            self, 
            dictionary: Trie, 
            sides: str, 
            delim: str = '-') -> None:
        self.dictionary = dictionary
        self.sides = sides.lower().split(delim)
        self.all_letters = list(
            letter for side in self.sides for letter in side)
        self.num_letters = len(self.all_letters)
        self.all_valid_words = list()
        self.all_solutions = list()
    
    def find_all_words(
            self,
            starting_with:str = None,
            current_side_idx: int = 0) -> None:
        if starting_with == None:
            for first_side_idx in range(len(self.sides)):
                for first_letter in self.sides[first_side_idx]:
                    self.find_all_words(first_letter, first_side_idx)
        else:
            for next_side_idx in range(len(self.sides)):
                if next_side_idx != current_side_idx:
                    for letter in self.sides[next_side_idx]:
                        candidate = starting_with + letter
                        query_result = self.dictionary.query(candidate)
                        if query_result == -1:
                            continue
                        if query_result == 1:
                            self.all_valid_words.append(candidate)
                        self.find_all_words(candidate, next_side_idx)
   
    def find_all_solutions(
            self,
            max_length:int = 100,
            candidate:list[str] = None,
            letters_covered:set[str] = None) -> None:
        # Initial word (head of recursion stack):
        if candidate == None:
            for w in self.all_valid_words:
                print(f"Finding solutions starting with {w}...")
                self.find_all_solutions(max_length, [w], set(w))
        # Recursive call:
        else:
            for w in self.all_valid_words:
                if candidate[-1][-1] == w[0] and w not in candidate:
                    print(f"  {candidate} + {w}?")
                    new_letters = set()
                    for letter in w:
                        if letter not in letters_covered:
                            new_letters.add(letter)
                    if len(new_letters) != 0:
                        candidate.append(w)
                        letters_covered = letters_covered.union(new_letters)
                        if len(letters_covered) != self.num_letters:
                            if len(candidate) < max_length:
                                self.find_all_solutions(
                                    max_length,
                                    candidate, 
                                    letters_covered)
                            else:
                                print(f"  {candidate} abandoned. MAX LENGTH REACHED")
                                candidate.pop()
                                return
                        else:
                            self.all_solutions.append(candidate.copy())
                            print(f"FOUND ONE! Adding {candidate} to solutions!!!")

def main(*args, **kwargs):
    pass

if __name__ == '__main__':
    # # Parse command line arguments and invoke main() accordingly
    # main(sys.argv[1], # foo
    #         sys.argv[2], # bar
    #         **dict(arg.split('=') for arg in sys.argv[3:])) # kwargs
    pass




# First, we create our dictionary of all valid words.
f = open('words_small.txt', 'r')
words = f.read().strip().split('\n')
words = [word.lower() for word in words if len(word)>2]


dictionary = Trie(words)

# puzzle = Puzzle(dictionary, 'meo-TIB-LKR-ahc')
max_sol_length = 4
puzzle = Puzzle(dictionary, 'sma-ilp-tne-ocz')
puzzle.find_all_words()
puzzle.find_all_solutions(max_sol_length)
print(f"Found {len(puzzle.all_solutions)} solutions of length {max_sol_length} or less!")
pass