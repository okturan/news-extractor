#!/usr/bin/env python3
"""
Test Newspaper4k's Article extraction on randomly selected URLs
from different Turkish news outlets
"""

from newspaper import Article, Config
import json
from datetime import datetime

# Test URLs from different outlets
test_urls = {
    'Hurriyet': [
        'https://www.hurriyet.com.tr/haberleri/18-30-yas-arasi-toki-basvuru-sartlari',
        'https://www.hurriyet.com.tr/bilgi/galeri-en-yeni-cuma-mesajlari-2025-resimli-kisa-anlamli-cuma-sozleri-tikla-ucretsiz-indir-ekrani-yakinlariniza-hadisli-duali-ayetli-43010548',
        'https://www.hurriyet.com.tr/mahmure/astroloji/',
    ],
    'OdaTV': [
        'https://www.odatv.com/guncel/akran-zorbaligi-davasinda-karar-cikti-120122351',
        'https://www.odatv.com/dunya/belcika-milli-guvenlik-konseyi-dronelar-sebebiyle-acil-toplanma-karari-aldi-120122297',
        'https://www.odatv.com/guncel/ogrencisi-tarafindan-vurulan-ogretmen-davayi-kazandi-120122371',
    ],
    'Bianet': [
        'https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281',
        'https://bianet.org/page/gizlilik-sozlesmesi-285338',
        'https://bianet.org/haber/iklim-agindan-turkiyeye-emisyonlari-azaltmadan-iklim-kriziyle-mucadele-edilemez-313275',
    ],
    'Sozcu': [
        'https://www.sozcu.com.tr/trafigi-tehlikeye-dusuren-drifte-ceza-p256461',
        'https://www.sozcu.com.tr/baskan-5-ay-sonra-gorevi-birakti-p256459',
        'https://www.sozcu.com.tr/firtina-degil-depremdir-gelen-p256151',
    ],
    'Cumhuriyet': [
        'https://www.cumhuriyet.com.tr/turkiye/son-dakika-manifest-uyelerinin-imza-zorunlulugu-kaldirildi-yurtdisi-cikis-yasagi-devam-edecek-2450429',
        'https://www.cumhuriyet.com.tr/ekonomi/altin-yeniden-yukseliste-fiyatlar-o-rakama-yaklasti-gram-ceyrek-cumhuriyet-altini-bugun-ne-kadar-oldu-6-kasim-2025-persembe-altin-fiyatlari-2450245',
        'https://www.cumhuriyet.com.tr/ekonomi/kasim-ayi-emekli-promosyonlari-guncellendi-en-yuksek-odemeyi-hangi-banka-yapiyor-2450284',
    ],
    'Milliyet': [
        'https://www.milliyet.com.tr/milliyet-tv/son-sansiydi-listeye-kayit-oldu-45-dakika-sonra-telefonu-caldi-video-7478234',
        'https://www.milliyet.com.tr/ramazan/imsakiye/istanbul-iftar-vakti/',
        'https://www.milliyet.com.tr/dunya/bmden-suriye-karari-saraya-yonelik-yaptirimlar-kaldirildi-7478392',
    ],
    'T24': [
        'https://t24.com.tr/haber/victor-osimhen-sampiyonlar-ligi-nde-haftanin-11-ine-secildi,1274139',
        'https://t24.com.tr/haber/merkez-bankasi-rezervleri-gecen-hafta-geriledi,1274090',
        'https://t24.com.tr/haber/isa-karakas-yazdi-hangi-maas-ve-haklardan-faydalanmak-icin-evli-olmak-gerekiyor,1256020',
    ],
    'Diken': [
        'https://www.diken.com.tr/evrenin-ilk-donemlerinde-olusmus-super-kutleli-bir-kara-delik-kesfedildi/',
        'https://www.diken.com.tr/fusun-sarp-nebil-mamdani-daha-genc-ve-dijital-odakli-kampanyalarin-yerlesik-siyaseti-yenebilecegini-gosterdi/',
        'https://www.diken.com.tr/brand-week-istanbula-son-bir-hafta-2/',
    ],
}


def test_article_extraction(url, source_name):
    """Test Newspaper4k Article extraction on a single URL"""

    try:
        config = Config()
        config.language = 'tr'
        config.request_timeout = 10
        config.browser_user_agent = 'Mozilla/5.0'

        article = Article(url, config=config)
        article.download()
        article.parse()

        # Get metadata
        result = {
            'url': url,
            'source': source_name,
            'success': True,
            'title': article.title,
            'authors': article.authors,
            'publish_date': str(article.publish_date) if article.publish_date else None,
            'text_length': len(article.text),
            'text_preview': article.text[:200] + '...' if len(article.text) > 200 else article.text,
            'top_image': article.top_image,
            'meta_description': article.meta_description,
            'meta_keywords': article.meta_keywords,
        }

        # Success indicator
        if result['text_length'] > 100:
            status = '✅'
        elif result['text_length'] > 0:
            status = '⚠️'
        else:
            status = '❌'

        print(f"{status} {source_name:12} | {result['text_length']:4} chars | {article.title[:50]}")

        return result

    except Exception as e:
        print(f"❌ {source_name:12} | ERROR | {str(e)[:50]}")
        return {
            'url': url,
            'source': source_name,
            'success': False,
            'error': str(e)
        }


def main():
    """Test Newspaper4k on random URLs from each outlet"""

    print("=" * 80)
    print("NEWSPAPER4K EXTRACTION TEST ON RANDOM URLS")
    print("=" * 80)
    print("\nTesting Article class on 3 random URLs from each of 8 outlets (24 total)")
    print("-" * 80)
    print(f"{'Status':^6} | {'Outlet':^12} | {'Chars':^10} | {'Title Preview'}")
    print("-" * 80)

    results = {
        'test_date': datetime.now().isoformat(),
        'total_urls': 0,
        'successful': 0,
        'failed': 0,
        'by_outlet': {}
    }

    for outlet, urls in test_urls.items():
        outlet_results = []

        for url in urls:
            result = test_article_extraction(url, outlet)
            outlet_results.append(result)

            results['total_urls'] += 1
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1

        results['by_outlet'][outlet] = {
            'tested': len(urls),
            'successful': sum(1 for r in outlet_results if r['success']),
            'results': outlet_results
        }

    # Print summary
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)

    print(f"\nOverall Results:")
    print(f"  Total URLs tested: {results['total_urls']}")
    print(f"  Successful: {results['successful']} ({results['successful']/results['total_urls']*100:.1f}%)")
    print(f"  Failed: {results['failed']} ({results['failed']/results['total_urls']*100:.1f}%)")

    print(f"\nResults by Outlet:")
    print("-" * 80)
    for outlet, data in results['by_outlet'].items():
        success_rate = data['successful'] / data['tested'] * 100
        status = '✅' if success_rate == 100 else '⚠️' if success_rate > 0 else '❌'
        print(f"  {status} {outlet:12} {data['successful']}/{data['tested']} ({success_rate:.0f}%)")

    # Text length analysis
    print(f"\nText Length Analysis:")
    print("-" * 80)
    for outlet, data in results['by_outlet'].items():
        lengths = [r.get('text_length', 0) for r in data['results'] if r['success']]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            print(f"  {outlet:12} avg: {avg_length:6.0f} chars, range: {min(lengths)}-{max(lengths)}")
        else:
            print(f"  {outlet:12} No successful extractions")

    # Save detailed results
    output_file = f'newspaper4k_extraction_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n📁 Detailed results saved to: {output_file}")

    # Show some example extractions
    print(f"\n" + "=" * 80)
    print("SAMPLE EXTRACTIONS (first success from each outlet)")
    print("=" * 80)

    for outlet, data in results['by_outlet'].items():
        successful = [r for r in data['results'] if r['success'] and r.get('text_length', 0) > 100]
        if successful:
            sample = successful[0]
            print(f"\n{outlet} - {sample['title']}")
            print(f"  URL: {sample['url']}")
            print(f"  Length: {sample['text_length']} chars")
            print(f"  Authors: {sample['authors']}")
            print(f"  Date: {sample['publish_date']}")
            print(f"  Preview: {sample['text_preview']}")
        else:
            print(f"\n{outlet} - No successful extractions")

    return results


if __name__ == '__main__':
    results = main()
