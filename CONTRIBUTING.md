# Contributing to QExtraWidgets

First off, thank you for considering contributing to QExtraWidgets! It's people like you that make this tool great.

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Technical Guidelines & Style Guide](#technical-guidelines--style-guide)
- [Development Setup](#development-setup)

## Code of Conduct
This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs
If you find a bug, please create a new **Issue** and include:
* A clear and descriptive title.
* Steps to reproduce the problem.
* What you expected to happen vs. what actually happened.
* Screenshots if applicable.

### Suggesting Enhancements
We love new ideas! To suggest an enhancement:
1. Check if the idea hasn't been suggested before.
2. Open an **Issue** explaining the feature and why it would be useful.

### Pull Requests
1. **Fork** the repository and create your branch from `main`.
2. Ensure your development environment is set up (see [Development Setup](#development-setup)).
3. If you've added code that should be tested, add tests.
4. Ensure the test suite passes: `pytest tests/tests.py`.
5. Make sure your code follows the project's [Style Guide](#technical-guidelines--style-guide).
6. Submit a Pull Request with a comprehensive description of changes.

## Technical Guidelines & Style Guide

To ensure consistency and maintainability, please adhere to the following technical guidelines when writing code for QExtraWidgets.

### 1. Tech Stack & Dependencies
Ensure your code is compatible with the following core libraries:
- **GUI Library:** PySide6 (v6.10.1).
- **Icons:** qtawesome (v1.4.0) – Used for vector icons.
- **Emoji Data:** emoji-data-python (v1.6.0) - Contains the emoji data.
- **Emoji Icons:** twemoji-api (v2.0.0) - Serves Twitter PNG and SVG icons for emojis.

### 2. Import Rules
- **Explicit Imports:** Avoid wildcard imports (`from PySide6.QtWidgets import *`). Import classes explicitly.
- **Correct Modules:** Verify the correct location of Qt classes (e.g., `QAction` belongs to `QtGui`, not `QtWidgets`).

### 3. Code Standards & Structure
- **Instance Variables:** All instance variables must be defined within `__init__`.
- **Constructors:** Every Widget must accept a `parent` argument (defaulting to `None`) and must call `super().__init__(parent)`.
- **Signals and Slots:** Use the modern connection syntax (e.g., `self.button.clicked.connect(self._on_clicked)`).

### 4. Naming Conventions (Hybrid Qt/Python)
We follow a hybrid naming pattern to match the Qt framework we are extending:
- **Classes:** PascalCase (e.g., `QExtraButton`).
- **Public Methods (API):** camelCase (e.g., `setBorderColor`).
- **Private/Internal Methods:** snake_case with a leading underscore (e.g., `_calculate_size`).
- **Local Variables/Parameters:** snake_case (e.g., `button_width`).
- **No Abbreviations:** Do not abbreviate variable, function, method, class, or module names. Use full descriptive names (e.g., `calculate_total_width` instead of `calc_tot_w`).

### 5. Getters, Setters, and Properties
- **Public Variables:** Must have both a getter and a setter; direct access is discouraged.
- **Private Variables:** Must not have an exposed getter.
- **Naming Standard:**
  - **Setter:** Prefix `set` + camelCase (e.g., `setColor`, `setEnabled`).
  - **Getter (Standard):** **NO** `get` prefix. Use the property name in camelCase (e.g., `color()`, `text()`).
  - **Getter (Boolean):** Prefix `is` or `has` + camelCase (e.g., `isEnabled()`, `isVisible()`, `hasBorder()`).
- **Qt Properties:** If an observable property is required for Qt internals, use the PySide6 `@Property` decorator.

### 6. Typing & Documentation
- **Type Hinting:** Mandatory usage of type hints (PEP 484) in all methods and parameters.
- **Comments & Docstrings:**
  - **Language:** English only.
  - **Docstrings:** Use Google Style docstrings for all classes and public methods.
  - **Inline Comments:** Use sparingly, only for complex logic.

## Commit Message Style
We follow the **Conventional Commits** pattern:
* `feat:` for new features.
* `fix:` for bug fixes.
* `docs:` for documentation changes.
* `refactor:` for code changes that neither fix a bug nor add a feature.

Example: `feat: add dark mode support to dashboard`

## Development Setup

To set up your local development environment:

1. **Clone your fork:**
```bash
git clone https://github.com/gpedrosobernardes/QExtraWidgets.git
cd QExtraWidgets
```
2. **Create and activate a virtual environment (Recommended):**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
3. **Install dependencies:**
```bash
pip install -r requirements.txt
```
4. **Run tests:**
```bash
pytest tests/tests.py
```