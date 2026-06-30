"""Read-only X MCP bookmark ingestion boundary.

This module intentionally does not call the X API or MCP endpoints. Live X
transport must plug in behind ``XReadOnlyBookmarkClient`` and provide only the
read method defined by that protocol.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from os import environ
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

X_MCP_DEFAULT_URL = "https://api.x.com/mcp"
X_DOCS_MCP_DEFAULT_URL = "https://docs.x.com/mcp"
X_API_DEFAULT_BASE_URL = "https://api.x.com/2"
DEFAULT_PAGE_SIZE = 100
READ_ONLY_CLIENT_METHODS = frozenset({"fetch_bookmarks_page"})
MUTATING_CLIENT_METHOD_NAMES = frozenset(
    {
        "block",
        "delete",
        "delete_bookmark",
        "follow",
        "like",
        "mute",
        "reply",
        "repost",
        "retweet",
        "unbookmark",
        "unfollow",
        "unlike",
    }
)


class XMCPError(Exception):
    """Base error for X MCP ingestion boundaries."""


class XAuthConfigurationError(XMCPError):
    """Raised when read-only ingestion is requested without auth config."""


class XReadOnlyViolationError(XMCPError):
    """Raised when a client exposes obvious account-mutation methods."""


class XRateLimitError(XMCPError):
    """Raised when a page response represents a rate-limit stop."""

    def __init__(self, message: str, rate_limit: "RateLimitInfo | None" = None):
        super().__init__(message)
        self.rate_limit = rate_limit


class XBookmarkPayloadError(XMCPError):
    """Raised when a fixture or client page shape is not usable."""


@dataclass(frozen=True)
class XMCPLocalConfig:
    """Environment-backed X MCP/API configuration."""

    mcp_server_url: str = X_MCP_DEFAULT_URL
    docs_mcp_server_url: str = X_DOCS_MCP_DEFAULT_URL
    api_base_url: str = X_API_DEFAULT_BASE_URL
    user_id: str | None = None
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


@dataclass(frozen=True)
class XBookmarkRequest:
    """Read-only bookmark page request."""

    user_id: str | None = None
    pagination_token: str | None = None
    max_results: int = DEFAULT_PAGE_SIZE

    def next_page(self, pagination_token: str) -> "XBookmarkRequest":
        return XBookmarkRequest(
            user_id=self.user_id,
            pagination_token=pagination_token,
            max_results=self.max_results,
        )


@dataclass(frozen=True)
class RateLimitInfo:
    """Rate-limit metadata parsed from response headers or fixtures."""

    limit: int | None = None
    remaining: int | None = None
    reset_epoch: int | None = None
    retry_after_seconds: int | None = None

    @classmethod
    def from_headers(cls, headers: Mapping[str, Any] | None) -> "RateLimitInfo":
        values = {str(key).lower(): value for key, value in (headers or {}).items()}
        return cls(
            limit=_optional_int(values.get("x-rate-limit-limit")),
            remaining=_optional_int(values.get("x-rate-limit-remaining")),
            reset_epoch=_optional_int(values.get("x-rate-limit-reset")),
            retry_after_seconds=_optional_int(values.get("retry-after")),
        )

    @property
    def is_exhausted(self) -> bool:
        return self.remaining == 0 or self.retry_after_seconds is not None


@dataclass(frozen=True)
class XBookmarkPage:
    """One read-only page of raw bookmark payloads."""

    items: tuple[Any, ...]
    next_token: str | None = None
    rate_limit: RateLimitInfo = field(default_factory=RateLimitInfo)
    status_code: int = 200


@dataclass(frozen=True)
class BookmarkValidationIssue:
    """Validation issue for one raw or normalized bookmark item."""

    item_index: int
    post_id: str | None
    errors: tuple[str, ...]


@dataclass(frozen=True)
class XBookmarkIngestionResult:
    """Structured result returned by the ingestion pipeline."""

    bookmarks: tuple[NormalizedBookmark, ...]
    validation_errors: tuple[BookmarkValidationIssue, ...] = ()
    pages_fetched: int = 0
    duplicates_removed: int = 0
    rate_limits: tuple[RateLimitInfo, ...] = ()
    next_token: str | None = None
    truncated: bool = False


@runtime_checkable
class XReadOnlyBookmarkClient(Protocol):
    """Client boundary for read-only X bookmark ingestion."""

    def fetch_bookmarks_page(self, request: XBookmarkRequest) -> XBookmarkPage:
        """Fetch a single page of bookmarks without mutating account state."""


@dataclass
class InMemoryXBookmarkClient:
    """Fixture-backed read-only client used by tests and dry-run CLI flows."""

    pages: Sequence[XBookmarkPage]
    requests: list[XBookmarkRequest] = field(default_factory=list)

    def fetch_bookmarks_page(self, request: XBookmarkRequest) -> XBookmarkPage:
        self.requests.append(request)
        page_index = len(self.requests) - 1
        if page_index >= len(self.pages):
            return XBookmarkPage(items=())
        return self.pages[page_index]


@dataclass(frozen=True)
class XAPIReadOnlyBookmarkClient:
    """Read-only X API transport for authenticated-user bookmarks.

    This class only issues GET requests. Tests inject a fake opener; production
    use must pass credentials through environment-backed config.
    """

    config: XMCPLocalConfig
    timeout_seconds: float = 30.0
    opener: Any = None

    def __post_init__(self) -> None:
        validate_x_api_transport_config(self.config, require_user_id=False)

    def fetch_bookmarks_page(self, request: XBookmarkRequest) -> XBookmarkPage:
        user_id = request.user_id or self.config.user_id
        if user_id is None:
            raise XAuthConfigurationError("X_API_USER_ID is required for live bookmark fetches.")

        url = self._bookmarks_url(user_id, request)
        http_request = Request(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.config.bearer_token}",
                "User-Agent": "bookmark-maxxing-readonly/0.1",
            },
            method="GET",
        )

        try:
            response = self._open(http_request)
            return _page_from_x_api_response(response)
        except HTTPError as error:
            if error.code == 429:
                return XBookmarkPage(
                    items=(),
                    rate_limit=RateLimitInfo.from_headers(error.headers),
                    status_code=429,
                )
            raise XBookmarkPayloadError(f"X API returned HTTP {error.code}") from error

    def _open(self, request: Request) -> Any:
        if self.opener is not None:
            return self.opener.open(request, timeout=self.timeout_seconds)
        return urlopen(request, timeout=self.timeout_seconds)

    def _bookmarks_url(self, user_id: str, request: XBookmarkRequest) -> str:
        query = {
            "expansions": "author_id",
            "max_results": str(_clamp_page_size(request.max_results)),
            "tweet.fields": "author_id,created_at,entities,public_metrics",
            "user.fields": "name,username",
        }
        if request.pagination_token:
            query["pagination_token"] = request.pagination_token
        base_url = self.config.api_base_url.rstrip("/")
        return f"{base_url}/users/{user_id}/bookmarks?{urlencode(query)}"


def load_x_mcp_config(env: Mapping[str, str] | None = None) -> XMCPLocalConfig:
    """Load local X MCP/API configuration from environment variables."""

    values = environ if env is None else env
    return XMCPLocalConfig(
        mcp_server_url=values.get("X_MCP_SERVER_URL", X_MCP_DEFAULT_URL),
        docs_mcp_server_url=values.get("X_DOCS_MCP_SERVER_URL", X_DOCS_MCP_DEFAULT_URL),
        api_base_url=values.get("X_API_BASE_URL", X_API_DEFAULT_BASE_URL),
        user_id=_empty_to_none(values.get("X_API_USER_ID")),
        bearer_token=_empty_to_none(values.get("X_API_BEARER_TOKEN")),
        client_id=_empty_to_none(values.get("X_API_CLIENT_ID")),
        client_secret=_empty_to_none(values.get("X_API_CLIENT_SECRET")),
        redirect_uri=_empty_to_none(values.get("X_API_REDIRECT_URI")),
        xurl_client_id=_empty_to_none(values.get("CLIENT_ID")),
        xurl_client_secret=_empty_to_none(values.get("CLIENT_SECRET")),
        xurl_redirect_uri=_empty_to_none(values.get("REDIRECT_URI")),
    )


def validate_x_auth_config(config: XMCPLocalConfig) -> None:
    """Validate that a future live read-only client has auth material."""

    has_bearer = config.bearer_token is not None
    has_oauth = config.client_id is not None and config.client_secret is not None
    has_xurl_oauth = (
        config.xurl_client_id is not None and config.xurl_client_secret is not None
    )
    if has_bearer or has_oauth or has_xurl_oauth:
        return
    raise XAuthConfigurationError(
        "Missing X auth configuration. Set a bearer token or OAuth client credentials locally."
    )


def validate_x_api_transport_config(
    config: XMCPLocalConfig,
    *,
    require_user_id: bool = True,
) -> None:
    """Validate direct read-only X API transport configuration."""

    if require_user_id and config.user_id is None:
        raise XAuthConfigurationError("X_API_USER_ID is required for live bookmark fetches.")
    if config.bearer_token is None:
        raise XAuthConfigurationError(
            "X_API_BEARER_TOKEN is required for direct read-only X API bookmark fetches."
        )


def assert_read_only_client(client: object) -> None:
    """Reject clients that expose obvious account-mutation methods."""

    missing = [
        name
        for name in READ_ONLY_CLIENT_METHODS
        if not callable(getattr(client, name, None))
    ]
    if missing:
        raise XBookmarkPayloadError(f"Client is missing read-only method(s): {', '.join(missing)}")

    exposed = [
        name
        for name in sorted(MUTATING_CLIENT_METHOD_NAMES)
        if callable(getattr(client, name, None))
    ]
    if exposed:
        raise XReadOnlyViolationError(
            "X bookmark clients must not expose mutation methods: " + ", ".join(exposed)
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

    linked_urls = _extract_linked_urls(raw.get("linked_urls") or raw.get("urls") or ())
    if isinstance(linked_urls, str):
        linked_urls = (linked_urls,)

    return NormalizedBookmark(
        source="x",
        post_id=post_id,
        source_url=source_url,
        author_username=author_username,
        author_name=_first_text(
            author.get("name"),
            raw.get("author_name"),
            author_username,
        ),
        text=_first_text(raw.get("text"), raw.get("full_text"), raw.get("title_or_text")),
        created_at=_optional_text(raw.get("created_at")),
        captured_at=_optional_text(raw.get("captured_at")),
        linked_urls=tuple(str(url).strip() for url in linked_urls if str(url).strip()),
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


def format_ingestion_result_markdown(result: XBookmarkIngestionResult) -> str:
    """Format an ingestion result as a Markdown source map with summary."""

    summary = (
        f"<!-- pages_fetched={result.pages_fetched} "
        f"duplicates_removed={result.duplicates_removed} "
        f"truncated={str(result.truncated).lower()} -->"
    )
    lines = [
        summary,
        format_markdown_source_map(result.bookmarks).rstrip(),
    ]
    if result.validation_errors:
        lines.extend(["", "## Validation Issues", ""])
        for issue in result.validation_errors:
            post_id = issue.post_id or "unknown"
            lines.append(
                f"- item {issue.item_index} ({post_id}): {'; '.join(issue.errors)}"
            )
    lines.append("")
    return "\n".join(lines)


def format_ingestion_result_json(result: XBookmarkIngestionResult) -> str:
    """Format an ingestion result as deterministic JSON."""

    payload = {
        "bookmarks": [_bookmark_to_dict(bookmark) for bookmark in result.bookmarks],
        "duplicates_removed": result.duplicates_removed,
        "next_token": result.next_token,
        "pages_fetched": result.pages_fetched,
        "truncated": result.truncated,
        "validation_errors": [
            {
                "errors": list(issue.errors),
                "item_index": issue.item_index,
                "post_id": issue.post_id,
            }
            for issue in result.validation_errors
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def ingest_x_bookmarks(
    client: XReadOnlyBookmarkClient,
    config: XMCPLocalConfig | None = None,
    *,
    request: XBookmarkRequest | None = None,
    max_pages: int = 10,
    require_auth: bool = True,
) -> XBookmarkIngestionResult:
    """Fetch, normalize, validate, and deduplicate X bookmarks.

    The client boundary is read-only and fixture-friendly. Live transport should
    be added behind the protocol without changing this pipeline.
    """

    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    active_config = config or load_x_mcp_config()
    if require_auth:
        validate_x_auth_config(active_config)
    assert_read_only_client(client)

    active_request = request or XBookmarkRequest(user_id=active_config.user_id)
    pages_fetched = 0
    next_token: str | None = None
    rate_limits: list[RateLimitInfo] = []
    bookmarks: list[NormalizedBookmark] = []
    validation_errors: list[BookmarkValidationIssue] = []
    items_seen = 0

    while pages_fetched < max_pages:
        page = client.fetch_bookmarks_page(active_request)
        _raise_for_page_status(page)
        pages_fetched += 1
        next_token = page.next_token
        rate_limits.append(page.rate_limit)

        for raw_item in page.items:
            item_index = items_seen
            items_seen += 1
            if not isinstance(raw_item, Mapping):
                validation_errors.append(
                    BookmarkValidationIssue(
                        item_index=item_index,
                        post_id=None,
                        errors=("payload item must be an object",),
                    )
                )
                continue

            bookmark = normalize_x_bookmark(raw_item)
            errors = validate_bookmark(bookmark)
            if errors:
                validation_errors.append(
                    BookmarkValidationIssue(
                        item_index=item_index,
                        post_id=bookmark.post_id or None,
                        errors=tuple(errors),
                    )
                )
                continue
            bookmarks.append(bookmark)

        if not next_token:
            break
        active_request = active_request.next_page(next_token)

    deduped = deduplicate_bookmarks(bookmarks)
    truncated = next_token is not None and pages_fetched >= max_pages
    return XBookmarkIngestionResult(
        bookmarks=tuple(deduped),
        validation_errors=tuple(validation_errors),
        pages_fetched=pages_fetched,
        duplicates_removed=len(bookmarks) - len(deduped),
        rate_limits=tuple(rate_limits),
        next_token=next_token if truncated else None,
        truncated=truncated,
    )


def deduplicate_bookmarks(
    bookmarks: Sequence[NormalizedBookmark],
) -> tuple[NormalizedBookmark, ...]:
    """Remove duplicate bookmarks while preserving first-seen order."""

    seen: set[str] = set()
    deduped: list[NormalizedBookmark] = []
    for bookmark in bookmarks:
        key = bookmark.post_id or bookmark.source_url
        if key in seen:
            continue
        seen.add(key)
        deduped.append(bookmark)
    return tuple(deduped)


def load_fixture_pages(payload: Any) -> tuple[XBookmarkPage, ...]:
    """Load fixture-backed pages from JSON-compatible payloads."""

    if isinstance(payload, list):
        return (XBookmarkPage(items=tuple(payload)),)
    if not isinstance(payload, Mapping):
        raise XBookmarkPayloadError("Fixture payload must be an object or list")

    pages_payload = payload.get("pages")
    if pages_payload is None:
        return (_page_from_mapping(payload),)
    if not isinstance(pages_payload, list):
        raise XBookmarkPayloadError("Fixture pages must be a list")
    return tuple(_page_from_mapping(page) for page in pages_payload)


def fetch_x_bookmarks_placeholder(_: XMCPLocalConfig) -> list[NormalizedBookmark]:
    """Placeholder for future live X MCP/API access.

    TODO: Implement after a local MCP/API client and auth flow are configured.
    This function must remain read-only and must not mutate X account state.
    """

    raise NotImplementedError(
        "Live X MCP/API ingestion is not implemented. Configure auth and add a read-only client first."
    )


def _page_from_mapping(page: Any) -> XBookmarkPage:
    if not isinstance(page, Mapping):
        raise XBookmarkPayloadError("Fixture page must be an object")

    items = page.get("items", page.get("data", page.get("bookmarks", ())))
    if not isinstance(items, list):
        raise XBookmarkPayloadError("Fixture page items must be a list")

    metadata = _mapping(page.get("meta"))
    headers = _mapping(page.get("headers"))
    return XBookmarkPage(
        items=tuple(items),
        next_token=_optional_text(
            page.get("next_token")
            or page.get("pagination_token")
            or metadata.get("next_token")
            or metadata.get("pagination_token")
        ),
        rate_limit=RateLimitInfo.from_headers(headers),
        status_code=_optional_int(page.get("status_code")) or 200,
    )


def _page_from_x_api_response(response: Any) -> XBookmarkPage:
    status_code = _response_status_code(response)
    headers = _response_headers(response)
    raw_body = response.read()
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (AttributeError, json.JSONDecodeError) as error:
        raise XBookmarkPayloadError("X API response body was not valid JSON") from error
    return _page_from_x_api_payload(payload, headers, status_code)


def _page_from_x_api_payload(
    payload: Any,
    headers: Mapping[str, Any] | None = None,
    status_code: int = 200,
) -> XBookmarkPage:
    if not isinstance(payload, Mapping):
        raise XBookmarkPayloadError("X API payload must be an object")

    data = payload.get("data") or []
    if not isinstance(data, list):
        raise XBookmarkPayloadError("X API payload data must be a list")

    users_by_id = _users_by_id(payload.get("includes"))
    items = tuple(_tweet_to_raw_bookmark(tweet, users_by_id) for tweet in data)
    metadata = _mapping(payload.get("meta"))
    return XBookmarkPage(
        items=items,
        next_token=_optional_text(metadata.get("next_token")),
        rate_limit=RateLimitInfo.from_headers(headers),
        status_code=status_code,
    )


def _tweet_to_raw_bookmark(
    tweet: Any,
    users_by_id: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, Any]:
    if not isinstance(tweet, Mapping):
        raise XBookmarkPayloadError("X API tweet item must be an object")

    author = users_by_id.get(_first_text(tweet.get("author_id")), {})
    username = _first_text(author.get("username"), tweet.get("author_username"))
    post_id = _first_text(tweet.get("id"))
    source_url = f"https://x.com/{username}/status/{post_id}" if username and post_id else ""
    return {
        "author": {
            "name": _first_text(author.get("name"), username),
            "username": username,
        },
        "created_at": _optional_text(tweet.get("created_at")),
        "id": post_id,
        "linked_urls": _extract_linked_urls(_mapping(tweet.get("entities")).get("urls") or ()),
        "source_url": source_url,
        "text": _first_text(tweet.get("text")),
    }


def _users_by_id(includes: Any) -> Mapping[str, Mapping[str, Any]]:
    users = _mapping(includes).get("users") or []
    if not isinstance(users, list):
        return {}
    return {
        _first_text(user.get("id")): user
        for user in users
        if isinstance(user, Mapping) and _first_text(user.get("id"))
    }


def _response_status_code(response: Any) -> int:
    if callable(getattr(response, "getcode", None)):
        return int(response.getcode())
    return _optional_int(getattr(response, "status", None)) or 200


def _response_headers(response: Any) -> Mapping[str, Any]:
    headers = getattr(response, "headers", None)
    if headers is None and callable(getattr(response, "info", None)):
        headers = response.info()
    if isinstance(headers, Mapping):
        return headers
    if callable(getattr(headers, "items", None)):
        return dict(headers.items())
    return {}


def _raise_for_page_status(page: XBookmarkPage) -> None:
    if page.status_code == 429:
        raise XRateLimitError("X bookmark ingestion hit a rate limit", page.rate_limit)
    if page.status_code < 200 or page.status_code >= 300:
        raise XBookmarkPayloadError(f"Unexpected X bookmark page status: {page.status_code}")


def _extract_linked_urls(value: Any) -> tuple[str, ...] | str:
    if isinstance(value, list):
        urls: list[str] = []
        for item in value:
            if isinstance(item, Mapping):
                url = _first_text(item.get("expanded_url"), item.get("url"))
            else:
                url = _first_text(item)
            if url:
                urls.append(url)
        return tuple(urls)
    return value


def _bookmark_to_dict(bookmark: NormalizedBookmark) -> dict[str, Any]:
    return {
        "author_name": bookmark.author_name,
        "author_username": bookmark.author_username,
        "captured_at": bookmark.captured_at,
        "created_at": bookmark.created_at,
        "linked_urls": list(bookmark.linked_urls),
        "post_id": bookmark.post_id,
        "source": bookmark.source,
        "source_url": bookmark.source_url,
        "text": bookmark.text,
        "theme": bookmark.theme,
    }


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


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _clamp_page_size(value: int) -> int:
    return min(max(int(value), 1), 100)


def _truncate_for_table(value: str, limit: int = 96) -> str:
    cleaned = " ".join(value.split())
    if len(cleaned) <= limit:
        return _escape_table(cleaned)
    return _escape_table(cleaned[: limit - 3].rstrip() + "...")


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|")
