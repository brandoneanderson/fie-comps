import esprima
import re

"""Will parse through .js files using Esprima module and extract common malicious features"""

node_types = {}

def analyzeJS(script, extClass):
    # Attempt to read file
    try:
        with open(script, 'r', encoding='utf8') as file:
            # grab entire script and store it as string
            js_content = file.read()
            # parsed_content_ast = esprima.parseModule(js_content, {"jsx": True, 'tokens':True, 'range':True, 'loc':True})

            # List to store specific funtion calls we want
            function_calls = []
            
            # traverseAST(parsed_content_ast, js_content)

            # print("Parsed_cotent type = :", parsed_content_ast)
    
    # Throw appropriate errors if anything goes wrong while attempting to read file
    except FileNotFoundError:
        print(f"Error: The file {script} was not found.")
    except Exception as e:
        print(f"An error ocurred: {e}")

def traverseAST(ast):
    # for node in ast.tokens:
    #     if node.value == 'fetch':
    #         print("Fetch Node: ", node)
            # print("Range: ", node.range)
            # print("Tokens[range]: ", ast.tokens[node.range[0]:node.range[1]])
            return
            # parent = ast.tokens[node.range[0]:node.range[1]]
            # print("Token Parent[range]: ", ast.tokens[parent.range[0]:parent.range[1]])