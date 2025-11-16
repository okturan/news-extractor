#!/usr/bin/env python3
"""
Test Trafilatura 2.0 on previously failed URLs
Focus: The 3 Bianet articles that failed in previous test
"""

import trafilatura
import json
from datetime import datetime

# The 3 Bianet URLs that failed with Trafilatura before
bianet_urls = [
    'https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281',
    'https://bianet.org/haber/iklim-agindan-turkiyeye-emisyonlari-azaltmadan-iklim-kriziyle-mucadele-edilemez-313275',
    'https://bianet.org/haber/gazetecilere-operasyon-yalcin-cakir-oghan-sevinc-ve-colak-serbest-313253',
]

# Also test the full set from before
all_test_urls = [
    # Hurriyet
    'https://www.hurriyet.com.tr/haberleri/18-30-yas-arasi-toki-basvuru-sartlari',

    # OdaTV
    'https://www.odatv.com/guncel/akran-zorbaligi-davasinda-karar-cikti-120122351',
    'https://www.odatv.com/dunya/belcika-milli-guvenlik-konseyi-dronelar-sebebiyle-acil-toplanma-karari-aldi-120122297',

    # Bianet (the problematic ones)
    'https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281',
    'https://bianet.org/haber/iklim-agindan-turkiyeye-emisyonlari-azaltmadan-iklim-kriziyle-mucadele-edilemez-313275',
    'https://bianet.org/haber/gazetecilere-operasyon-yalcin-cakir-oghan-sevinc-ve-colak-serbest-313253',

    # Sozcu
    'https://www.sozcu.com.tr/trafigi-tehlikeye-dusuren-drifte-ceza-p256461',

    # Cumhuriyet
    'https://www.cumhuriyet.com.tr/turkiye/son-dakika-manifest-uyelerinin-imza-zorunlulugu-kaldirildi-yurtdisi-cikis-yasagi-devam-edecek-2450429',

    # T24
    'https://t24.com.tr/haber/victor-osimhen-sampiyonlar-ligi-nde-haftanin-11-ine-secildi,1274139',
    'https://t24.com.tr/haber/merkez-bankasi-rezervleri-gecen-hafta-geriledi,1274090',

    # Diken
    'https://www.diken.com.tr/evrenin-ilk-donemlerinde-olusmus-super-kutleli-bir-kara-delik-kesfedildi/',
]


def test_trafilatura_2_0(url):
    """Test Trafilatura 2.0 extraction"""
    try:
        # Get version info
        version = trafilatura.__version__

        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return {
                'url': url,
                'version': version,
                'success': False,
                'error': 'Failed to download',
                'text_length': 0
            }

        # Extract metadata
        metadata = trafilatura.extract_metadata(downloaded)

        # Extract text
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            with_metadata=False
        )

        if not text:
            return {
                'url': url,
                'version': version,
                'success': False,
                'error': 'No text extracted',
                'text_length': 0
            }

        return {
            'url': url,
            'version': version,
            'success': True,
            'title': metadata.title if metadata else None,
            'author': metadata.author if metadata else None,
            'date': metadata.date if metadata else None,
            'text': text,
            'text_length': len(text),
            'text_preview': text[:200] + '...' if len(text) > 200 else text,
        }

    except Exception as e:
        return {
            'url': url,
            'version': trafilatura.__version__,
            'success': False,
            'error': str(e),
            'text_length': 0
        }


print("=" * 80)
print("TRAFILATURA 2.0 TEST - FOCUS ON BIANET FAILURES")
print("=" * 80)
print(f"Trafilatura version: {trafilatura.__version__}")
print()

# Test the 3 Bianet URLs first
print("🎯 TESTING BIANET (Previously Failed):")
print("-" * 80)

bianet_results = []
for i, url in enumerate(bianet_urls, 1):
    print(f"\n[{i}/3] {url}")
    result = test_trafilatura_2_0(url)
    bianet_results.append(result)

    if result['success']:
        print(f"  ✅ SUCCESS - {result['text_length']} chars")
        print(f"  Title: {result['title']}")
        print(f"  Author: {result['author']}")
        print(f"  Date: {result['date']}")
        print(f"  Preview: {result['text_preview'][:100]}...")
    else:
        print(f"  ❌ FAILED - {result.get('error', 'Unknown error')}")

# Summary for Bianet
bianet_success = sum(1 for r in bianet_results if r['success'])
print("\n" + "=" * 80)
print("BIANET RESULTS:")
print("=" * 80)
print(f"Success rate: {bianet_success}/3 ({bianet_success/3*100:.1f}%)")
if bianet_success == 3:
    print("🎉 FIXED! All Bianet articles now extract successfully!")
elif bianet_success > 0:
    print("⚠️  Partial improvement - some Bianet articles now work")
else:
    print("❌ Still failing on Bianet")

# Test all URLs
print("\n\n" + "=" * 80)
print("FULL TEST ON ALL OUTLETS:")
print("-" * 80)

all_results = []
for i, url in enumerate(all_test_urls, 1):
    outlet = url.split('/')[2].replace('www.', '')
    print(f"\n[{i}/{len(all_test_urls)}] {outlet}", end=" ")

    result = test_trafilatura_2_0(url)
    all_results.append(result)

    if result['success']:
        print(f"✅ {result['text_length']} chars")
    else:
        print(f"❌ {result.get('error', 'Failed')}")

# Overall summary
print("\n" + "=" * 80)
print("OVERALL SUMMARY:")
print("=" * 80)

total_success = sum(1 for r in all_results if r['success'])
success_rate = total_success / len(all_results) * 100

print(f"\nTrafilatura version: {trafilatura.__version__}")
print(f"Total URLs tested: {len(all_results)}")
print(f"Successful: {total_success} ({success_rate:.1f}%)")
print(f"Failed: {len(all_results) - total_success}")

# Compare with previous results
print("\n📊 Comparison with Previous Test:")
print("-" * 80)
print(f"Previous Trafilatura: 14/17 (82.4%)")
print(f"Trafilatura 2.0:     {total_success}/{len(all_results)} ({success_rate:.1f}%)")

if success_rate > 82.4:
    improvement = success_rate - 82.4
    print(f"✅ IMPROVEMENT: +{improvement:.1f}% success rate!")
elif success_rate == 82.4:
    print("➡️  Same performance as before")
else:
    print("⚠️  Lower performance (unexpected)")

# Save detailed results
output_file = f'trafilatura_2_0_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'version': trafilatura.__version__,
        'test_date': datetime.now().isoformat(),
        'total_urls': len(all_results),
        'successful': total_success,
        'success_rate': success_rate,
        'results': all_results
    }, f, ensure_ascii=False, indent=2)

print(f"\n📁 Detailed results saved to: {output_file}")
print("=" * 80)
