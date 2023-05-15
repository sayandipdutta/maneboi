from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pfzy import fuzzy_match
from rich.console import RenderableType
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Input, Markdown, OptionList

database: dict[RenderableType, dict[str, str]] = {}
keys: list[RenderableType] = []


def build_database():
    path = Path(__file__).parent / "data"
    for file in path.iterdir():
        if file.suffix == ".md":
            with open(file) as fh:
                file_content = fh.read()
                md = {"title": file.stem, "message": file_content}
                for line in file_content.splitlines():
                    if line.startswith("aliases:"):
                        start = line.index("[")
                        content = eval(line[start:])
                        content.append(file.stem)
                        for name in content:
                            database[name] = md
                        break
    keys.extend(list(database))


async def find_match(results):
    seen = set()
    for result in results:
        key = result["value"]
        value = database[key]
        if (title := value["title"]) in seen:
            continue
        seen.add(title)
        yield key, value


class ManeboiApp(App):
    """Searches ab dictionary API as-you-type."""

    CSS_PATH = "maneboi.css"
    KEYS: ClassVar[list[str]] = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search for a word")
        with Container(id="result-area"):
            yield OptionList(id="search-results")
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
            self.query_one("#search-results", OptionList).clear_options()

    @work(exclusive=True)
    async def lookup_word(self, word: str) -> None:
        """Looks up a word."""

        try:
            results = await fuzzy_match(word, keys, key="value")  # type: ignore
        except KeyError:
            self.query_one("#results", Markdown).update("No matches found.")
            self.query_one("#search-results", OptionList).clear_options()
        else:
            options = [result["value"] for result in results]
            self.query_one("#search-results", OptionList).clear_options()
            self.query_one("#search-results", OptionList).add_options(options)

    @on(OptionList.OptionSelected)
    def option_selected(self, event: OptionList.OptionSelected) -> None:
        content = database[event.option.prompt]
        md = self.make_word_markdown(content)
        self.query_one("#results", Markdown).update(md)

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
    app = ManeboiApp()
    app.run()
