# Template Extraction Pattern for Batch HTML Generation

## Problem

When generating multiple HTML files with identical structure (CSS, JS, Toolbar) but different content, regenerating the entire HTML for each file is error-prone — one typo in CSS/JS affects all files, and fixes must be applied 12+ times.

## Solution: Gold Standard + Extraction

1. Designate ONE file as the **Gold Standard** — this file has the final, reviewed CSS/JS/Toolbar/Modal
2. For each new file, extract the **static parts** from the Gold Standard:
   - `before` = everything from `<!DOCTYPE html>` up to (but not including) the section-break header
   - `after` = everything from the `slide-end` div to `</html>`
3. Generate only the **dynamic parts** (section header + gap slides)
4. Concatenate: `before + section_header + gap_slides + after`
5. Replace all occurrences of the old SOP name in `before` and `after`

## Implementation

```python
with open('gold-standard.html', 'r', encoding='utf-8') as f:
    template = f.read()

# Find section break divider
sb = template.find('<div class="slide-container section-break" id="slide-sop')
first_gap = template.find('<div class="slide-container" id="slide-2-')
slide_end_pos = template.find('<div class="slide-container section-break" id="slide-end">')

before = template[:first_gap]   # CSS + JS + Toolbar + Cover
after = template[slide_end_pos:] # End slide + Modal + Toast + Scripts

# For each new SOP:
gap_slides = [...]
section_header = f'<div class="slide-container section-break">...SOP NAME...</div>'
end_slide = after.replace('OLD_SOP_NAME', new_sop_name)

html = before + '\n' + section_header + '\n' + gap_slides + '\n' + end_slide
html = html.replace('OLD_SOP_NAME', new_sop_name)  # Fix all references
```

## When to Use This

- SOP Review documents (13 files, same toolbar/features)
- Any batch of documents sharing the same UI shell
- When a CSS/JS fix needs to propagate to all files

## Anti-patterns to Avoid

- ❌ Regenerating full HTML from scratch for each file → CSS/JS drift between files
- ❌ Using execute_code with Thai Unicode escaping (`\uXXXX`) → SyntaxError
- ❌ Using delegate_task for batch file generation → silent timeout
- ❌ Copying Gold Standard file and manually editing → human error, missed replacements
