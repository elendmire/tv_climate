from pathlib import Path

import pytest

from tr_climate.matcher import load_keywords, match_climate, match_topics


@pytest.fixture
def kw_path(tmp_path: Path) -> Path:
    p = tmp_path / "k.yaml"
    p.write_text(
        """
version: "test-1"
climate_keywords:
  tr:
    - iklim
    - sera gazı
  en:
    - climate
topic_rules:
  energy:
    tr: [petrol]
    en: []
""",
        encoding="utf-8",
    )
    return p


def test_climate_match_turkish(kw_path: Path) -> None:
    cfg = load_keywords(kw_path)
    ok, hits = match_climate(cfg, "Türkiye iklim politikası", "")
    assert ok is True
    assert "iklim" in hits


def test_climate_no_false_empty(kw_path: Path) -> None:
    cfg = load_keywords(kw_path)
    ok, hits = match_climate(cfg, "Seçim sonuçları açıklandı", "")
    assert ok is False
    assert hits == []


def test_topic_energy(kw_path: Path) -> None:
    cfg = load_keywords(kw_path)
    topics = match_topics(cfg, "Petrol fiyatları arttı", "")
    assert "energy" in topics
