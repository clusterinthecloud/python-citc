#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

version_spec=${1:-}

if [[ -z "${version_spec}" ]]
  then
    echo "This script must be called with an argument of the version number or a \"bump spec\"."
    echo "See \`poetry version --help\`"
    echo "For example, pass in \"patch\", \"minor\" or \"major\" to bump that segment."
    exit 1
fi

if ! git diff-index --quiet HEAD -- pyproject.toml
  then
    echo "There are uncomitted changes to \`pyproject.toml\`."
    echo "Commit or restore them before continuing."
    exit 1
fi

if ! git diff --cached --quiet
  then
    echo "There are uncomitted changes in the staging area."
    echo "Commit or restore them before continuing."
    exit 1
fi

poetry version "${version_spec}"
new_version=$(poetry version | awk '{print $2}')
git add pyproject.toml
git commit -m "Update to version ${new_version}"
git tag "${new_version}"
git push --all --tags
