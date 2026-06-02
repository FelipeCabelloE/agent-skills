#!/usr/bin/env bash
# Grading script for mantine-ui skill evals
# Usage: grade.sh <output_dir> <css_dir> <metadata_json>
# Example: grade.sh /tmp/.../with_skill/outputs /tmp/.../with_skill/outputs /tmp/.../eval_metadata.json

OUTPUT_DIR="$1"
CSS_DIR="${2:-$OUTPUT_DIR}"
METADATA="$3"

if [ -z "$OUTPUT_DIR" ] || [ -z "$METADATA" ]; then
  echo "Usage: grade.sh <output_dir> <css_dir> <metadata_json>"
  exit 1
fi

assertions=$(cat "$METADATA" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for a in data['assertions']:
    print(json.dumps(a))
")

echo "$assertions" | while read -r assertion; do
  text=$(echo "$assertion" | python3 -c "import json,sys; print(json.load(sys.stdin)['text'])")
  check=$(echo "$assertion" | python3 -c "import json,sys; print(json.load(sys.stdin)['check'])")
  atype=$(echo "$assertion" | python3 -c "import json,sys; print(json.load(sys.stdin)['type'])")

  passed="false"
  evidence=""

  if [ "$atype" = "contains" ]; then
    for f in "$OUTPUT_DIR"/*.tsx; do
      if [ -f "$f" ] && grep -Fq "$check" "$f" 2>/dev/null; then
        passed="true"
        evidence="Found in $(basename $f)"
        break
      fi
    done
    if [ "$passed" = "false" ]; then
      evidence="Not found in any .tsx file"
    fi
  elif [ "$atype" = "contains_regex" ]; then
    for f in "$OUTPUT_DIR"/*.tsx; do
      if [ -f "$f" ] && grep -Eq "$check" "$f" 2>/dev/null; then
        passed="true"
        evidence="Matched in $(basename $f)"
        break
      fi
    done
    if [ "$passed" = "false" ]; then
      evidence="Regex not matched in any .tsx file"
    fi
  elif [ "$atype" = "contains_file_pattern" ]; then
    for f in "$CSS_DIR"/*.css "$OUTPUT_DIR"/*.tsx; do
      if [ -f "$f" ] && grep -Fq "$check" "$f" 2>/dev/null; then
        passed="true"
        evidence="Found in $(basename $f)"
        break
      fi
    done
    if [ "$passed" = "false" ]; then
      evidence="Not found in any .css or .tsx file"
    fi
  fi

  echo "{\"text\": $(echo "$text" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))"), \"passed\": $passed, \"evidence\": $(echo "$evidence" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))")}"
done
