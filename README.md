# Stock Postprocessing Workflow

## Overview

This project automates the common postprocessing tasks that are part of running ResStock and ComStock

## Installation

1. Clone the repository

```shell
git clone
```

2. Install uv globally if you don't already have it installed

```shell
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# or via pip
pip install uv

uv --version
```

3. Create the uv virtual environment and install dependencies, then activate it

```shell
uv python install

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

4. Update the uv dependencies

```shell
# (Re-)generate your lockfile from pyproject.toml
uv lock --upgrade

# Create/update your virtualenv and install the dependencies
uv sync
```

## Run pre-commit to check code style

```shell
uv run pre-commit run --all-files
```

#### Create and activate the uv environment

```shell
pip install -e .
stock-postproc run --config-file=config.yaml
```
