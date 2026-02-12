# How to Maintain Documentation

## ✅ Implemented Solution

The project now uses the `mkdocs-include-markdown-plugin` to **eliminate duplication** between `README.md` and `docs/index.md`.

### How it works:

1. **You edit ONLY the `README.md`** ✏️
2. The `docs/index.md` file automatically includes the content from `README.md`
3. When building or deploying the documentation, the content is synchronized automatically

## 📝 Workflow

### To edit the main documentation:
```bash
# Edit only the README.md
code README.md

# The docs/index.md will automatically include the content
```

### To preview the documentation locally:
```bash
# Install documentation dependencies (first time only)
pip install -e ".[docs]"

# Or install manually:
pip install mkdocs-material mkdocstrings[python] mkdocs-include-markdown-plugin

# Serve the documentation locally
mkdocs serve

# Open http://127.0.0.1:8000 in your browser
```

### To build the documentation:
```bash
mkdocs build
```

### To deploy (already done automatically via GitHub Actions):
```bash
mkdocs gh-deploy --force
```

## 🎯 Important Files

- **`README.md`** - MAIN file that you should edit
- **`docs/index.md`** - File that automatically includes README.md (DO NOT EDIT DIRECTLY)
- **`docs/api.md`** - API documentation (can be edited normally)
- **`mkdocs.yml`** - MkDocs configuration
- **`.github/workflows/docs.yml`** - GitHub Actions for automatic deployment

## 📦 Dependencies

Documentation dependencies are defined in `pyproject.toml`:

```toml
[project.optional-dependencies]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
    "mkdocs-include-markdown-plugin>=6.0.0",
    "mkdocstrings[python]>=0.24.0"
]
```

To install:
```bash
pip install -e ".[docs]"
```

## 🚀 Benefits

- ✅ **Zero duplication**: Edit only the `README.md`
- ✅ **Automatic synchronization**: docs/index.md always reflects README.md
- ✅ **Automatic deployment**: GitHub Actions takes care of the rest
- ✅ **Simple maintenance**: A single file to update

## 🔧 Troubleshooting

If you see errors about the `include-markdown` plugin not being installed:
```bash
pip install mkdocs-include-markdown-plugin
```

If the build fails during GitHub Actions deployment, verify that the `.github/workflows/docs.yml` file is installing all the correct dependencies.
