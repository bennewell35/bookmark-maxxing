"""Local X MCP bookmark ingestion scaffold.

This module intentionally does not call the X API or MCP endpoints. It keeps the
first implementation slice limited to configuration, normalization, validation,
and deterministic Markdown output.
"""

from __future__ import annotations

from dataclasses import dataclass
from os import environ
from typing import Any, Mapping, Sequence

X_MCP_DEFAULT_URL = "https://api.x.com/mcp"
X_DOCS_MCP_DEFAULT_URL = "https://docs.x.com/mcp"


@dataclass(frozen=True)
class XMCPLocalConfig:
    """Environment-backed X MCP/API configuration."""

    mcp_server_url: str = X_MCP_DEFAULT_URL
    docs_mcp_server_url: str = X_DOCS_MCP_DEFAULT_URL
    bearer_token: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    redirect_uri: str | None = None
    xurl_client_id: str | None = None
    xurl_client_secret: str | None = None
    xurl_redirect_uri: str | None = None


@dataclass(frozen=True)
class NormalizedBookmark:
    """Normalized bookmark metadata used by Bookmark Maxxing."""

    source: str
    post_id: str
    source_url: str
    author_username: str
    author_name: str
    text: str
    created_at: str | None = None
    captured_at: str | None = None
    linked_urls: tuple[str, ...] = ()
    theme: str | None = None


def load_x_mcp_config(env: Mapping[str, str] | None = None) -> XMCPLocalConfig:
    """Load local X MCP/API configuration from environment variables."""

    values = environ if env is None else env
    return XMCPLocalConfig(
        mcp_server_url=values.get("X_MCP_SERVER_URL", X_MCP_DEFAULT_URL),
        docs_mcp_server_url=values.get("X_DOCS_MCP_SERVER_URL", X_DOCS_MCP_DEFAULT_URL),
        bearer_token=_empty_to_none(values.get("X_API_BEARER_TOKEN")),
        client_id=_empty_to_none(values.get("X_API_CLIENT_ID")),
        client_secret=_empty_to_none(values.get("X_API_CLIENT_SECRET")),
        redirect_uri=_empty_to_none(values.get("X_API_REDIRECT_URI")),
        xurl_client_id=_empty_to_none(values.get("CLIENT_ID")),
        xurl_client_secret=_empty_to_none(values.get("CLIENT_SECRET")),
        xurl_redirect_uri=_empty_to_none(values.get("REDIRECT_URI")),
    )


def normalize_x_bookmark(raw: Mapping[str, Any]) -> NormalizedBookmark:
    """Normalize one raw X bookmark-like object.

    Accepts a minimal X-shaped dictionary and preserves source attribution.
    Live MCP/API response parsing should adapt into this function instead of
    changing downstream outputs.
    """

    author = _mapping(raw.get("author"))
    author_username = _first_text(
        author.get("username"),
        author.get("screen_name"),
        raw.get("author_username"),
        raw.get("username"),
    )
    post_id = _first_text(raw.get("id"), raw.get("post_id"), raw.get("tweet_id"))
    source_url = _first_text(raw.get("url"), raw.get("source_url"))

    if not source_url and author_username and post_id:
        source_url = f"https://x.com/{author_username}/status/{post_id}"

    linked_urls = raw.get("linked_urls") or raw.get("urls") or ()
    if isinstance(linked_urls, str):
        linked_urls = (linked_urls,)

    return NormalizedBookmark(
        source="x",
        post_id=post_id,
        source_url=source_url,
        author_username=author_username,
        author_name=_first_text(author.get("name"), raw.get("author_name"), author_username),
        text=_first_text(raw.get("text"), raw.get("full_text"), raw.get("title_or_text")),
        created_at=_optional_text(raw.get("created_at")),
        captured_at=_optional_text(raw.get("captured_at")),
        linked_urls=tuple(str(url) for url in linked_urls if str(url).strip()),
        theme=_optional_text(raw.get("theme")),
    )


def validate_bookmark(bookmark: NormalizedBookmark) -> list[str]:
    """Return validation errors for normalized bookmark metadata."""

    errors: list[str] = []
    if bookmark.source != "x":
        errors.append("source must be x")
    if not bookmark.post_id:
        errors.append("post_id is required")
    if not bookmark.source_url:
        errors.append("source_url is required")
    if not bookmark.author_username:
        errors.append("author_username is required")
    if not bookmark.text:
        errors.append("text is required")
    return errors


def format_markdown_source_map(bookmarks: Sequence[NormalizedBookmark]) -> str:
    """Format normalized bookmarks as a deterministic Markdown source map."""

    lines = [
        "# X Bookmark Source Map",
        "",
        "| Source | Author | Theme | Text | Link |",
        "|---|---|---|---|---|",
    ]
    for bookmark in bookmarks:
        author = f"@{bookmark.author_username}"
        theme = bookmark.theme or "uncategorized"
        text = _truncate_for_table(bookmark.text)
        lines.append(
            f"| X | {author} | {theme} | {text} | [source]({bookmark.source_url}) |"
        )
    lines.append("")
    return "\n".join(lines)


def fetch_x_bookmarks_placeholder(_: XMCPLocalConfig) -> list[NormalizedBookmark]:
    """Placeholder for future live X MCP/API access.

    TODO: Implement after a local MCP/API client and auth flow are configured.
    This function must remain read-only and must not mutate X account state.
    """

    raise NotImplementedError(
        "Live X MCP/API ingestion is not implemented. Configure auth and add a read-only client first."
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _first_text(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _optional_text(value: Any) -> str | None:
    text = _first_text(value)
    return text or None


def _empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _truncate_for_table(value: str, limit: int = 96) -> str:
    cleaned = " ".join(value.split())
    if len(cleaned) <= limit:
        return _escape_table(cleaned)
    return _escape_table(cleaned[: limit - 3].rstrip() + "...")


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|")
