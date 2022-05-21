"""
My version of NYT's LetterBoxed puzzle solver.

This essentially borrows all of its functionality from three existing projects and combines their best features. The three projects are:

* https://calebrob.com/algorithms/2019/01/15/nytimes-letter-boxed.html
* https://github.com/dcbriccetti/letter-boxed-game-solver
* https://github.com/pmclaugh/LetterBoxedNYT
"""


from ast import Num
import sys


# The Trie data structure which'll hold our dictionary of valid words.
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
        # implementation, only the existence of this special key
        # matters. not the associated value.
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
        self.all_valid_words = self.find_all_words()
        self.words_by_1st_letter = self.map_valid_words()
    
    def find_all_words(
            self,
            starting_with:str = None,
            current_side_idx: int = 0) -> list[str]:
        if starting_with == None:
            valid_words = []
            for first_side_idx in range(len(self.sides)):
                for first_letter in self.sides[first_side_idx]:
                    valid_words += self.find_all_words(
                            first_letter,
                            first_side_idx)
            return valid_words
        else:
            valid_words = []
            for next_side_idx in range(len(self.sides)):
                if next_side_idx != current_side_idx:
                    for letter in self.sides[next_side_idx]:
                        candidate = starting_with + letter
                        query_result = self.dictionary.query(candidate)
                        if query_result == -1:
                            continue
                        if query_result == 1:
                            valid_words.append(candidate)
                        valid_words += self.find_all_words(
                                candidate, 
                                next_side_idx)
            return valid_words

    def map_valid_words(self) -> dict:
        valid_words_map = {}
        for l in self.all_letters:
            valid_words_map[l] = list(filter(
                    lambda x: x[0] == l, 
                    self.all_valid_words.copy()))
        return valid_words_map

    def find_solutions(
            self,
            max_length: int = 10,
            candidate:list[str] = None,
            used_letters:set[str] = None) -> list[list[str]]:
        # Initial word (head of recursion stack):
        if candidate == None:
            solutions = []
            for w in self.all_valid_words:
                solutions += self.find_solutions(
                        max_length,
                        [w],
                        set(w))
            return solutions
        # Recursive call:
        else:
            # termination criteria
            if len(used_letters) == self.num_letters:
                # print(f"Found solution: {candidate}")
                return [candidate]
            elif len(candidate) == max_length:
                return []
            
            # last letter of the last word
            next_letter = candidate[-1][-1]
            solution = []
            for next_word in self.words_by_1st_letter[next_letter]:
                new_letters = set(next_word) - used_letters
                if new_letters:
                    solution += self.find_solutions(
                        max_length,
                        candidate + [next_word], 
                        used_letters | new_letters)
            return solution


def main(*args, **kwargs):
    pass

if __name__ == '__main__':
    # # Parse command line arguments and invoke main() accordingly
    # main(sys.argv[1], # foo
    #         sys.argv[2], # bar
    #         **dict(arg.split('=') for arg in sys.argv[3:])) # kwargs
    pass

# First, we create our dictionary of all valid words.
f = open('dict_M.txt', 'r')
words = f.read().strip().split('\n')
words = [word.lower() for word in words if len(word)>2]
f.close()

dictionary = Trie(words)
puzzle = Puzzle(dictionary, 'mrf-sna-opu-gci')
max_soln_length = 2

all_solutions = puzzle.find_solutions(max_soln_length)
print(f"Found {len(all_solutions)} solutions of length {max_soln_length} or less.")