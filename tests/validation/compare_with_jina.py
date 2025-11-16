#!/usr/bin/env python3
"""
Compare the News Extractor results with Jina Reader (https://r.jina.ai/<url>)
for the canonical validation URLs.
"""

from __future__ import annotations

import logging
import textwrap
from typing import Any, Dict, List, Optional

import requests

from news_extractor import ArticleExtractor

logger = logging.getLogger(__name__)


VALIDATION_URLS: List[Dict[str, str]] = [
    {
        "name": "T24 - Empty extraction",
        "url": "https://t24.com.tr/haber/victor-osimhen-sampiyonlar-ligi-nde-haftanin-11-ine-secildi,1274139",
        "issue": "Newspaper4k empty text",
    },
    {
        "name": "Sözcü - 404 error",
        "url": "https://www.sozcu.com.tr/2025/gundem/son-dakika-haberi-rusen-cakir-gozaltina-alindi-8423910/",
        "issue": "Newspaper removed/404",
    },
    {
        "name": "NTV Gallery - 404 error",
        "url": "https://www.ntv.com.tr/galeri/turkiye/son-dakika-gaziantepte-deprem-kandilli-ve-afad-son-depremler-listesi,9kQ8R0F5pESlN-Nn6_jYxg",
        "issue": "Gallery (out of scope)",
    },
    {
        "name": "Cumhuriyet - Wrong article",
        "url": "https://www.cumhuriyet.com.tr/turkiye/turkiye-vize-kolayligi-getirilen-ulkeler-listesi-listede-hangi-ulkeler-var-2261093",
        "issue": "Previously mismatched title",
    },
    {
        "name": "Bianet (baseline)",
        "url": "https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281",
        "issue": "Baseline",
    },
    {
        "name": "OdaTV (good)",
        "url": "https://www.odatv.com/guncel/akran-zorbaligi-davasinda-karar-cikti-120122351",
        "issue": "Baseline",
    },
]

MIN_TEXT_LENGTH = 100
ERROR_KEYWORDS = ("404", "sayfa bulunamadı", "anasayfa", "Haberler, En Son Güncel Haberler")


def looks_like_error(text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in ERROR_KEYWORDS)


def fetch_jina_reader(url: str) -> Dict[str, Any]:
    jina_url = f"https://r.jina.ai/{url}"
    result: Dict[str, Any] = {
        "success": False,
        "text_length": 0,
        "status": None,
        "error": None,
        "preview": "",
        "needs_review": False,
    }
    try:
        response = requests.get(jina_url, timeout=20)
        result["status"] = response.status_code
        response.raise_for_status()
        text = response.text.strip()
        result["text_length"] = len(text)
        result["success"] = len(text) >= MIN_TEXT_LENGTH
        result["preview"] = textwrap.shorten(text, width=160, placeholder="...")
        if looks_like_error(text):
            result["needs_review"] = True
    except requests.RequestException as exc:
        logger.warning("Jina reader failed for url=%s: %s", url, exc)
        result["error"] = str(exc)
    return result


def summarize_row(name: str, local: Optional[Dict[str, Any]], jina: Dict[str, Any]) -> None:
    local_status = "✅" if local else "❌"
    jina_status = "✅" if jina["success"] else "❌"
    local_len = local["text_length"] if local else 0
    jina_len = jina["text_length"]
    local_method = local["method"] if local else "-"
    warning_tag = " [REVIEW]" if jina.get("needs_review") else ""

    print("=" * 80)
    print(name)
    print("-" * 80)
    print(f"News Extractor: {local_status} | len={local_len} | method={local_method}")
    if local:
        preview = textwrap.shorten(local["text"], width=160, placeholder="...")
        if looks_like_error(local["text"]):
            preview += " [REVIEW]"
        print(f"Preview: {preview}")
    print()
    print(f"Jina Reader  : {jina_status}{warning_tag} | len={jina_len} | status={jina['status']}")
    if jina["preview"]:
        print(f"Preview: {jina['preview']}")
    if jina["error"]:
        print(f"Error: {jina['error']}")
    print()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    extractor = ArticleExtractor(min_text_length=MIN_TEXT_LENGTH)
    local_success = 0
    jina_success = 0

    for entry in VALIDATION_URLS:
        url = entry["url"]
        local = extractor.extract(url)
        jina = fetch_jina_reader(url)
        if local:
            local_success += 1
        if jina["success"]:
            jina_success += 1
        summarize_row(entry["name"], local, jina)

    total = len(VALIDATION_URLS)
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"News Extractor success: {local_success}/{total} ({local_success/total*100:.1f}%)")
    print(f"Jina Reader success : {jina_success}/{total} ({jina_success/total*100:.1f}%)")


if __name__ == "__main__":
    main()
