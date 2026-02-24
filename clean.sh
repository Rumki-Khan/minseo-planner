#!/bin/bash

echo " Cleaning project cache and temporary files..."

# Remove Python cache directories
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove LaTeX build files
rm -f *.aux *.log *.toc *.out *.lof *.lot *.fls *.fdb_latexmk *.synctex.gz

# Remove VS Code workspace cache (optional)
rm -rf .vscode/.cache 2>/dev/null

# Remove generic cache folders
find . -type d -name ".cache" -exec rm -rf {} +

echo " Cleanup complete!"
