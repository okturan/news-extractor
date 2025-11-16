#!/usr/bin/env python3
"""
Simple test to see all available Newspaper4k configuration options
"""

from newspaper import Config
import pprint

config = Config()

print("=" * 80)
print("ALL NEWSPAPER4K CONFIGURATION OPTIONS")
print("=" * 80)

# Get all non-private attributes
config_options = {
    attr: getattr(config, attr)
    for attr in dir(config)
    if not attr.startswith('_') and not callable(getattr(config, attr))
}

print("\nAvailable config options:")
print("-" * 80)
pprint.pprint(config_options, width=80)

print("\n" + "=" * 80)
print("DISCOVERY-RELATED OPTIONS?")
print("=" * 80)

discovery_related = {
    'memorize_articles': config.memorize_articles,
    'use_meta_language': config.use_meta_language,
    'follow_meta_refresh': config.follow_meta_refresh,
    'language': config.language,
}

print("\nThese might affect discovery:")
for key, value in discovery_related.items():
    print(f"  {key:25} = {value}")

print("\n" + "=" * 80)
print("TEST: Does changing config affect discovery?")
print("=" * 80)

from newspaper import build

# Test 1: Default config
print("\n1. Default config (language='en'):")
config1 = Config()
config1.memorize_articles = False
site1 = build('https://bianet.org', config=config1)
print(f"   Bianet articles found: {site1.size()}")

# Test 2: Turkish language
print("\n2. Turkish language (language='tr'):")
config2 = Config()
config2.language = 'tr'
config2.memorize_articles = False
site2 = build('https://bianet.org', config=config2)
print(f"   Bianet articles found: {site2.size()}")

# Test 3: Different user agent
print("\n3. Custom user agent:")
config3 = Config()
config3.language = 'tr'
config3.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
config3.memorize_articles = False
site3 = build('https://bianet.org', config=config3)
print(f"   Bianet articles found: {site3.size()}")

# Test 4: Test on different site (Cumhuriyet - had 0-416 variance)
print("\n4. Test Cumhuriyet (previously inconsistent):")
config4 = Config()
config4.language = 'tr'
config4.memorize_articles = False
site4 = build('https://www.cumhuriyet.com.tr', config=config4)
print(f"   Cumhuriyet articles found: {site4.size()}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
If all tests return similar article counts, it means:
→ Config options do NOT significantly affect URL discovery
→ Discovery algorithm is hardcoded and not configurable
→ Must use manual discovery approach for Turkish sites
""")
