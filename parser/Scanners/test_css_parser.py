from css_parser import analyze_CSS

class DummyExt:
    def __init__(self):
        self.css_features = None

dummy = DummyExt()

analyze_CSS("test.css", dummy)

print(dummy.css_features)