from __future__ import annotations

import re
import unicodedata


def normalize_text(s: str) -> str:
  """NFKC + casefold for robust TR/EN substring matching."""
  if not s:
    return ""
  return unicodedata.normalize("NFKC", s).casefold()


def strip_html_to_text(html: str, max_len: int = 500) -> str:
  if not html:
    return ""
  text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
  text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
  text = re.sub(r"<[^>]+>", " ", text)
  text = re.sub(r"\s+", " ", text).strip()
  return text[:max_len]

