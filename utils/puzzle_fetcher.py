import re
import requests
from bs4 import BeautifulSoup


def fetch() -> str:
    """
    Return today's puzzle grouped by side with groups separated by hyphens
    """
    response = requests.get("https://www.nytimes.com/puzzles/letter-boxed")
    soup = BeautifulSoup(response.text, "html.parser")
    scripts = soup.find_all("script")
    game_data_script = [
        script.text
        for script in scripts
        if script.text.startswith("window.gameData")
    ][0]
    
    search = '"sides":'
    sides_start = game_data_script.index(search) + len(search) + 1
    length = len('"ABC"') * 4 + len(",") * 3
    sides_data = game_data_script[
        sides_start : sides_start + length
    ]  # "UPO","XTS","EIL","NCY"
    puzzle = sides_data.replace('"', "").replace(",", "-")
    
    solution_data = re.findall(r'"ourSolution":\[.*?\]', game_data_script)
    # solution_data = game_data_script[
    #     solution_start : solution_start + length
    # ]
    solution = solution_data[0].replace('"ourSolution":', "").replace('"', "'")
    return puzzle, str.lower(solution)


if __name__ == "__main__":
    print(fetch())
