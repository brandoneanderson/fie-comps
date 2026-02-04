from html.parser import HTMLParser

class myHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)

def analyze_HTML(htmlFile, extClass):
    # htmlParser = myHTMLParser()
    # htmlParser.feed(htmlFile)
    return