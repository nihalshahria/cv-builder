# CV Builder

Source for my CV, written in YAML and rendered to PDF with [RenderCV](https://docs.rendercv.com/).
One base CV holds all content; each **flavor** overrides only what it needs (headline, summary,
bullet order, skills) to target a kind of role.

## Flavors

| Flavor    | Focus                               | PDF                                                                              |
| --------- | ----------------------------------- | -------------------------------------------------------------------------------- |
| `backend` | General backend (the base CV as-is) | [`Md_Shahria_Islam_Nihal_CV.pdf`](rendercv_output/Md_Shahria_Islam_Nihal_CV.pdf) |

The `backend` PDF path must stay unchanged; my portfolio links to it.

## Layout

| Path                     | Purpose                                                      |
| ------------------------ | ------------------------------------------------------------ |
| `cv/base.yaml`           | Full CV: content, design, locale and settings                |
| `cv/flavors/<name>.yaml` | Per-flavor overrides, plus that flavor's PDF path            |
| `build.py`               | Merges base + flavor and renders it with RenderCV            |
| `rendercv_output/`       | Rendered PDFs (committed)                                    |
| `.build/`                | Merged YAML, Typst and PNG previews per flavor (git-ignored) |
| `CV_PROMPT.md`           | Full background notes the CV is written from                 |

## Setup

Requires Python 3.12+.

```bash
git clone git@github.com:nihalshahria/cv-builder.git
cd cv-builder
python3 -m venv .venv
.venv/bin/pip install "rendercv[full]==2.8"
```

RenderCV bundles Typst and its fonts, so no LaTeX or Typst install is needed.

## Build

```bash
.venv/bin/python build.py            # all flavors
.venv/bin/python build.py go web3    # only the named flavors
```

Check `.build/<flavor>/<flavor>_1.png` for a quick preview. If a `<flavor>_2.png` appears, that
flavor has spilled onto a second page and needs trimming.

## Writing a flavor

A flavor file is merged over `cv/base.yaml`:

- Mappings merge key by key, so you only write the fields that change.
- Lists (summary, skills, bullets) **replace** the base list entirely.
- Experience entries are the exception: they are matched to the base by `company`
  (exact string), and only the fields you give change, e.g. reordering one job's `highlights`.
- Setting a key to `null` removes it, e.g. `problem_solving_&_achievements: null` drops a section.
- Every flavor must set `settings.render_command.pdf_path` (relative to the repo root).

Minimal example, `cv/flavors/java.yaml`:

```yaml
cv:
    headline: Backend Software Engineer · Java · Spring · Microservices
    sections:
        summary:
            - Backend engineer with ...
settings:
    render_command:
        pdf_path: rendercv_output/Md_Shahria_Islam_Nihal_CV_Java.pdf
```

Then `.venv/bin/python build.py java`.
