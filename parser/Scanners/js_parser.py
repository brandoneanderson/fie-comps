import esprima
# import re
from pathlib import Path
import jsbeautifier


def analyzeJS(script, extClass):
    try:
        beautified_file = beautify_file(script, extClass)
        ast = parseScript(beautified_file)
        if ast != None:
            traverseAST(ast, extClass)
        return


    except FileNotFoundError:
        print(f"Error: The file {script} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def beautify_file(script, extClass):
        # Set jsbeautifier modifiers to default settings
        opts = jsbeautifier.default_options()
       
        # Find Extensions root file path
        folderPath = script
        while folderPath.name != "Extensions":
            if folderPath.parent == folderPath:
                raise RuntimeError("Reached filesystem root without finding Extensions")
            folderPath = folderPath.parent


        # Grab root parent of script file (ex. MyBib() folder)
        extensions_path = Path(folderPath/extClass.folderpath)
        if not extensions_path.exists():
            raise FileNotFoundError("Extension root folder path not found")


        # Create beautified folder for easy viewing
        extensions_path_beautified_files = Path(extensions_path/"beautified")
        extensions_path_beautified_files.mkdir(parents=True, exist_ok=True)


        # Create beautified file
        script_beauty = script.with_name(script.stem + "_beautified.js")
        output_path = Path(extensions_path_beautified_files/script_beauty.name)


        # If beautified file exists, just return
        if output_path.exists():
            return output_path


        # Call beautified method
        beautified = jsbeautifier.beautify_file(script, opts)


        # Write output into file and store in Beautified folder
        with open(output_path, "w", encoding="utf8") as out:
            out.write(beautified)


        print(f"[+] Beautified JS saved to {output_path}")


        return output_path


def parseScript(script):
    # Esprima options to mark location of lines
    options = {"jsx": True,"tolerant":True, 'tokens':True, 'range':True, 'loc':True}
    # Attempt to read file
    try:
        with open(script, 'r', encoding='utf8') as file:
            # grab entire script and store it as string
            js_content = file.read()
            parsed_content_ast = esprima.parseModule(js_content, options)
            parsed_content_ast = esprima.parseScript(js_content, options)


            return parsed_content_ast
   
   
    # Throw appropriate errors if anything goes wrong while attempting to read file
    except FileNotFoundError:
        print(f"Error: The file {script} was not found.")
    except Exception as e:
        print(f"An error ocurred: {e}")


def traverseAST(ast, extClass):
    for branch in ast.body:
        traverseNode(branch, extClass)


def traverseNode(node, extClass):
    if node is None:
        return
   
    if node.type == "CallExpression":
        if node.callee.type == "Identifier":
            # eval runs a string of javascript code Big no no
            if node.callee.name == "eval" or "setTimeout" or "setInterval" or "new Function":
                extClass.js_features["dynamic_code_gen_functions"] += 1


    # Visit children
    for attr, value in node.__dict__.items():


        # Single child node
        if hasattr(value, 'type'):
            traverseNode(value, extClass)


        # List of child nodes
        elif isinstance(value, list):
            for item in value:
                if hasattr(item, 'type'):
                    traverseNode(item, extClass)
