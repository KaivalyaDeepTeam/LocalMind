#!/bin/bash

# Script to organize screenshots from Desktop to proper location
# Maps screenshot times to meaningful names

DEST_DIR="/Users/prepladder/localmind/localmind/docs/user-guides/screenshots"

# Copy screenshots by matching time patterns
cd ~/Desktop || exit 1

copy_screenshot() {
    local pattern="$1"
    local dest="$2"
    local source_file

    source_file=$(find . -maxdepth 1 -name "*${pattern}*.png" 2>/dev/null | head -1)

    if [ -n "$source_file" ]; then
        echo "Copying: $source_file -> $dest"
        cp "$source_file" "$DEST_DIR/$dest"
        return 0
    else
        echo "Warning: Could not find screenshot for pattern: $pattern"
        return 1
    fi
}

# English screenshots
copy_screenshot "7.27.38" "01-main-window-en.png"
copy_screenshot "7.28.03" "02-scoring-parameters-en.png"
copy_screenshot "7.28.44" "03-settings-llm-en.png"
copy_screenshot "7.28.47" "04-llm-provider-dropdown-en.png"
copy_screenshot "7.28.50" "05-model-selection-en.png"
copy_screenshot "7.28.53" "06-settings-transcription-en.png"
copy_screenshot "7.28.56" "07-settings-output-en.png"
copy_screenshot "7.28.59" "08-settings-appearance-en.png"

# Russian screenshots
copy_screenshot "7.32.01" "11-main-window-ru.png"
copy_screenshot "7.32.31" "12-settings-llm-ru.png"
copy_screenshot "7.32.33" "13-settings-transcription-ru.png"
copy_screenshot "7.32.34" "14-settings-output-ru.png"
copy_screenshot "7.32.36" "15-settings-appearance-ru.png"
copy_screenshot "7.32.43" "16-language-dropdown-ru.png"

echo ""
echo "Done! Screenshots organized."
ls -lh "$DEST_DIR"
