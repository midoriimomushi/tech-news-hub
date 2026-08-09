import unittest
import os
import sys

# Add scripts directory to module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from fetch_rss import parse_rss

SAMPLE_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF 
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns="http://purl.org/rss/1.0/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:hatena="http://www.hatena.ne.jp/info/xmlns#">
  <channel>
    <title>はてなブックマーク - テクノロジー</title>
  </channel>
  <item rdf:about="https://example.com/article-1">
    <title>【テスト記事】Pythonで開発するAIツール</title>
    <link>https://example.com/article-1</link>
    <description>&lt;p&gt;これは&lt;b&gt;テスト記事&lt;/b&gt;の概要です。&lt;/p&gt;</description>
    <dc:date>2026-08-08T12:00:00Z</dc:date>
    <hatena:bookmarkcount>150</hatena:bookmarkcount>
    <hatena:imageurl>https://example.com/thumb.jpg</hatena:imageurl>
  </item>
</rdf:RDF>
"""

class TestFetchRSS(unittest.TestCase):

    def test_parse_rss_success(self):
        """正常なRSS XMLから正しくデータが抽出できるかテスト"""
        items = parse_rss(SAMPLE_RSS_XML.encode('utf-8'), 'ai')
        
        self.assertEqual(len(items), 1)
        item = items[0]
        
        self.assertEqual(item['title'], '【テスト記事】Pythonで開発するAIツール')
        self.assertEqual(item['link'], 'https://example.com/article-1')
        self.assertEqual(item['description'], 'これはテスト記事の概要です。')
        self.assertEqual(item['bookmark_count'], 150)
        self.assertEqual(item['image_url'], 'https://example.com/thumb.jpg')
        self.assertEqual(item['domain'], 'example.com')
        self.assertEqual(item['category'], 'ai')
        self.assertIn('2026-08-08', item['date_formatted'])

    def test_parse_rss_empty_or_malformed(self):
        """壊れたXMLや空データを渡したときにエラーにならず安全に処理されるかテスト"""
        items_empty = parse_rss(b"", 'tech')
        self.assertEqual(items_empty, [])

        items_invalid = parse_rss(b"INVALID XML DATA", 'tech')
        self.assertEqual(items_invalid, [])

if __name__ == '__main__':
    unittest.main()
