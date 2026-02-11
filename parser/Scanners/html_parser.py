# Scanners/html_parser.py
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

URL_ATTRS = {"src", "href", "action", "formaction", "data", "poster"}


def _is_probable_file_path(x: Any) -> bool:
    """True if x looks like a path that exists on disk."""
    try:
        p = Path(str(x))
        return p.is_file()
        # return isinstance(x, (str, Path)) and Path(str(x)).exists()
    except Exception:
        return False


def _is_external(url: str) -> bool:
    u = (url or "").strip().lower()
    return u.startswith("http://") or u.startswith("https://")


def _is_http(url: str) -> bool:
    u = (url or "").strip().lower()
    return u.startswith("http://")


def _is_js_url(url: str) -> bool:
    u = (url or "").strip().lower()
    return u.startswith("javascript:")


def _is_data_url(url: str) -> bool:
    u = (url or "").strip().lower()
    return u.startswith("data:")


def _cap_add(examples: Dict[str, List[str]], key: str, value: str, cap: int = 10) -> None:
    """Add example strings, de-duped, capped."""
    if not value:
        return
    bucket = examples.setdefault(key, [])
    if value in bucket:
        return
    if len(bucket) >= cap:
        return
    bucket.append(value)


def _ensure_ext_fields(extClass: Any) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    """
    Force extClass.html_features and extClass.html_examples to be dicts.
    Robust even if they start as None or were overwritten.
    """
    if not hasattr(extClass, "html_features") or extClass.html_features is None or not isinstance(extClass.html_features, dict):
        extClass.html_features = {}
    if not hasattr(extClass, "html_examples") or extClass.html_examples is None or not isinstance(extClass.html_examples, dict):
        extClass.html_examples = {}
    return extClass.html_features, extClass.html_examples


class ExtensionHTMLFeatureParser(HTMLParser):
    """
    HTML-only feature extraction for extensions.
    Produces:
      features (counts) + examples (small evidence lists)
    """
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.features: Dict[str, int] = {}
        self.examples: Dict[str, List[str]] = {}

    def _inc(self, key: str, n: int = 1) -> None:
        self.features[key] = self.features.get(key, 0) + n

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        t = (tag or "").lower()
        attr_dict = { (k or "").lower(): (v or "") for k, v in (attrs or []) if k }

        # --- tag counts ---
        if t == "iframe":
            self._inc("num_iframe_tags")
        elif t == "form":
            self._inc("num_form_tags")
        elif t == "script":
            self._inc("num_script_tags")
        elif t in {"object", "embed", "applet"}:
            self._inc(f"num_{t}_tags")

        # --- inline event handlers (XSS-ish vector) ---
        for k in attr_dict.keys():
            if k.startswith("on"):
                self._inc("num_inline_event_handlers")

        # --- password inputs (phishing surface) ---
        if t == "input":
            if attr_dict.get("type", "").strip().lower() == "password":
                self._inc("num_password_inputs")

        # --- meta refresh redirects + evidence ---
        if t == "meta":
            if attr_dict.get("http-equiv", "").strip().lower() == "refresh":
                self._inc("num_meta_refresh")
                _cap_add(self.examples, "meta_refresh_content", (attr_dict.get("content", "") or "").strip())

        # --- URL-bearing attributes ---
        for attr_name, attr_val in attr_dict.items():
            if attr_name not in URL_ATTRS:
                continue

            url = (attr_val or "").strip()
            if not url:
                continue

            if _is_http(url):
                self._inc("num_http_urls")
                _cap_add(self.examples, "http_urls", url)

            if _is_external(url):
                self._inc("num_external_urls")
                _cap_add(self.examples, "external_urls", url)

            if _is_js_url(url):
                self._inc("num_javascript_urls")
                _cap_add(self.examples, "javascript_urls", url)

            if _is_data_url(url):
                self._inc("num_data_urls")
                _cap_add(self.examples, "data_urls", url)

            # Tag-specific “external” checks + evidence
            if t == "iframe" and attr_name == "src" and _is_external(url):
                self._inc("num_external_iframe_src")
                _cap_add(self.examples, "external_iframe_src", url)

            if t == "form" and attr_name == "action" and _is_external(url):
                self._inc("num_external_form_actions")
                _cap_add(self.examples, "external_form_actions", url)

            # Scripts: count script src attrs (local OR external), plus external ones
            if t == "script" and attr_name == "src":
                self._inc("num_script_src_attrs")
                _cap_add(self.examples, "script_src_attrs", url)
                if _is_external(url):
                    self._inc("num_external_script_src")
                    _cap_add(self.examples, "external_script_src", url)


def analyze_HTML(htmlFile: Any, extClass: Any) -> None:
    """
    Analyze a single HTML file path OR raw HTML string and accumulate into extClass.

    Updates:
      - extClass.html_features: dict[str,int]
      - extClass.html_examples: dict[str,list[str]] (each list capped to 10)
    """
    features, examples = _ensure_ext_fields(extClass)

    # Load content from disk if it's a real path; otherwise treat as raw HTML
    if _is_probable_file_path(htmlFile):
        p = Path(str(htmlFile))

        # Windows MAX_PATH safety
        if len(str(p)) > 240:
            return
        
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
    else:
        content = str(htmlFile)

    parser = ExtensionHTMLFeatureParser()
    parser.feed(content)

    # Sum counts
    for k, v in parser.features.items():
        features[k] = features.get(k, 0) + int(v)

    # Merge examples (dedupe + cap)
    for key, vals in parser.examples.items():
        bucket = examples.setdefault(key, [])
        for val in vals:
            if len(bucket) >= 10:
                break
            if val not in bucket:
                bucket.append(val)
