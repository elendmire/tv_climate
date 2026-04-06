from pathlib import Path

from bs4 import BeautifulSoup

from tr_climate.trt_html import _ARTICLE_RE


def test_article_url_regex() -> None:
    assert _ARTICLE_RE.match(
        "https://www.trthaber.com/haber/gundem/ornek-baslik-123456.html"
    )
    assert not _ARTICLE_RE.match("https://www.trthaber.com/haber/gundem/")


def test_parse_fixture_snippet() -> None:
    html = Path(__file__).parent / "fixtures" / "trt_snippet.html"
    soup = BeautifulSoup(html.read_text(encoding="utf-8"), "html.parser")
    found = []
    for a in soup.select("a.site-url[href]"):
        href = (a.get("href") or "").strip()
        if _ARTICLE_RE.match(href):
            found.append((href, a.get("title")))
    assert len(found) == 2
    assert "iklim" in found[0][1].lower()
