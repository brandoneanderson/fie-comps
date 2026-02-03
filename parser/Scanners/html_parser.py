from html.parser import HTMLParser
from pathlib import Path

URL_ATTRS = {"src", "href", "action", "formaction", "data", "poster"}


class ExtensionHTMLFeatureParser(HTMLParser):
    """
    HTML-only feature extraction for extensions.
    Produces a dict like:
      - num_iframe_tags
      - num_form_tags
      - num_object_tags, num_embed_tags, num_applet_tags
      - num_script_tags, num_external_script_src
      - num_inline_event_handlers
      - num_javascript_urls, num_data_urls
      - num_http_urls, num_external_urls
      - num_external_iframe_src, num_external_form_actions
      - num_meta_refresh
      - num_password_inputs
    """
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.results = {
            "num_iframe_tags": 0,
            "num_form_tags": 0,

            "num_object_tags": 0,
            "num_embed_tags": 0,
            "num_applet_tags": 0,

            "num_script_tags": 0,
            "num_external_script_src": 0,

            "num_inline_event_handlers": 0,
            "num_javascript_urls": 0,
            "num_data_urls": 0,

            "num_http_urls": 0,
            "num_external_urls": 0,

            "num_external_iframe_src": 0,
            "num_external_form_actions": 0,

            "num_meta_refresh": 0,
            "num_password_inputs": 0,
        }

    @staticmethod
    def _is_external(url: str) -> bool:
        u = (url or "").strip().lower()
        return u.startswith("http://") or u.startswith("https://")

    @staticmethod
    def _is_http(url: str) -> bool:
        u = (url or "").strip().lower()
        return u.startswith("http://")

    @staticmethod
    def _is_js_url(url: str) -> bool:
        u = (url or "").strip().lower()
        return u.startswith("javascript:")

    @staticmethod
    def _is_data_url(url: str) -> bool:
        u = (url or "").strip().lower()
        return u.startswith("data:")

    def handle_starttag(self, tag, attrs):
        t = (tag or "").lower()
        attr_dict = { (k or "").lower(): (v or "") for k, v in (attrs or []) if k }

        # Tag counts you asked for
        if t == "iframe":
            self.results["num_iframe_tags"] += 1
        elif t == "form":
            self.results["num_form_tags"] += 1
        elif t == "script":
            self.results["num_script_tags"] += 1
        elif t == "object":
            self.results["num_object_tags"] += 1
        elif t == "embed":
            self.results["num_embed_tags"] += 1
        elif t == "applet":
            self.results["num_applet_tags"] += 1

        # Inline event handlers (XSS-ish vector): onclick=, onload=, etc.
        for k in attr_dict.keys():
            if k.startswith("on"):
                self.results["num_inline_event_handlers"] += 1

        # Password inputs (phishing surface)
        if t == "input":
            if attr_dict.get("type", "").strip().lower() == "password":
                self.results["num_password_inputs"] += 1

        # Meta refresh redirects
        if t == "meta":
            if attr_dict.get("http-equiv", "").strip().lower() == "refresh":
                self.results["num_meta_refresh"] += 1

        # URL-bearing attrs: href/src/action/...
        for attr_name, attr_val in attr_dict.items():
            if attr_name not in URL_ATTRS:
                continue

            url = (attr_val or "").strip()
            if not url:
                continue

            if self._is_http(url):
                self.results["num_http_urls"] += 1

            if self._is_external(url):
                self.results["num_external_urls"] += 1

            if self._is_js_url(url):
                self.results["num_javascript_urls"] += 1

            if self._is_data_url(url):
                self.results["num_data_urls"] += 1

            # Tag-specific “external” checks
            if t == "iframe" and attr_name == "src" and self._is_external(url):
                self.results["num_external_iframe_src"] += 1

            if t == "form" and attr_name == "action" and self._is_external(url):
                self.results["num_external_form_actions"] += 1

            if t == "script" and attr_name == "src" and self._is_external(url):
                self.results["num_external_script_src"] += 1


def analyze_HTML(htmlFile, extClass):
    """
    Read HTML from file path, parse, and accumulate into extClass.html_features.
    Mirrors the behavior of analyze_CSS().
    """
    p = Path(htmlFile)

    # Read tolerant of encoding weirdness
    try:
        html = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        html = p.read_text(errors="ignore")

    parser = ExtensionHTMLFeatureParser()
    parser.feed(html)

    results = parser.results

    # If first html file parsed, assign results
    if extClass.html_features is None:
        extClass.html_features = results
    else:
        for feature, count in results.items():
            extClass.html_features[feature] = extClass.html_features.get(feature, 0) + count

    return
