from __future__ import annotations

from pathlib import Path
from typing import ClassVar


from textual import work
from pfzy import fuzzy_match
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, Markdown

database: dict[str, dict[str, str]] = {}
keys: list[str] = []


def build_database():
    path = Path(__file__).parent / "data"
    for file in path.iterdir():
        if file.suffix == ".md":
            with open(file) as fh:
                file_content = fh.read()
                md = {"title": file.stem, "message": file_content}
                for line in file_content.splitlines():
                    if line.startswith("aliases:"):
                        start = line.index('[')
                        content = eval(line[start:])
                        content.append(file.stem)
                        for name in content:
                            database[name] = md
                        break
    keys.extend(list(database))


async def find_match(word, haystack):
    results = await fuzzy_match(word, haystack, key="value")
    seen = set()
    for result in results:
        if (title := database[result['value']]['title']) in seen:
            continue
        seen.add(title)
        yield database[result['value']]


class DictionaryApp(App):
    """Searches ab dictionary API as-you-type."""

    CSS_PATH = "dictionary.css"
    KEYS: ClassVar[list[str]] = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search for a word")
        with VerticalScroll(id="results-container"):
            yield Markdown(id="results")

    def on_mount(self) -> None:
        """Called when app starts."""
        # Give the input focus, so we can start typing straight away
        build_database()
        self.query_one(Input).focus()

    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""
        if message.value:
            self.lookup_word(message.value)
        else:
            # Clear the results
            self.query_one("#results", Markdown).update("")

    @work(exclusive=True)
    async def lookup_word(self, word: str) -> None:
        """Looks up a word."""

        try:
            results = [result async for result in find_match(word, keys)]
        except KeyError:
            self.query_one("#results", Markdown).update("No matches found.")
        else:
            if word == self.query_one(Input).value:
                markdown = self.make_word_markdown(results)
                self.query_one("#results", Markdown).update(markdown)

    def make_word_markdown(self, results: object) -> str:
        """Convert the results in to markdown."""
        lines = []
        if isinstance(results, dict):
            lines.append(f"# {results['title']}")
            lines.append(results["message"])
        elif isinstance(results, list):
            for result in results:
                lines.append(f"# {result['title']}")
                lines.append(result["message"])

        return "\n".join(lines)


if __name__ == "__main__":
    app = DictionaryApp()
    app.run()
