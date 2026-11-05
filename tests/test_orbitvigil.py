"""Unit tests for OrbitVigil."""

import unittest
from orbitvigil.checker import LinkExtractor


class TestOrbitVigil(unittest.TestCase):
    def test_link_extractor(self):
        html = """
        <html>
            <body>
                <a href="/about">About Us</a>
                <a href="https://example.com/docs">Documentation</a>
                <a href="#section">Fragment Link</a>
                <a href="mailto:test@example.com">Email</a>
            </body>
        </html>
        """
        parser = LinkExtractor(base_url="https://example.com")
        parser.feed(html)

        self.assertIn("https://example.com/about", parser.links)
        self.assertIn("https://example.com/docs", parser.links)
        self.assertNotIn("https://example.com/#section", parser.links)
        self.assertNotIn("mailto:test@example.com", parser.links)


if __name__ == "__main__":
    unittest.main()
