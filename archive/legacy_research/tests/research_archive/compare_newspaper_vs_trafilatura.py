#!/usr/bin/env python3
"""
Compare Newspaper4k vs Trafilatura on the same URLs
Extract content with both libraries and save for analysis
"""

from newspaper import Article, Config
import trafilatura
import json
from datetime import datetime
import time

# Test URLs from different outlets (using URLs we already tested)
test_urls = [
    # Hurriyet
    'https://www.hurriyet.com.tr/haberleri/18-30-yas-arasi-toki-basvuru-sartlari',

    # OdaTV
    'https://www.odatv.com/guncel/akran-zorbaligi-davasinda-karar-cikti-120122351',
    'https://www.odatv.com/dunya/belcika-milli-guvenlik-konseyi-dronelar-sebebiyle-acil-toplanma-karari-aldi-120122297',
    'https://www.odatv.com/guncel/ogrencisi-tarafindan-vurulan-ogretmen-davayi-kazandi-120122371',

    # Bianet
    'https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281',
    'https://bianet.org/haber/iklim-agindan-turkiyeye-emisyonlari-azaltmadan-iklim-kriziyle-mucadele-edilemez-313275',
    'https://bianet.org/haber/gazetecilere-operasyon-yalcin-cakir-oghan-sevinc-ve-colak-serbest-313253',

    # Sozcu
    'https://www.sozcu.com.tr/trafigi-tehlikeye-dusuren-drifte-ceza-p256461',
    'https://www.sozcu.com.tr/baskan-5-ay-sonra-gorevi-birakti-p256459',

    # Cumhuriyet
    'https://www.cumhuriyet.com.tr/turkiye/son-dakika-manifest-uyelerinin-imza-zorunlulugu-kaldirildi-yurtdisi-cikis-yasagi-devam-edecek-2450429',
    'https://www.cumhuriyet.com.tr/ekonomi/altin-yeniden-yukseliste-fiyatlar-o-rakama-yaklasti-gram-ceyrek-cumhuriyet-altini-bugun-ne-kadar-oldu-6-kasim-2025-persembe-altin-fiyatlari-2450245',

    # Milliyet
    'https://www.milliyet.com.tr/milliyet-tv/son-sansiydi-listeye-kayit-oldu-45-dakika-sonra-telefonu-caldi-video-7478234',
    'https://www.milliyet.com.tr/dunya/bmden-suriye-karari-saraya-yonelik-yaptirimlar-kaldirildi-7478392',

    # T24
    'https://t24.com.tr/haber/victor-osimhen-sampiyonlar-ligi-nde-haftanin-11-ine-secildi,1274139',
    'https://t24.com.tr/haber/merkez-bankasi-rezervleri-gecen-hafta-geriledi,1274090',

    # Diken
    'https://www.diken.com.tr/evrenin-ilk-donemlerinde-olusmus-super-kutleli-bir-kara-delik-kesfedildi/',
    'https://www.diken.com.tr/fusun-sarp-nebil-mamdani-daha-genc-ve-dijital-odakli-kampanyalarin-yerlesik-siyaseti-yenebilecegini-gosterdi/',
]


def extract_with_newspaper4k(url):
    """Extract article content using Newspaper4k"""
    try:
        config = Config()
        config.language = 'tr'
        config.request_timeout = 10
        config.browser_user_agent = 'Mozilla/5.0'

        article = Article(url, config=config)
        article.download()
        article.parse()

        result = {
            'success': True,
            'title': article.title,
            'authors': article.authors,
            'publish_date': str(article.publish_date) if article.publish_date else None,
            'text': article.text,
            'text_length': len(article.text),
            'top_image': article.top_image,
            'meta_description': article.meta_description,
            'meta_keywords': article.meta_keywords,
        }

        return result

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'text': '',
            'text_length': 0
        }


def extract_with_trafilatura(url):
    """Extract article content using Trafilatura"""
    try:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return {
                'success': False,
                'error': 'Failed to download URL',
                'text': '',
                'text_length': 0
            }

        # Extract with metadata
        metadata = trafilatura.extract_metadata(downloaded)
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            with_metadata=False  # We get metadata separately
        )

        if not text:
            return {
                'success': False,
                'error': 'No text extracted',
                'text': '',
                'text_length': 0
            }

        result = {
            'success': True,
            'title': metadata.title if metadata else None,
            'authors': metadata.author if metadata else None,
            'publish_date': metadata.date if metadata else None,
            'text': text,
            'text_length': len(text),
            'description': metadata.description if metadata else None,
            'categories': metadata.categories if metadata else None,
            'tags': metadata.tags if metadata else None,
            'sitename': metadata.sitename if metadata else None,
        }

        return result

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'text': '',
            'text_length': 0
        }


def compare_extractions():
    """Compare both extraction methods on the same URLs"""

    print("=" * 80)
    print("NEWSPAPER4K VS TRAFILATURA COMPARISON")
    print("=" * 80)
    print(f"\nTesting {len(test_urls)} URLs with both libraries...\n")

    results = {
        'test_date': datetime.now().isoformat(),
        'total_urls': len(test_urls),
        'comparisons': []
    }

    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Processing: {url[:80]}...")

        # Extract with both
        print("  - Newspaper4k...", end=" ", flush=True)
        newspaper_result = extract_with_newspaper4k(url)
        print(f"{'✅' if newspaper_result['success'] else '❌'} ({newspaper_result['text_length']} chars)")

        print("  - Trafilatura...", end=" ", flush=True)
        trafilatura_result = extract_with_trafilatura(url)
        print(f"{'✅' if trafilatura_result['success'] else '❌'} ({trafilatura_result['text_length']} chars)")

        # Store comparison
        comparison = {
            'url': url,
            'outlet': url.split('/')[2].replace('www.', ''),
            'newspaper4k': newspaper_result,
            'trafilatura': trafilatura_result,
            'text_length_diff': newspaper_result['text_length'] - trafilatura_result['text_length'],
        }

        results['comparisons'].append(comparison)

        # Small delay to be polite
        time.sleep(0.5)

    # Calculate summary stats
    newspaper_successes = sum(1 for c in results['comparisons'] if c['newspaper4k']['success'])
    trafilatura_successes = sum(1 for c in results['comparisons'] if c['trafilatura']['success'])

    newspaper_avg_length = sum(c['newspaper4k']['text_length'] for c in results['comparisons']) / len(results['comparisons'])
    trafilatura_avg_length = sum(c['trafilatura']['text_length'] for c in results['comparisons']) / len(results['comparisons'])

    results['summary'] = {
        'newspaper4k': {
            'successes': newspaper_successes,
            'success_rate': newspaper_successes / len(test_urls) * 100,
            'avg_text_length': newspaper_avg_length,
        },
        'trafilatura': {
            'successes': trafilatura_successes,
            'success_rate': trafilatura_successes / len(test_urls) * 100,
            'avg_text_length': trafilatura_avg_length,
        }
    }

    # Save results
    output_file = f'comparison_newspaper_vs_trafilatura_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Print summary
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)

    print(f"\nNewspaper4k:")
    print(f"  Success rate: {newspaper_successes}/{len(test_urls)} ({results['summary']['newspaper4k']['success_rate']:.1f}%)")
    print(f"  Avg text length: {newspaper_avg_length:.0f} chars")

    print(f"\nTrafilatura:")
    print(f"  Success rate: {trafilatura_successes}/{len(test_urls)} ({results['summary']['trafilatura']['success_rate']:.1f}%)")
    print(f"  Avg text length: {trafilatura_avg_length:.0f} chars")

    print(f"\n📁 Detailed results saved to: {output_file}")
    print("\n" + "=" * 80)
    print("Ready for analysis by subagent!")
    print("=" * 80)

    return results, output_file


if __name__ == '__main__':
    results, output_file = compare_extractions()
