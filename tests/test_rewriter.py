import unittest

from auto_url_fixer.config import Rule, load_config
from auto_url_fixer.rewriter import rewrite_text, rewrite_url


class RewriteUrlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rules = load_config().enabled_rules

    def test_rewrites_twitter(self) -> None:
        self.assertEqual(
            rewrite_url("https://twitter.com/example/status/123", self.rules),
            "https://fxtwitter.com/example/status/123",
        )

    def test_rewrites_x(self) -> None:
        self.assertEqual(
            rewrite_url("https://x.com/example/status/123?s=20", self.rules),
            "https://fxtwitter.com/example/status/123?s=20",
        )

    def test_rewrites_multiple_urls_in_text(self) -> None:
        rewritten, changed = rewrite_text(
            "A https://www.instagram.com/p/abc and https://reddit.com/r/test/comments/1",
            self.rules,
        )

        self.assertTrue(changed)
        self.assertEqual(
            rewritten,
            "A https://ddinstagram.com/p/abc and https://rxddit.com/r/test/comments/1",
        )

    def test_flattens_single_markdown_link_to_raw_url(self) -> None:
        rewritten, changed = rewrite_text(
            "[w](https://x.com/1nCoin/status/2064708177816657987?s=20)",
            self.rules,
        )

        self.assertTrue(changed)
        self.assertEqual(
            rewritten,
            "https://fxtwitter.com/1nCoin/status/2064708177816657987?s=20",
        )

    def test_preserves_trailing_punctuation(self) -> None:
        rewritten, changed = rewrite_text(
            "See (https://www.tiktok.com/@name/video/123).",
            self.rules,
        )

        self.assertTrue(changed)
        self.assertEqual(rewritten, "See (https://tnktok.com/@name/video/123).")

    def test_rewrites_tumblr_subdomain(self) -> None:
        self.assertEqual(
            rewrite_url("https://staff.tumblr.com/post/123", self.rules),
            "https://staff.tpmblr.com/post/123",
        )

    def test_ignores_unknown_hosts(self) -> None:
        url = "https://example.com/post/1"
        self.assertEqual(rewrite_url(url, self.rules), url)

    def test_disabled_candidate_rule_can_be_enabled_manually(self) -> None:
        rules = (
            Rule(
                name="Reddit to rxyddit",
                enabled=True,
                hosts=("reddit.com",),
                target_host="rxyddit.com",
            ),
        )
        self.assertEqual(
            rewrite_url("https://reddit.com/r/test/comments/1", rules),
            "https://rxyddit.com/r/test/comments/1",
        )


if __name__ == "__main__":
    unittest.main()
