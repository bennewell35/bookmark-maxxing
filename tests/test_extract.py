import io
import json
import unittest
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError, URLError

from bookmark_maxxing.cli import main as cli_main
from bookmark_maxxing.extract import (
    DEFAULT_EXTRACT_PROMPT,
    DEFAULT_LLM_BASE_URL,
    DEFAULT_LLM_MODEL,
    BookmarkInputError,
    ComposeOnlyPromptRunner,
    ExtractInput,
    LLMConfig,
    LLMPromptRunner,
    LLMRunError,
    PromptNotFoundError,
    compose_prompt,
    load_extract_input_from_payload,
    load_llm_config,
    load_prompt_text,
    run_extract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = REPO_ROOT / "prompts"

SAMPLE_PAYLOAD = {
    "bookmarks": [
        {
            "author_name": "Ben (AI eng)",
            "author_username": "ben_ai_eng",
            "source": "x",
            "source_url": "https://x.com/ben_ai_eng/status/1",
            "text": "Bookmarks are the input. Skills are the output.",
            "theme": None,
        },
        {
            "author_name": "Systems Builder",
            "author_username": "systems_builder",
            "source": "x",
            "source_url": "https://x.com/systems_builder/status/2",
            "text": "Design repeatable systems, not better prompts.",
            "theme": "operating loops",
        },
    ],
    "pages_fetched": 2,
    "duplicates_removed": 0,
    "truncated": False,
}


def _write_payload(tmp_path: Path, payload) -> Path:
    target = tmp_path / "bookmarks.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


class FakeChatResponse:
    def __init__(self, content):
        self._content = content

    def read(self):
        return json.dumps(
            {"choices": [{"message": {"role": "assistant", "content": self._content}}]}
        ).encode("utf-8")


class RecordingOpener:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return self.response


class LoadInputTests(unittest.TestCase):
    def test_accepts_full_ingestion_object(self):
        data = load_extract_input_from_payload(SAMPLE_PAYLOAD)
        self.assertEqual(len(data.bookmarks), 2)
        self.assertEqual(data.pages_fetched, 2)
        self.assertFalse(data.truncated)

    def test_accepts_bare_list(self):
        data = load_extract_input_from_payload(SAMPLE_PAYLOAD["bookmarks"])
        self.assertEqual(len(data.bookmarks), 2)
        self.assertEqual(data.pages_fetched, 0)

    def test_missing_bookmarks_key_raises(self):
        with self.assertRaises(BookmarkInputError):
            load_extract_input_from_payload({})

    def test_non_object_item_raises(self):
        with self.assertRaises(BookmarkInputError):
            load_extract_input_from_payload({"bookmarks": ["not-an-object"]})


class LoadPromptTests(unittest.TestCase):
    def test_loads_known_prompt(self):
        text = load_prompt_text("extract-skills", PROMPTS_DIR)
        self.assertIn("Extract Skills", text)

    def test_unknown_prompt_name_raises(self):
        with self.assertRaises(PromptNotFoundError):
            load_prompt_text("summarize-everything", PROMPTS_DIR)

    def test_missing_prompt_file_raises(self):
        with self.assertRaises(PromptNotFoundError):
            load_prompt_text("extract-skills", Path("/tmp/does-not-exist-xyz"))


class ComposePromptTests(unittest.TestCase):
    def setUp(self):
        self.data = load_extract_input_from_payload(SAMPLE_PAYLOAD)

    def test_injects_prompt_body_and_bookmarks(self):
        prompt_text = load_prompt_text("extract-skills", PROMPTS_DIR)
        composed = compose_prompt(prompt_text, self.data)
        self.assertIn("Extract Skills", composed)
        self.assertIn("## Bookmarks To Analyze", composed)
        self.assertIn("@ben_ai_eng", composed)
        self.assertIn("operating loops", composed)
        self.assertIn("Source items: 2 | pages_fetched: 2", composed)
        self.assertIn("```json", composed)

    def test_is_deterministic(self):
        prompt_text = load_prompt_text("extract-skills", PROMPTS_DIR)
        first = compose_prompt(prompt_text, self.data)
        second = compose_prompt(prompt_text, self.data)
        self.assertEqual(first, second)

    def test_escapes_pipe_in_text(self):
        payload = {
            "bookmarks": [
                {
                    "author_username": "pipe_user",
                    "source_url": "https://x.com/pipe_user/status/9",
                    "text": "a | b table breaker",
                    "theme": None,
                }
            ]
        }
        data = load_extract_input_from_payload(payload)
        composed = compose_prompt("# P", data)
        self.assertIn("a \\| b table breaker", composed)


class RunExtractTests(unittest.TestCase):
    def test_compose_only_returns_prompt(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = _write_payload(tmp_path, SAMPLE_PAYLOAD)
            result = run_extract(
                input_path=input_path,
                prompts_dir=PROMPTS_DIR,
                prompt_name=DEFAULT_EXTRACT_PROMPT,
                runner=ComposeOnlyPromptRunner(),
            )
        self.assertIn("Extract Skills", result)
        self.assertIn("@ben_ai_eng", result)

    def test_runner_receives_composed_prompt(self):
        import tempfile

        captured = {}

        class SpyRunner:
            def run(self, prompt):
                captured["prompt"] = prompt
                return "SKILLS-OUTPUT"

        with tempfile.TemporaryDirectory() as tmp:
            input_path = _write_payload(Path(tmp), SAMPLE_PAYLOAD)
            result = run_extract(
                input_path=input_path,
                prompts_dir=PROMPTS_DIR,
                runner=SpyRunner(),
            )
        self.assertEqual(result, "SKILLS-OUTPUT")
        self.assertIn("## Bookmarks To Analyze", captured["prompt"])


class LLMConfigTests(unittest.TestCase):
    def test_defaults_target_ollama(self):
        config = load_llm_config({})
        self.assertEqual(config.base_url, DEFAULT_LLM_BASE_URL)
        self.assertEqual(config.model, DEFAULT_LLM_MODEL)
        self.assertIsNone(config.api_key)

    def test_env_overrides(self):
        config = load_llm_config(
            {
                "BOOKMARK_MAXXING_LLM_BASE_URL": "http://example.test/v1",
                "BOOKMARK_MAXXING_LLM_MODEL": "qwen2.5",
                "BOOKMARK_MAXXING_LLM_API_KEY": "secret",
                "BOOKMARK_MAXXING_LLM_TEMPERATURE": "0.7",
            }
        )
        self.assertEqual(config.base_url, "http://example.test/v1")
        self.assertEqual(config.model, "qwen2.5")
        self.assertEqual(config.api_key, "secret")
        self.assertEqual(config.temperature, 0.7)


class LLMPromptRunnerTests(unittest.TestCase):
    def test_sends_openai_chat_request_and_parses_content(self):
        opener = RecordingOpener(response=FakeChatResponse("## Theme: loops\nSkill: X"))
        runner = LLMPromptRunner(LLMConfig(model="llama3.1"), opener=opener)

        result = runner.run("COMPOSED PROMPT")

        self.assertEqual(result, "## Theme: loops\nSkill: X")
        self.assertEqual(len(opener.requests), 1)
        request = opener.requests[0]
        self.assertEqual(request.method, "POST")
        self.assertTrue(request.full_url.endswith("/chat/completions"))
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["model"], "llama3.1")
        self.assertFalse(body["stream"])
        self.assertEqual(body["messages"][-1]["content"], "COMPOSED PROMPT")
        self.assertEqual(body["messages"][0]["role"], "system")

    def test_sends_authorization_header_when_api_key_set(self):
        opener = RecordingOpener(response=FakeChatResponse("ok"))
        runner = LLMPromptRunner(
            LLMConfig(api_key="abc123"), opener=opener
        )
        runner.run("p")
        self.assertEqual(
            opener.requests[0].get_header("Authorization"), "Bearer abc123"
        )

    def test_connection_error_is_clean(self):
        opener = RecordingOpener(error=URLError("Connection refused"))
        runner = LLMPromptRunner(LLMConfig(), opener=opener)
        with self.assertRaises(LLMRunError) as ctx:
            runner.run("p")
        self.assertIn("Could not reach an LLM server", str(ctx.exception))

    def test_http_error_mentions_model(self):
        error = HTTPError(
            url="http://localhost:11434/v1/chat/completions",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"model not found"}'),
        )
        opener = RecordingOpener(error=error)
        runner = LLMPromptRunner(LLMConfig(model="llama3.1"), opener=opener)
        with self.assertRaises(LLMRunError) as ctx:
            runner.run("p")
        self.assertIn("ollama pull llama3.1", str(ctx.exception))

    def test_empty_choices_raises(self):
        class EmptyResponse:
            def read(self):
                return json.dumps({"choices": []}).encode("utf-8")

        runner = LLMPromptRunner(LLMConfig(), opener=RecordingOpener(response=EmptyResponse()))
        with self.assertRaises(LLMRunError):
            runner.run("p")


class ExtractCLITests(unittest.TestCase):
    def test_cli_compose_only_emits_prompt(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            input_path = _write_payload(Path(tmp), SAMPLE_PAYLOAD)
            stdout = io.StringIO()
            exit_code = cli_main(
                [
                    "extract",
                    "--input",
                    str(input_path),
                    "--prompts-dir",
                    str(PROMPTS_DIR),
                ],
                stdout=stdout,
            )
        self.assertEqual(exit_code, 0)
        self.assertIn("Extract Skills", stdout.getvalue())
        self.assertIn("@systems_builder", stdout.getvalue())

    def test_cli_unknown_prompts_dir_exits_cleanly(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            input_path = _write_payload(Path(tmp), SAMPLE_PAYLOAD)
            with self.assertRaises(SystemExit) as ctx:
                cli_main(
                    [
                        "extract",
                        "--input",
                        str(input_path),
                        "--prompts-dir",
                        str(Path(tmp) / "missing"),
                    ],
                    stdout=io.StringIO(),
                )
        self.assertIn("Prompt file not found", str(ctx.exception))

    def test_cli_llm_clean_failure_without_server(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            input_path = _write_payload(Path(tmp), SAMPLE_PAYLOAD)
            env = {"BOOKMARK_MAXXING_LLM_BASE_URL": "http://127.0.0.1:1/v1"}
            with mock.patch.dict("os.environ", env, clear=False):
                with self.assertRaises(SystemExit) as ctx:
                    cli_main(
                        [
                            "extract",
                            "--input",
                            str(input_path),
                            "--prompts-dir",
                            str(PROMPTS_DIR),
                            "--llm",
                        ],
                        stdout=io.StringIO(),
                    )
        self.assertIn("Could not reach an LLM server", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
