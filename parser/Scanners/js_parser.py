import esprima
import re
from pathlib import Path
import jsbeautifier
from math import log2

# Malicious JS infaltes the rate these characters appear
suspicious = set('%\\xu+=;{}()[]|^')

# Malicious JS inflate rate of these keywords
keywords = {"this", "if", "var"}

def analyzeJS(script, extClass):
    try:
        # beautify first (returns beautified path or creates one)
        beautified_file = beautify_file(script, extClass)

        # analyze the beautified file (fall back to original if beautify failed)
        if beautified_file is not None:
            target = beautified_file
        else:
            target = script

        # Extract all JS features from raw file no AST
        extractStringFeatures(target, extClass)

        # Grab AST of scripts using esprima
        ast = parseScript(target)

        # Traverse AST to extract AST-specific analysis features
        if ast is not None:
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

        # Just to see if it worked
        # print(f"[+] Beautified JS saved to {output_path}")


        return output_path

def parseScript(script):
    # Esprima options to mark location of lines
    options = {"jsx": True,"tolerant":True, 'tokens':True, 'range':True, 'loc':True}
    # Attempt to read file
    try:
        with open(script, 'r', encoding='utf-8', errors='ignore') as file:
            # grab entire script and store it as string
            js_content = file.read()
        try:
            parsed_content_ast = esprima.parseModule(js_content, options)
        except Exception:
            parsed_content_ast = esprima.parseScript(js_content, options)


        return parsed_content_ast
   
   
    # Throw appropriate errors if anything goes wrong while attempting to read file
    except FileNotFoundError:
        print(f"Error: The file {script} was not found.")
    except Exception as e:
        print(f"An error ocurred: {e}")

def traverseAST(ast, extClass):
    # Still don't get why I can't just iterate through it without this function
    for branch in ast.body:
        traverseNode(branch, extClass)

def traverseNode(node, extClass):
    # Edge Case
    if node is None:
        return
    
    # - - - - - AST TRAVERSAL FEATURE CAPTURING - - - - - - 

    # Dynamic Code Generation Functions
    if node.type == "CallExpression":
        if node.callee.type == "Identifier":
            # eval runs a string of javascript code Big no no
            if node.callee.name in {"eval", "setTimeout", "setInterval"}:
                extClass.js_features["dynamic_code_gen_functions"] += 1

    if node.type == "NewExpression":
        if node.callee.name == "Function":
            extClass.js_features["dynamic_code_gen_functions"] += 1

    # HTML DOM Change Methods and Properties
    if node.type == "MemberExpression":
        if node.property.name in {"innerHTML", "outerHTML", "write", "appendChild", "insertAdjacentHTML"}:
            extClass.js_features["DOM change methods"] += 1

    # Number of Event Handlers
    if node.type == "CallExpression":
        callee = node.callee
        if callee.type == "MemberExpression":
            prop = callee.property
            if prop and prop.type == "Identifier" and prop.name in {"addEventListener", "attachEvent"}:
                extClass.js_features["event handlers"] += 1
    
    # Number of XMLHttpRequests
    if node.type == "NewExpression":
        if node.callee.name == "XMLHttpRequest":
            extClass.js_features["XMLHttpRequests"] += 1
    
    # Number of HTTP header mofication callbacks
    if node.type == "CallExpression":
        callee = node.callee
        if callee.type == "MemberExpression":
            prop = callee.property
            if prop.type == "Identifier" and prop.name == "addListener":
                obj = callee.object
                if obj.type == "MemberExpression":
                    event_prop = obj.property
                    if (event_prop.type == "Identifier" and event_prop.name in {"onBeforeSendHeaders","onHeadersReceived","onSendHeaders"}):
                        extClass.js_features["modification callbacks"] += 1

    # Number of HTTP Scripts
    if node.type == "AssignmentExpression":
        left = node.left
        right = node.right
        if (
            left.type == "MemberExpression"
            and left.property.name == "src"
            and right.type == "Literal"
            and isinstance(right.value, str)
            and right.value.startswith(("http://"))
        ):
            extClass.js_features["HTTP scripts"] += 1

    # Visit node's children
    for attr, value in node.__dict__.items():

        # Single child node
        if hasattr(value, 'type'):
            traverseNode(value, extClass)

        # List of child nodes
        elif isinstance(value, list):
            for item in value:
                if hasattr(item, 'type'):
                    traverseNode(item, extClass)

def extractStringFeatures(script, extClass):
    # Update total number of files encountered
    extClass.js_totals["file_count"] += 1

    with open(script, 'r', encoding='utf-8', errors='ignore') as fp:
        content = fp.read()

        # update total number of chars in each file
        extClass.js_totals["total_chars"] += len(content)

        # Average line length Feature (Sum)
        lines = content.splitlines()
        extClass.js_totals["total_lines"] += len(lines)

        for line in lines:
            extClass.js_totals["total_line_chars"] += len(line)

        # Whitespace percentage / specific characters
        for c in content:
            if c in suspicious:
                extClass.js_totals["specific_chars"] += 1
            if c.isspace():
                extClass.js_totals["whitespace"] += 1

        # AVG Word Size
        words = re.findall(r'[A-Za-z0-9_]+', content)
        extClass.js_features["word size"] += sum(len(w) for w in words)
        extClass.js_totals["total_words"] += len(words)

        # Keyword density
        lower = content.lower()
        for kw in keywords:
            extClass.js_keyword_den[f"kw_{kw}"] += lower.count(kw)

        # String entropy - - - weird math
        strings = re.findall(r'["\']([^"\']{6,})["\']', content)

        for string in strings:
            freq = {}
            for char in string:
                freq[char] = freq.get(char, 0) + 1

            entropy = 0
            for count in freq.values():
                p = count / len(string)
                entropy -= p * log2(p)

            extClass.js_features["string entropy"] += entropy
            extClass.js_totals["entropy_strings"] += 1
