# Scanners/html_report.py
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _safe_dict(x):
    return x if isinstance(x, dict) else {}


def _top_features(features: Dict[str, int]) -> List[Tuple[str, int]]:
    """
    Returns features ordered roughly by risk priority, then by count desc.
    """
    # Higher = more "interesting"
    priority = {
        "num_inline_event_handlers": 100,
        "num_javascript_urls": 95,
        "num_data_urls": 90,
        "num_http_urls": 85,
        "num_external_script_src": 82,
        "num_external_iframe_src": 80,
        "num_external_form_actions": 78,
        "num_meta_refresh": 70,
        "num_password_inputs": 65,
        "num_script_tags": 40,
        "num_script_src_attrs": 38,
        "num_iframe_tags": 35,
        "num_form_tags": 30,
        "num_object_tags": 25,
        "num_embed_tags": 25,
        "num_applet_tags": 25,
        "num_external_urls": 20,
    }

    items = [(k, int(v)) for k, v in features.items() if int(v) > 0]
    items.sort(key=lambda kv: (priority.get(kv[0], 0), kv[1]), reverse=True)
    return items


def _format_feature_name(k: str) -> str:
    # num_external_script_src -> External script src
    name = k
    if name.startswith("num_"):
        name = name[4:]
    name = name.replace("_", " ").strip()
    # small prettification
    name = name.replace("src", "src").replace("urls", "URLs")
    return name[:1].upper() + name[1:]


def _print_kv_lines(lines: List[str], title: str, pairs: List[Tuple[str, int]]) -> None:
    lines.append(f"### {title}")
    if not pairs:
        lines.append("- (none detected)")
        return
    for k, v in pairs:
        lines.append(f"- **{_format_feature_name(k)}**: {v}")


def _print_examples(lines: List[str], examples: Dict[str, List[str]]) -> None:
    lines.append("### Evidence (examples)")
    if not examples:
        lines.append("- (no examples captured)")
        return

    order = [
        "http_urls",
        "javascript_urls",
        "data_urls",
        "external_script_src",
        "external_iframe_src",
        "external_form_actions",
        "meta_refresh_content",
        "script_src_attrs",
        "external_urls",
    ]

    def titleize(key: str) -> str:
        return key.replace("_", " ").strip().title()

    any_printed = False
    for key in order:
        vals = examples.get(key, [])
        if not vals:
            continue
        any_printed = True
        lines.append(f"- **{titleize(key)}**:")
        for s in vals:
            # Keep it single-line readable
            s = str(s).replace("\n", "\\n")
            lines.append(f"  - {s}")

    # Print any other example buckets not in order list
    remaining = [k for k in examples.keys() if k not in set(order)]
    for key in sorted(remaining):
        vals = examples.get(key, [])
        if not vals:
            continue
        any_printed = True
        lines.append(f"- **{titleize(key)}**:")
        for s in vals:
            s = str(s).replace("\n", "\\n")
            lines.append(f"  - {s}")

    if not any_printed:
        lines.append("- (no examples captured)")


def html_report_section(ext: Any, heading: str = "HTML Analysis") -> str:
    """
    Returns a readable report section as a string (Markdown-like),
    based on ext.html_features and ext.html_examples.
    """
    features = _safe_dict(getattr(ext, "html_features", None))
    examples = _safe_dict(getattr(ext, "html_examples", None))

    top = _top_features(features)

    # Quick “headline” flags
    headline_flags = []
    if features.get("num_inline_event_handlers", 0) > 0:
        headline_flags.append("inline event handlers")
    if features.get("num_javascript_urls", 0) > 0:
        headline_flags.append("javascript: URLs")
    if features.get("num_http_urls", 0) > 0:
        headline_flags.append("http:// URLs (insecure)")
    if features.get("num_external_script_src", 0) > 0:
        headline_flags.append("external script src")
    if features.get("num_external_iframe_src", 0) > 0:
        headline_flags.append("external iframe src")
    if features.get("num_external_form_actions", 0) > 0:
        headline_flags.append("external form actions")
    if features.get("num_meta_refresh", 0) > 0:
        headline_flags.append("meta refresh redirects")

    lines: List[str] = []
    lines.append(f"## {heading}")

    if not top and not examples:
        lines.append("No HTML risk indicators were detected (or no HTML files were analyzed).")
        return "\n".join(lines)

    if headline_flags:
        lines.append("**Key findings:** " + ", ".join(headline_flags) + ".")
    else:
        lines.append("No high-priority HTML indicators detected, but counts/evidence below may still be useful.")

    # Counts
    _print_kv_lines(lines, "Counts", top)

    # Evidence
    _print_examples(lines, examples)

    return "\n".join(lines)
