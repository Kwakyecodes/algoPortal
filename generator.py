# Import libraries
import requests 
import re
import url as U
import constants as keys
from bs4 import BeautifulSoup
from processor import process
from url import get_link


def get_code_lines(hmtl_article: str) -> list:
    '''Process complete html article and extract html lines containing the code'''
    code_lines = re.findall('<div class="line number.+ index.+ alt.+">.+</div>', hmtl_article)
    code_lines = code_lines[0].split('</div>')
    return code_lines


def extract_text(code_line: str) -> str:
    '''Extract actual text from html code lines'''
    code = ""
    collect = False
    for char in code_line:
        if char == '>':
            collect = True
            continue
        elif char == '<':
            collect = False
            continue
            
        if collect:
            code += char
    
    return code


def generate_code(url: str, programming_language: str):
    '''Get lines of code from url and return list of chunks of code''' 
    complete_article_html = U.get_data(url=url)
    soup = BeautifulSoup(complete_article_html, 'html.parser')
    
    # Get dictionary of languages and their appropriate indices
    languages = {}
    for ind, html_line in enumerate(soup.find_all('h2', class_='tabtitle')):
        lang = extract_text(f"{html_line}").lower()
        if lang in languages:
            languages[lang].append(ind)
        else:
            languages[lang] = [ind]
            
    # Get all codes into code_container
    code_container = soup.find_all("div", class_='code-container')
    
    # Check if there are any codes on that webpage
    if not code_container:
        return {"error": keys.NO_CODE}
    
    solutions = []
    
    if not programming_language or not languages:
        for i in range(len(code_container)):
            code_lines = get_code_lines(hmtl_article=f"{code_container[i]}")
            solution = ''
            for line in code_lines:
                if "class" in line:
                    code = extract_text(f"{line}")
                    solution += code + '\n'
                    
            solution = solution.replace("&lt;", "<") # Fix < bug
            solution = solution.replace("&gt;", ">") # Fix > bug
            solutions.append(solution)
            
        return solutions
            
    # python and python3 should should be considered as the same language 
    if "python" in languages and "python" in programming_language:
        programming_language = "python"
    elif "python3" in languages and "python" in programming_language:
        programming_language = "python3"
    
    # Check if programming_language is among the available langauges
    if programming_language not in languages:
        return {"error": f"{programming_language} implementation not found"} 
    
    # Get hmtl lines that contain the code text and extract the text into solutions
    solutions = []
    for i in languages[programming_language]:
        code_lines = get_code_lines(hmtl_article=f"{code_container[i]}")
        solution = ''
        for line in code_lines:
            if "class" in line:
                code = extract_text(f"{line}")
                solution += code + '\n'
                
        solution = solution.replace("&lt;", "<") # Fix < bug
        solution = solution.replace("&gt;", ">") # Fix > bug
        solutions.append(solution)
    
    return solutions 