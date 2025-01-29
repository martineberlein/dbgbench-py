#!/bin/bash

echo "Checking out dbgbench repository..."

# Move to the parent directory where the repo should be
pushd ../ || exit 1

# Clone the repo if it does not exist
if [ ! -d "dbgbench.github.io/.git" ]; then
    git clone https://github.com/dbgbench/dbgbench.github.io.git
else
    echo "Repository already exists."
fi

echo "Applying patch to dbgbench..."
cd dbgbench.github.io || exit 1

# Ensure the patch file exists
PATCH_FILE="../debuggingbench/dbgbench.patch"
if [ ! -f "$PATCH_FILE" ]; then
    echo "Patch file not found: $PATCH_FILE"
    ls -l "$(dirname "$PATCH_FILE")"
    exit 1
fi

git apply --reject --whitespace=fix $PATCH_FILE

# Return to the original directory
popd || exit 1

echo "Patch applied successfully."
