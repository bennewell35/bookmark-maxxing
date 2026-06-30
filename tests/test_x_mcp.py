import io
import json
from pathlib import Path
import unittest

from bookmark_maxxing.cli import main as cli_main
from bookmark_maxxing.x_mcp import (
    InMemoryXBookmarkClient,
    RateLimitInfo,
    XAuthConfigurationError,
    XBookmarkPage,
    XBookmarkRequest,
    X_DOCS_MCP_DEFAULT_URL,
    X_MCP_DEFAULT_URL,
    XRateLimitError,
    XReadOnlyViolationError,
    assert_read_only_client,
    format_ingestion_result_json,
    format_ingestion_result_markdown,
    format_markdown_source_map,
    ingest_x_bookmarks,
    load_fixture_pages,
    load_x_mcp_config,
    normalize_x_bookmark,
    validate_bookmark,
    validate_x_auth_config,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "x_bookmarks_pages.json"


class XMCPLocalConfigTests(unittest.TestCase):
    def test_load_config_defaults(self):
        config = load_x_mcp_config({})

        self.assertEqual(config.mcp_server_url, X_MCP_DEFAULT_URL)
        self.assertEqual(config.docs_mcp_server_url, X_DOCS_MCP_DEFAULT_URL)
        self.assertIsNone(config.user_id)
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

    def test_validate_auth_config_reports_missing_auth(self):
        with self.assertRaises(XAuthConfigurationError):
            validate_x_auth_config(load_x_mcp_config({}))

    def test_validate_auth_config_accepts_bearer_token(self):
        validate_x_auth_config(load_x_mcp_config({"X_API_BEARER_TOKEN": "token"}))


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


class XBookmarkIngestionTests(unittest.TestCase):
    def test_ingests_paginated_fixture_and_preserves_request_tokens(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
            pages = load_fixture_pages(json.load(fixture_file))
        client = InMemoryXBookmarkClient(pages)

        result = ingest_x_bookmarks(
            client,
            load_x_mcp_config({}),
            request=XBookmarkRequest(user_id="42", max_results=2),
            require_auth=False,
        )

        self.assertEqual(result.pages_fetched, 2)
        self.assertEqual(len(result.bookmarks), 3)
        self.assertFalse(result.truncated)
        self.assertEqual(client.requests[0].pagination_token, None)
        self.assertEqual(client.requests[1].pagination_token, "page-2")
        self.assertEqual(result.bookmarks[0].author_username, "ben_ai_eng")
        self.assertEqual(result.bookmarks[0].source_url, "https://x.com/ben_ai_eng/status/1")

    def test_rate_limit_response_raises_clear_error(self):
        client = InMemoryXBookmarkClient(
            [
                XBookmarkPage(
                    items=(),
                    status_code=429,
                    rate_limit=RateLimitInfo(limit=15, remaining=0, retry_after_seconds=60),
                )
            ]
        )

        with self.assertRaises(XRateLimitError) as error:
            ingest_x_bookmarks(client, load_x_mcp_config({"X_API_BEARER_TOKEN": "token"}))

        self.assertEqual(error.exception.rate_limit.retry_after_seconds, 60)

    def test_malformed_bookmark_payload_is_reported_not_exported(self):
        client = InMemoryXBookmarkClient(
            [
                XBookmarkPage(
                    items=(
                        {"id": "missing-text", "author_username": "builder"},
                        "not-an-object",
                    )
                )
            ]
        )

        result = ingest_x_bookmarks(client, load_x_mcp_config({}), require_auth=False)

        self.assertEqual(result.bookmarks, ())
        self.assertEqual(len(result.validation_errors), 2)
        self.assertIn("text is required", result.validation_errors[0].errors)
        self.assertIn("payload item must be an object", result.validation_errors[1].errors)

    def test_duplicate_bookmarks_are_removed_by_post_id(self):
        client = InMemoryXBookmarkClient(
            [
                XBookmarkPage(
                    items=(
                        {
                            "id": "1",
                            "text": "First copy",
                            "author_username": "builder",
                            "url": "https://x.com/builder/status/1",
                        },
                        {
                            "id": "1",
                            "text": "Second copy",
                            "author_username": "builder",
                            "url": "https://x.com/builder/status/1",
                        },
                    )
                )
            ]
        )

        result = ingest_x_bookmarks(client, load_x_mcp_config({}), require_auth=False)

        self.assertEqual(len(result.bookmarks), 1)
        self.assertEqual(result.duplicates_removed, 1)
        self.assertEqual(result.bookmarks[0].text, "First copy")

    def test_markdown_and_json_exports_are_deterministic(self):
        client = InMemoryXBookmarkClient(
            [
                XBookmarkPage(
                    items=(
                        {
                            "id": "1",
                            "text": "A saved idea about source maps.",
                            "author_username": "builder",
                            "author_name": "Builder",
                            "url": "https://x.com/builder/status/1",
                            "theme": "source attribution",
                        },
                    )
                )
            ]
        )
        result = ingest_x_bookmarks(client, load_x_mcp_config({}), require_auth=False)

        markdown = format_ingestion_result_markdown(result)
        json_output = format_ingestion_result_json(result)

        self.assertIn("duplicates_removed=0", markdown)
        self.assertIn("@builder", markdown)
        self.assertIn('"pages_fetched": 1', json_output)
        self.assertIn('"author_username": "builder"', json_output)

    def test_client_boundary_rejects_mutation_methods(self):
        class UnsafeClient:
            def fetch_bookmarks_page(self, request):
                return XBookmarkPage(items=())

            def like(self, post_id):
                return post_id

        with self.assertRaises(XReadOnlyViolationError):
            assert_read_only_client(UnsafeClient())


class XBookmarkCLITests(unittest.TestCase):
    def test_dry_run_cli_reads_fixture_and_outputs_json(self):
        output = io.StringIO()

        exit_code = cli_main(
            ["ingest-x", "--dry-run", "--input", str(FIXTURE_PATH), "--format", "json"],
            stdout=output,
        )

        self.assertEqual(exit_code, 0)
        self.assertIn('"pages_fetched": 2', output.getvalue())
        self.assertIn('"author_username": "ben_ai_eng"', output.getvalue())


if __name__ == "__main__":
    unittest.main()
