# maneboi
Find what you are looking for.

# Usage:
- Clone the repo.
- `cd maneboi`
- `$ pip install .`
- Create a folder `data` inside `maneboi/maneboi`
- Store all your `.md` files inside that folder.
- The `.md` file must have a section `alias` in its frontmatter:
  Example:
  #### `Foo.md`
```markdown
---
aliases: ["foo", "bar", "baz"]
<other fields> ...
---
<Rest of the content>
```
- From the root folder, run the following command in your shell:
```shell
$ textual run maneboi/maneboi.py
```
