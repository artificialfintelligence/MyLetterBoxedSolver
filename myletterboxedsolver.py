"""
My version of NYT's LetterBoxed puzzle solver.

This essentially borrows all of its functionality from three existing projects and combines their best features. The three projects are:

* https://calebrob.com/algorithms/2019/01/15/nytimes-letter-boxed.html
* https://github.com/dcbriccetti/letter-boxed-game-solver
* https://github.com/pmclaugh/LetterBoxedNYT
"""


from utils import puzzle_fetcher
import sys
import re


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


def main(**kwargs):
    if '--len' in kwargs:
        try:
            max_soln_length = int(kwargs['--len'])
        except:
            print(f'Invalid maximum solution length: {kwargs["--len"]}')
            return
    else:
        max_soln_length = 2
    if max_soln_length > 9:
        print(f'Error: Maximum solution length must be less than 10.')
        return

    if '--dict' in kwargs:
        dict_file_path = kwargs['--dict']
    else:
        dict_file_path = 'resources/dict_S.txt'
    try:
        f = open(dict_file_path, 'r')
        words = f.read().strip().split('\n')
        words = [word.lower() for word in words if len(word)>2]
    except Exception as e:
        print(f'Failed to open dictionary file {dict_file_path}:\n {e}')
        return
    f.close()
    dictionary = Trie(words)

    if '--puzzle' in kwargs:
        puzzle_string = kwargs['--puzzle']
        if not bool(re.match('\A([a-z]+-)+[a-z]+$', puzzle_string)):
            print(f'Invalid puzzle string: {puzzle_string}')
            return
    else:
        try:
            puzzle_string = puzzle_fetcher.fetch()
        except:
            print(f'Failed to fetch today\'s puzzle from the NYT website.')
            return
    puzzle = Puzzle(dictionary, puzzle_string)

    print(f"\nFound {len(puzzle.all_valid_words)} valid words.")
    print(f"\nSolving {puzzle_string}...")
    all_solutions = puzzle.find_solutions(max_soln_length)
    print(f"\nFound {len(all_solutions)} solutions of length {max_soln_length} or less.")

    if '--output' in kwargs:
        output_file_path = kwargs['--output']
        try:
            f = open(output_file_path, 'w') 
        except Exception as e:
            print(f'Failed to open output file {output_file_path}:\n {e}')
            return
        print(f'\nWriting results to {output_file_path}...')
        for solution in all_solutions:
            f.write(f'{solution}\n')
        f.close()
    elif len(all_solutions) != 0:
        show_output = input('\nOutput file not specified. Output all solutions to the terminal? (y/N): ') or 'n'
        while show_output.lower() not in {'y', 'n'}:
            show_output = input('Output all solutions to the terminal? (y/N): ') or 'n'
        if show_output.lower() == 'y':
            for solution in all_solutions:
                    print(f'{solution}')

if __name__ == '__main__':
    # Parse command line arguments and invoke main() accordingly
    usage_guide = f'''
            Usage: myletterboxedsolver [--option <value>] 
            
            Where:
            
            --puzzle <abc-def-ghi-jkl>
            Solves the provided puzzle (must contain at least one
            hyphen). If ommitted, will attempt to retrieve today's
            puzzle from the NYT website.
            
            --len <M>
            Limits solutions to those with a maximum of M guesses.
            (Default = 2)
            
            --dict <path_to_dictionary_file>
            Uses the provided dictionary of valid words. (Note: Words
            shorter than 3 letters will be ignored). 
            (default = resources/dict_S.txt)

            --output <path_to_output_file>
            Writes solutions to the specified file. WARNING: If the file
            already exists, it will be over-written.
            (default: Do not output results)

            Example:
            myletterboxedsolver --puzzle abc-def-ghi --len 3 --dict words.txt
            '''
    args = sys.argv[1:]
    valid_options = ['puzzle', 'len', 'dict', 'output']
    valid_keys = list(map(lambda x: '--' + x, valid_options))
    values = args[1::2]
    keys = args[::2]
    if len(args) % 2 != 0:
        print(usage_guide)
    else:
        for key in keys:
            if key not in valid_keys:
                print(usage_guide)
                break
        else:
            main(**dict(zip(keys, values)))
    pass
