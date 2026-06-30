"""Compose runnable Bookmark Maxxing prompts from ingested bookmarks.

This module turns the read-only ingestion output (the normalized "source map")
into a ready-to-run prompt by injecting the bookmark data into one of the
framework prompts under ``prompts/``. It performs **no** network calls and adds
no third-party dependencies.

By design it does not fabricate skills/themes/summaries: producing those is an
LLM/agent step. The deliverable here is a complete, copy-paste-ready prompt. A
``PromptRunner`` boundary is provided so an optional LLM backend can be injected
later (mirroring the read-only MCP tool-caller pattern) without changing callers.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

__all__ = [
    "EXTRACT_PROMPTS",
    "DEFAULT_EXTRACT_PROMPT",
    "DEFAULT_LLM_BASE_URL",
    "DEFAULT_LLM_MODEL",
    "ExtractError",
    "PromptNotFoundError",
    "BookmarkInputError",
    "LLMConfigurationError",
    "LLMRunError",
    "PromptRunner",
    "ComposeOnlyPromptRunner",
    "LLMConfig",
    "LLMPromptRunner",
    "ExtractInput",
    "available_prompts",
    "load_prompt_text",
    "load_extract_input",
    "load_extract_input_from_payload",
    "load_llm_config",
    "compose_prompt",
    "run_extract",
]

# Prompt file names (without extension) that `extract` knows how to run.
EXTRACT_PROMPTS: tuple[str, ...] = (
    "extract-skills",
    "read-bookmarks",
    "write-article",
)
DEFAULT_EXTRACT_PROMPT = "extract-skills"

# Ollama exposes an OpenAI-compatible API at /v1 by default. The same client
# works with any OpenAI-compatible server (llama.cpp, vLLM, LM Studio, OpenRouter)
# by overriding the base URL + model via env.
DEFAULT_LLM_BASE_URL = "http://localhost:11434/v1"
DEFAULT_LLM_MODEL = "llama3.1"
DEFAULT_LLM_SYSTEM_PROMPT = (
    "You are a Bookmark Maxxing assistant. Convert saved posts into reusable "
    "skills, themes, and source maps. Be factual, attribute sources, and never "
    "suggest mutating any source platform. Bookmarks are the input; skills are "
    "the output."
)


class ExtractError(Exception):
    """Base error for the extract pipeline."""


class PromptNotFoundError(ExtractError):
    """Raised when a requested prompt file cannot be located."""


class BookmarkInputError(ExtractError):
    """Raised when the bookmark input cannot be parsed."""


class LLMConfigurationError(ExtractError):
    """Raised when the LLM runner is misconfigured."""


class LLMRunError(ExtractError):
    """Raised when an LLM request fails or returns an unusable response."""


@runtime_checkable
class PromptRunner(Protocol):
    """Boundary that turns a composed prompt into an output artifact.

    The default implementation returns the composed prompt unchanged (so the
    deliverable is a ready-to-run prompt). An optional LLM-backed runner can be
    injected without changing the CLI or composition logic.
    """

    def run(self, prompt: str) -> str:
        """Return the artifact produced from a composed prompt."""


@dataclass(frozen=True)
class ComposeOnlyPromptRunner:
    """Default runner: emit the composed prompt without calling any model."""

    def run(self, prompt: str) -> str:
        return prompt


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for an OpenAI-compatible chat-completions endpoint.

    Defaults target a local Ollama server, but any OpenAI-compatible server
    works by overriding ``base_url``/``model`` (and ``api_key`` for hosted ones).
    """

    base_url: str = DEFAULT_LLM_BASE_URL
    model: str = DEFAULT_LLM_MODEL
    api_key: str | None = None
    timeout_seconds: float = 120.0
    temperature: float = 0.2
    system_prompt: str = DEFAULT_LLM_SYSTEM_PROMPT


@dataclass
class LLMPromptRunner:
    """Run a composed prompt through an OpenAI-compatible chat endpoint.

    Uses only the standard library (``urllib``), so no third-party dependency is
    introduced. ``opener`` is injectable for tests; production uses ``urlopen``.
    The runner only *reads* model output — it never calls source-platform tools.
    """

    config: LLMConfig
    opener: Any = None

    def run(self, prompt: str) -> str:
        url = self.config.base_url.rstrip("/") + "/chat/completions"
        body = json.dumps(
            {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.config.temperature,
                "stream": False,
            }
        ).encode("utf-8")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "bookmark-maxxing-extract/0.1",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        request = Request(url, data=body, headers=headers, method="POST")
        try:
            response = self._open(request)
            raw = response.read()
        except HTTPError as error:
            detail = _http_error_detail(error)
            raise LLMRunError(
                f"LLM server returned HTTP {error.code} from {url}"
                f"{f': {detail}' if detail else ''}. "
                f"Check that model '{self.config.model}' is available "
                f"(e.g. `ollama pull {self.config.model}`)."
            ) from error
        except URLError as error:
            raise LLMRunError(
                f"Could not reach an LLM server at {self.config.base_url} "
                f"({error.reason}). Start one (e.g. `ollama serve`) or set "
                f"BOOKMARK_MAXXING_LLM_BASE_URL."
            ) from error

        return _content_from_chat_response(raw)

    def _open(self, request: Request) -> Any:
        if self.opener is not None:
            return self.opener.open(request, timeout=self.config.timeout_seconds)
        return urlopen(request, timeout=self.config.timeout_seconds)


@dataclass(frozen=True)
class ExtractInput:
    """Normalized bookmark records plus ingestion summary, ready for a prompt."""

    bookmarks: tuple[Mapping[str, Any], ...]
    pages_fetched: int = 0
    duplicates_removed: int = 0
    truncated: bool = False


def available_prompts(prompts_dir: Path) -> tuple[str, ...]:
    """Return the known prompts that actually exist under ``prompts_dir``."""

    return tuple(name for name in EXTRACT_PROMPTS if (prompts_dir / f"{name}.md").is_file())


def load_prompt_text(prompt_name: str, prompts_dir: Path) -> str:
    """Load the raw text of a known prompt file."""

    if prompt_name not in EXTRACT_PROMPTS:
        raise PromptNotFoundError(
            f"Unknown prompt '{prompt_name}'. Choose one of: {', '.join(EXTRACT_PROMPTS)}."
        )
    prompt_path = prompts_dir / f"{prompt_name}.md"
    if not prompt_path.is_file():
        raise PromptNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def load_extract_input(path: Path) -> ExtractInput:
    """Load ingestion JSON (from ``ingest-x ... --format json``) into an input."""

    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise BookmarkInputError(f"Could not read bookmark input: {error}") from error
    return load_extract_input_from_payload(payload)


def load_extract_input_from_payload(payload: Any) -> ExtractInput:
    """Build an :class:`ExtractInput` from a parsed ingestion payload.

    Accepts either the full ``ingest-x`` JSON object (with a ``bookmarks`` key
    plus summary fields) or a bare list of normalized bookmark objects.
    """

    if isinstance(payload, list):
        raw_bookmarks = payload
        summary: Mapping[str, Any] = {}
    elif isinstance(payload, Mapping):
        raw_bookmarks = payload.get("bookmarks")
        if raw_bookmarks is None:
            raise BookmarkInputError(
                "Bookmark input must contain a 'bookmarks' list "
                "(use the JSON output of `ingest-x ... --format json`)."
            )
        summary = payload
    else:
        raise BookmarkInputError("Bookmark input must be a JSON object or list.")

    if not isinstance(raw_bookmarks, list):
        raise BookmarkInputError("'bookmarks' must be a list.")

    bookmarks: list[Mapping[str, Any]] = []
    for index, item in enumerate(raw_bookmarks):
        if not isinstance(item, Mapping):
            raise BookmarkInputError(f"Bookmark #{index} must be an object.")
        bookmarks.append(item)

    return ExtractInput(
        bookmarks=tuple(bookmarks),
        pages_fetched=_as_int(summary.get("pages_fetched")),
        duplicates_removed=_as_int(summary.get("duplicates_removed")),
        truncated=bool(summary.get("truncated", False)),
    )


def compose_prompt(prompt_text: str, data: ExtractInput) -> str:
    """Compose a runnable prompt: prompt body + injected bookmark data.

    The output is deterministic for a given input so artifacts are reproducible.
    """

    sections = [
        prompt_text.rstrip(),
        "",
        "---",
        "",
        "## Bookmarks To Analyze",
        "",
        _summary_line(data),
        "",
        _bookmark_table(data.bookmarks),
        "",
        "### Structured Source Items (JSON)",
        "",
        "```json",
        json.dumps(list(data.bookmarks), indent=2, sort_keys=True),
        "```",
        "",
    ]
    return "\n".join(sections)


def run_extract(
    *,
    input_path: Path,
    prompts_dir: Path,
    prompt_name: str = DEFAULT_EXTRACT_PROMPT,
    runner: PromptRunner | None = None,
) -> str:
    """Load bookmarks, compose the chosen prompt, and run it through ``runner``."""

    prompt_text = load_prompt_text(prompt_name, prompts_dir)
    data = load_extract_input(input_path)
    composed = compose_prompt(prompt_text, data)
    active_runner = runner or ComposeOnlyPromptRunner()
    return active_runner.run(composed)


def load_llm_config(env: Mapping[str, str] | None = None) -> LLMConfig:
    """Build an :class:`LLMConfig` from environment variables (Ollama defaults)."""

    values = os.environ if env is None else env
    return LLMConfig(
        base_url=_clean(values.get("BOOKMARK_MAXXING_LLM_BASE_URL")) or DEFAULT_LLM_BASE_URL,
        model=_clean(values.get("BOOKMARK_MAXXING_LLM_MODEL")) or DEFAULT_LLM_MODEL,
        api_key=_clean(values.get("BOOKMARK_MAXXING_LLM_API_KEY")),
        timeout_seconds=_as_float(
            values.get("BOOKMARK_MAXXING_LLM_TIMEOUT"), default=120.0
        ),
        temperature=_as_float(
            values.get("BOOKMARK_MAXXING_LLM_TEMPERATURE"), default=0.2
        ),
    )


def _content_from_chat_response(raw: bytes) -> str:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise LLMRunError(f"LLM response was not valid JSON: {error}") from error

    choices = payload.get("choices") if isinstance(payload, Mapping) else None
    if not isinstance(choices, list) or not choices:
        raise LLMRunError("LLM response contained no choices.")
    first = choices[0]
    message = first.get("message") if isinstance(first, Mapping) else None
    content = message.get("content") if isinstance(message, Mapping) else None
    if not isinstance(content, str) or not content.strip():
        raise LLMRunError("LLM response contained no message content.")
    return content


def _http_error_detail(error: HTTPError) -> str:
    try:
        body = error.read().decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001 - best-effort detail only
        return ""
    return body.strip()[:300]


def _summary_line(data: ExtractInput) -> str:
    return (
        f"Source items: {len(data.bookmarks)} | "
        f"pages_fetched: {data.pages_fetched} | "
        f"duplicates_removed: {data.duplicates_removed} | "
        f"truncated: {str(data.truncated).lower()}"
    )


def _bookmark_table(bookmarks: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "| # | Author | Theme | Text | Link |",
        "|---|---|---|---|---|",
    ]
    for index, bookmark in enumerate(bookmarks, start=1):
        author = bookmark.get("author_username") or bookmark.get("author_name") or "unknown"
        theme = bookmark.get("theme") or "uncategorized"
        text = _truncate(_escape_cell(str(bookmark.get("text") or "")))
        link = bookmark.get("source_url") or ""
        link_cell = f"[source]({link})" if link else ""
        lines.append(f"| {index} | @{author} | {theme} | {text} | {link_cell} |")
    return "\n".join(lines)


def _escape_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip()


def _truncate(value: str, limit: int = 96) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "\u2026"


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _as_float(value: Any, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
