import bleach

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "ul", "ol", "li", "a",
    "code", "pre", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6",
]
ALLOWED_ATTRS = {"a": ["href", "title"]}


def sanitize_text(text: str) -> str:
    return bleach.clean(text, tags=[], strip=True)


def sanitize_html(text: str) -> str:
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
