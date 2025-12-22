---
description: "Retrieve YouTube video transcripts and optionally generate Cursor rules/commands from the content"
---

# YouTube Transcript Command

Retrieve full transcripts from YouTube videos and optionally generate Cursor rules or commands based on the transcript content.

## Usage

```bash
# Basic usage - retrieve transcript
youtube-transcript <youtube_url>

# Save transcript to file
youtube-transcript <youtube_url> --output transcript.txt

# Generate rules/commands from transcript (proposes changes for approval)
youtube-transcript <youtube_url> --generate-rules

# Only propose rules/commands without writing (preview mode)
youtube-transcript <youtube_url> --generate-rules --propose-only

# Different output formats
youtube-transcript <youtube_url> --format json
youtube-transcript <youtube_url> --format markdown
```

## Options

- `<youtube_url>`: YouTube URL or video ID (required)
  - Supports: `https://www.youtube.com/watch?v=VIDEO_ID`
  - Supports: `https://youtu.be/VIDEO_ID`
  - Supports: `VIDEO_ID` (just the ID)
- `--output`, `-o`: Save transcript to file instead of printing
- `--format`, `-f`: Output format (`text`, `json`, or `markdown`)
- `--languages`, `-l`: Preferred language codes (default: `en en-US en-GB`)
- `--generate-rules`: Generate Cursor rules/commands from transcript content
- `--propose-only`: Only propose rules/commands, don't write them (requires `--generate-rules`)

## Execution Steps

When the user invokes this command:

1. **Extract the YouTube URL** from the user's request
2. **Determine if `--generate-rules` flag is present** (user may say "generate rules" or use the flag)
3. **Run the script:**
   ```bash
   python scripts/youtube_transcript.py <url> [--generate-rules] [--propose-only] [other flags]
   ```
4. **If `--generate-rules` is used:**
   - The script will output special markers in stderr: `---CURSOR_RULE_GENERATION_REQUEST---` and `---TRANSCRIPT_START---` / `---TRANSCRIPT_END---`
   - **Capture the transcript content** from the script output
   - **Analyze the transcript** to identify:
     - Coding patterns, conventions, or best practices
     - Guidelines that should be enforced as rules
     - Workflow improvements that could become commands
     - Tool usage patterns
     - Architecture or design principles
   - **Generate proposals** for new rules/commands:
     - Review existing rules in `.cursor/rules/` to avoid duplication
     - Review existing commands in `.cursor/commands/` to avoid duplication
     - Follow the structure in [cursor_rules.mdc](mdc:.cursor/rules/cursor_rules.mdc)
     - Create proposals with:
       - Proposed file name and path
       - Full content of the proposed rule/command
       - Explanation of why this rule/command is valuable
       - How it relates to the transcript content
   - **Present proposals to the user** and **WAIT FOR EXPLICIT APPROVAL** before writing any files
   - **If `--propose-only` is used:** Only show proposals, do not write files even if approved
   - **If approved and not `--propose-only`:** Write the approved files following project conventions
5. **If `--generate-rules` is NOT used:** Simply display or save the transcript as requested

## How It Works

1. **Transcript Retrieval**: The script uses `youtube-transcript-api` to fetch the full transcript
2. **Rule Generation**: When `--generate-rules` is used, the Cursor agent will:
   - Analyze the transcript content
   - Identify patterns, best practices, or guidelines that should become rules
   - Propose new `.cursor/rules/*.mdc` files or `.cursor/commands/*.md` files
   - **Request your approval** before writing any files (unless `--propose-only` is used, which only shows proposals)

## Rule Generation Process

When `--generate-rules` is specified, the agent will:

1. **Analyze the Transcript**: Review the content to identify:
   - Coding patterns or conventions
   - Best practices mentioned
   - Guidelines that should be enforced
   - Workflow or process improvements
   - Tool usage patterns

2. **Propose Rules/Commands**: Generate proposals for:
   - New rule files in `.cursor/rules/` (following [cursor_rules.mdc](mdc:.cursor/rules/cursor_rules.mdc) format)
   - New command files in `.cursor/commands/` (following the pattern of existing commands)
   - Updates to existing rules if appropriate

3. **Request Approval**: Before writing any files, the agent will:
   - Show you the proposed rule/command content
   - Explain why each rule/command is being proposed
   - Wait for your explicit approval before creating files

4. **Write Files** (if approved): Only after approval, the agent will:
   - Create new rule files with proper frontmatter and structure
   - Create new command files following existing patterns
   - Ensure files follow project conventions

## Examples

### Basic Transcript Retrieval

```bash
youtube-transcript https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Outputs the transcript as plain text to stdout.

### Save Transcript

```bash
youtube-transcript https://youtu.be/dQw4w9WgXcQ --output docs/transcript.txt
```

Saves the transcript to a file.

### Generate Rules from Coding Tutorial

```bash
youtube-transcript https://www.youtube.com/watch?v=example --generate-rules
```

The agent will analyze the transcript, identify coding patterns or best practices, and propose new Cursor rules for your approval.

### Preview Rule Proposals

```bash
youtube-transcript https://www.youtube.com/watch?v=example --generate-rules --propose-only
```

Shows proposed rules/commands without writing any files. Useful for reviewing what would be created.

## Integration

This command calls the `scripts/youtube_transcript.py` script, which can also be used directly:

```bash
# As a standalone script
python scripts/youtube_transcript.py <url>

# In other scripts
from scripts.youtube_transcript import get_transcript, extract_video_id
```

## Requirements

The script requires `youtube-transcript-api`:

```bash
uv pip install youtube-transcript-api
```

## Error Handling

The script handles common errors gracefully:

- **Video Unavailable**: Video doesn't exist or is private
- **Transcripts Disabled**: Transcripts are disabled for the video
- **No Transcript Found**: No transcript available in requested languages
- **Invalid URL**: URL format not recognized

## Notes

- The script automatically tries multiple language codes and falls back to auto-generated transcripts
- Transcripts are retrieved in the original format with timestamps preserved
- When generating rules, the agent follows the structure defined in [cursor_rules.mdc](mdc:.cursor/rules/cursor_rules.mdc)
- All proposed rules/commands are reviewed before being written to ensure quality and relevance

