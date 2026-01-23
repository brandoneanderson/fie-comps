import esprima
import re

"""Will parse through .js files using Esprima module and extract common malicious features"""

def analyzeJS(script, extClass):
    # Attempt to read file
    try:
        with open(script, 'r', encoding='utf8') as file:
            # grab entire script and store it as string
            js_content = file.read()
            parsed_content = esprima.parseModule(js_content, {"jsx": True, 'tokens':True})
            print("Parsed_cotent type = :", type(parsed_content.tokens))
            print("Parsed_content[0] type: ", parsed_content.tokens[0][0])
    
    # Throw appropriate errors if anything goes wrong while attempting to read file
    except FileNotFoundError:
        print(f"Error: The file {script} was not found.")
    except Exception as e:
        print(f"An error ocurred: {e}")