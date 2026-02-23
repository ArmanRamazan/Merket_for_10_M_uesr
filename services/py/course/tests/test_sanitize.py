from app.sanitize import sanitize_text, sanitize_html


def test_sanitize_text_strips_script():
    assert sanitize_text('<script>alert(1)</script>') == "alert(1)"


def test_sanitize_text_strips_all_tags():
    assert sanitize_text('<b>bold</b> and <i>italic</i>') == "bold and italic"


def test_sanitize_text_preserves_plain():
    assert sanitize_text("Hello World") == "Hello World"


def test_sanitize_html_strips_script():
    result = sanitize_html('<p>Hello</p><script>alert(1)</script>')
    assert "<script>" not in result
    assert "<p>Hello</p>" in result


def test_sanitize_html_allows_safe_tags():
    html = '<p>Hello <strong>world</strong></p><ul><li>item</li></ul>'
    assert sanitize_html(html) == html


def test_sanitize_html_allows_links():
    html = '<a href="https://example.com" title="Ex">link</a>'
    assert sanitize_html(html) == html


def test_sanitize_html_strips_onclick():
    result = sanitize_html('<a href="#" onclick="alert(1)">link</a>')
    assert "onclick" not in result


def test_sanitize_html_strips_img():
    result = sanitize_html('<img src="x" onerror="alert(1)">')
    assert "<img" not in result
