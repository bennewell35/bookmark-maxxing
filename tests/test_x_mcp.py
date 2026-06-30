import unittest

from bookmark_maxxing.x_mcp import (
    X_DOCS_MCP_DEFAULT_URL,
    X_MCP_DEFAULT_URL,
    format_markdown_source_map,
    load_x_mcp_config,
    normalize_x_bookmark,
    validate_bookmark,
)


class XMCPLocalConfigTests(unittest.TestCase):
    def test_load_config_defaults(self):
        config = load_x_mcp_config({})

        self.assertEqual(config.mcp_server_url, X_MCP_DEFAULT_URL)
        self.assertEqual(config.docs_mcp_server_url, X_DOCS_MCP_DEFAULT_URL)
        self.assertIsNone(config.bearer_token)

    def test_load_config_strips_empty_secret_values(self):
        config = load_x_mcp_config({"X_API_BEARER_TOKEN": "   "})

        self.assertIsNone(config.bearer_token)

    def test_load_config_supports_xurl_bridge_env(self):
        config = load_x_mcp_config(
            {
                "CLIENT_ID": "client-id",
                "CLIENT_SECRET": "client-secret",
                "REDIRECT_URI": "http://localhost:8080/callback",
            }
        )

        self.assertEqual(config.xurl_client_id, "client-id")
        self.assertEqual(config.xurl_client_secret, "client-secret")
        self.assertEqual(config.xurl_redirect_uri, "http://localhost:8080/callback")


class XBookmarkNormalizationTests(unittest.TestCase):
    def test_normalizes_minimal_bookmark_and_builds_source_url(self):
        bookmark = normalize_x_bookmark(
            {
                "id": "2071272699251298483",
                "text": "don't collect bookmarks. collect skills.",
                "author": {"username": "ben_ai_eng", "name": "Ben Newell"},
                "created_at": "2026-06-28T16:41:08Z",
                "theme": "bookmark maxxing",
            }
        )

        self.assertEqual(bookmark.source, "x")
        self.assertEqual(bookmark.post_id, "2071272699251298483")
        self.assertEqual(bookmark.author_username, "ben_ai_eng")
        self.assertEqual(bookmark.author_name, "Ben Newell")
        self.assertEqual(
            bookmark.source_url,
            "https://x.com/ben_ai_eng/status/2071272699251298483",
        )
        self.assertEqual(bookmark.theme, "bookmark maxxing")
        self.assertEqual(validate_bookmark(bookmark), [])

    def test_validation_reports_missing_required_fields(self):
        bookmark = normalize_x_bookmark({"author": {}, "text": ""})

        self.assertEqual(
            validate_bookmark(bookmark),
            [
                "post_id is required",
                "source_url is required",
                "author_username is required",
                "text is required",
            ],
        )

    def test_markdown_source_map_preserves_attribution(self):
        bookmark = normalize_x_bookmark(
            {
                "id": "1",
                "text": "A saved idea about agent memory.",
                "author_username": "mvanhorn",
                "author_name": "Matt Van Horn",
                "url": "https://x.com/mvanhorn/status/1",
                "theme": "memory discipline",
            }
        )

        markdown = format_markdown_source_map([bookmark])

        self.assertIn("# X Bookmark Source Map", markdown)
        self.assertIn("@mvanhorn", markdown)
        self.assertIn("memory discipline", markdown)
        self.assertIn("[source](https://x.com/mvanhorn/status/1)", markdown)


if __name__ == "__main__":
    unittest.main()
