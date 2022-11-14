This repository is the main repository of the Cosmian Technical Documentation rendered at https://docs.cosmian.com


## Editing the docs

The documentation is written in markdown and served by mkdocs.

The [mkdocs.yml](./mkdocs.yml) specifies most of the important navigation and rendering options of the documentation.

Edit the `nav` section of the `mkdocs.yml` file when adding new files.

### markdown extensions

The docs supports many markdown extensions, in particular:

- code blocks
- code tabs
- admonitions
- maths symbols in LaTeX
- graphs using mermaid.js
- ...

Check the complete reference at: https://squidfunk.github.io/mkdocs-material/reference/

### mkdocs install and usage

The HTML is generated using mkdocs.

1. Install it locally

```sh
pip3 install pydoc-markdown git+https://github.com/twardoch/mkdocs-combine.git mkdocs-kroki-plugin mkdocs-material pandoc-latex-admonition install markdown-katex git+https://gitlab.com/myriacore/pandoc-kroki-filter.git
```

2. From the project root, run a local server

```sh
mkdocs serve
```

Then open a browser window at http://127.0.0.1:8003

The doc is live rendered when editing the markdown files.

## Deploying the documentation


### Main documentation

1. Build the documentation web site

```sh
mkdocs build
```

2. Copy it to docs.cosmian.com

```sh
scp -r site/* cosmian@docs.cosmian.com:/home/cosmian/documentation_root/
```

### KMS Documentation

The KMS documentation is automatically deployed from the KMS ci. However, you need
to adapt the [mkdocs.yml](mkdocs.yml) to add the tag in the `nav` and redeploy
`public_documentation`.

If you want to reproduce the CI manually, refer to the following steps:

1. Create an empty directory entry with the version number in the `nav` sub section of the `KMS`.
Then deploy the main documentation to docs.cosmian.com

2. Go to the KMS project `documentation` folder, then run

```sh
mkdocs build
scp -r site/* cosmian@docs.cosmian.com:/home/cosmian/documentation_root/kms/[VERSION]/
```

where `[VERSION]` is the version number (e.g. v2.3)
