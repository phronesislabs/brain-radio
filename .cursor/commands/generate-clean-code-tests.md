---
description: "Generate static Clean Code validation tests from .cursor/rules/clean_code.mdc that can run in CI without LLM dependencies"
---

# Generate Clean Code Static Tests

This command generates static, CI-compatible test files that validate code against Clean Code principles from `.cursor/rules/clean_code.mdc`. The generated tests use AST/parser analysis and can run independently without LLM dependencies.

## Overview

The command:
1. Reads `.cursor/rules/clean_code.mdc` and parses rule sections
2. Detects project languages (Python, TypeScript, Rust, shell, YAML, etc.)
3. Generates language-agnostic validator framework
4. Creates language-specific parsers and validators
5. Generates test files in appropriate framework (pytest, jest, cargo test, etc.)
6. Creates configuration file for project-specific settings

## Execution Steps

When the user invokes this command:

1. **Step 1: Read Rule Files**
   - Read `.cursor/rules/clean_code.mdc` using `read_file`
   - Read `.cursor/commands/code_review.md` for rule categories (optional reference)
   - Parse markdown to extract rule sections and requirements

2. **Step 2: Detect Project Structure**
   - Check for language indicators:
     - Python: `pyproject.toml`, `setup.py`, `requirements.txt`, `*.py` files
     - TypeScript: `package.json` with TypeScript, `tsconfig.json`, `*.ts`, `*.tsx` files
     - Rust: `Cargo.toml`, `*.rs` files
     - Shell: `*.sh`, `*.bash` files in scripts directory
     - YAML: `.github/workflows/*.yml`, `terraform/*.tf`, `*.yaml` files
   - Auto-detect source paths from language-specific config files
   - Create or update `.cursor/clean_code_test_config.yaml` with detected settings

3. **Step 3: Create Validator Framework**
   - Create `tests/clean_code_validator/` directory structure
   - Create base classes (`base.py`, `violations.py`)
   - Create language parser adapters directory (`parsers/`)
   - Create validators directory (`validators/`)
   - Create test generators directory (`test_generators/`)

4. **Step 4: Implement Core Components**
   - Create rule parser (`tests/_clean_code_rule_parser.py`)
   - Implement language parsers (Python AST, TypeScript parser, etc.)
   - Implement core validators (function length, line length, naming, etc.)
   - Implement test generators for each framework

5. **Step 5: Generate Test Files**
   - Generate test files for each detected language:
     - Python: `tests/test_clean_code_static.py` (pytest)
     - TypeScript: `tests/clean-code-static.test.ts` (jest/vitest)
     - Rust: `tests/clean_code_static.rs` (cargo test)
     - Shell: `tests/test_clean_code_static.sh` (shell script)
     - YAML: `tests/test_clean_code_github_actions.py` (pytest)
   - Ensure tests integrate with existing test suite

6. **Step 6: Verify Integration**
   - Check that generated tests can be run with existing test commands
   - Verify tests are included in quality gate if applicable
   - Ensure configuration file is properly formatted

## How It Works

### Architecture

The command generates a language-agnostic validation framework:

- **Abstract Validator Interface** - Language-independent rule validators
- **Language Parser Adapters** - Language-specific parsers (Python AST, TypeScript parser, Rust syn, shell parsers, YAML parsers)
- **Test Framework Generators** - Generate tests in appropriate framework (pytest, jest, cargo test, shell scripts, etc.)
- **Configuration File** - Project-specific test configuration with language detection

### Rule Parsing

The rule parser (`tests/_clean_code_rule_parser.py`) extracts:
- Rule sections from markdown (Meaningful Names, Functions, Comments, etc.)
- Specific requirements and thresholds
- Code examples (DO/DON'T patterns)
- Language-specific patterns

### Validator Framework

Each validator:
- Implements `Validator` abstract base class
- Works with `CodeNode` language-agnostic representation
- Produces `Violation` objects for rule violations
- Supports language-specific patterns and thresholds

### Language Parsers

Parsers convert language-specific AST to common `CodeNode` format:
- **Python:** Uses `ast` module
- **TypeScript:** Uses `typescript-eslint-parser` or `tree-sitter-typescript`
- **Rust:** Uses `tree-sitter-rust` or Python bindings to `syn`
- **Shell:** Uses `bash-parser` or regex-based parsing
- **YAML:** Uses `ruamel.yaml` or `pyyaml` + custom logic

### Test Generation

Test generators create framework-specific test files:
- **Python:** pytest test classes with test methods
- **TypeScript:** Jest/Vitest describe/it blocks
- **Rust:** cargo test modules with test functions
- **Shell:** Shell script with test functions
- **YAML:** Python tests for validation

## Examples

### Example 1: Python Project

After running the command, a Python project will have:

```python
# tests/test_clean_code_static.py
"""Static Clean Code validation tests - Auto-generated from .cursor/rules/clean_code.mdc"""
import pytest
from pathlib import Path
from clean_code_validator import (
    FunctionLengthValidator,
    LineLengthValidator,
    PythonParser,
    NamingConventionValidator,
)

SOURCE_PATHS = ["src/brain_radio"]
EXCLUDE_PATTERNS = ["__pycache__", "*.pyc", "tests/"]

class TestCleanCodeNames:
    def test_no_single_letter_names(self):
        """Verify single-letter names only used for loop counters."""
        parser = PythonParser()
        validator = NamingConventionValidator()
        # Implementation...
```

Run with: `pytest tests/test_clean_code_static.py`

### Example 2: TypeScript Project

For a TypeScript project:

```typescript
// tests/clean-code-static.test.ts
import { describe, it, expect } from '@jest/globals';
import { TypeScriptParser } from './clean_code_validator/parsers/typescript_parser';
import { FunctionLengthValidator } from './clean_code_validator/validators/function_length';

const SOURCE_PATHS = ['src'];
const EXCLUDE_PATTERNS = ['node_modules', 'dist', '*.test.ts'];

describe('Clean Code - Names', () => {
  it('should verify no single-letter names', () => {
    const parser = new TypeScriptParser();
    const validator = new NamingConventionValidator();
    // Implementation...
  });
});
```

Run with: `npm test -- clean-code-static.test.ts`

### Example 3: Multi-Language Project

For a project with multiple languages, the command generates tests for each:

- `tests/test_clean_code_static.py` - Python tests
- `tests/clean-code-static.test.ts` - TypeScript tests
- `tests/test_clean_code_static.sh` - Shell script tests
- `tests/test_clean_code_github_actions.py` - GitHub Actions validation

## Configuration

The command generates `.cursor/clean_code_test_config.yaml` with:

```yaml
# Clean Code Static Test Configuration
# Auto-generated by generate-clean-code-tests command
project:
  name: "brain-radio"
  languages:
    - python
    - typescript
    - shell
    - yaml
    
  source_paths:
    python:
      - "src/brain_radio"
    typescript:
      - "frontend/src"
    shell:
      - "scripts"
    yaml:
      - ".github/workflows"
      
  exclude_patterns:
    python:
      - "__pycache__"
      - "*.pyc"
      - "tests/"
    typescript:
      - "node_modules"
      - "dist"
      - "*.test.ts"
    shell:
      - "*.sh.bak"
    yaml:
      - "*.yml.bak"

rules:
  function_length:
    enabled: true
    max_lines: 20
    warn_threshold: 15
    languages: ["python", "typescript", "rust", "shell"]
    
  line_length:
    enabled: true
    max_chars: 120
    hard_max: 200
    languages: ["*"]
    
  # ... more rule configurations
```

## Integration with CI

Generated tests integrate with existing CI pipelines:

- **Python Projects:** Run as part of pytest suite: `pytest tests/test_clean_code_static.py`
- **TypeScript Projects:** Run as part of Jest/Vitest: `npm test -- clean-code-static.test.ts`
- **Rust Projects:** Run as part of cargo test: `cargo test clean_code_static`
- **Multi-Language:** Run all language tests: `./scripts/run-all-clean-code-tests.sh` (if generated)

## Related Rules

- [clean_code.mdc](mdc:.cursor/rules/clean_code.mdc): Complete Clean Code principles and guidelines
- [code_review.md](mdc:.cursor/commands/code_review.md): Code review checklist generator
- [auto-checks.mdc](mdc:.cursor/rules/auto-checks.mdc): Automatic quality checks
- [cursor_rules.mdc](mdc:.cursor/rules/cursor_rules.mdc): Guidelines for creating and maintaining rules

## Important Notes

- **Deterministic:** Same input produces same output
- **Language-Aware:** Automatically detects and supports multiple languages
- **CI-Compatible:** Generated tests run without LLM dependencies
- **Extensible:** Easy to add new language parsers and validators
- **Configurable:** Project-specific settings via config file

## Usage

To use this command, invoke it through Cursor. The command will:

1. Automatically detect your project structure
2. Parse Clean Code rules from `.cursor/rules/clean_code.mdc`
3. Generate configuration file (`.cursor/clean_code_test_config.yaml`)
4. Create validator framework in `tests/clean_code_validator/`
5. Generate test files in `tests/` directory

### Manual Execution

You can also run the generation programmatically:

```python
from pathlib import Path
from tests._config_generator import ConfigGenerator
from tests._test_generator import TestGenerator

# Generate configuration
config_gen = ConfigGenerator()
config_path = config_gen.generate()

# Generate test files
test_gen = TestGenerator(config_path)
generated_files = test_gen.generate_all()

print(f"Generated {len(generated_files)} test files:")
for file in generated_files:
    print(f"  - {file}")
```

### Running Generated Tests

**Python (pytest):**
```bash
# Run all Clean Code tests
pytest tests/test_clean_code_static.py -v

# Run specific test class
pytest tests/test_clean_code_static.py::TestCleanCodeNames -v

# Run with coverage
pytest tests/test_clean_code_static.py --cov=src/brain_radio
```

The generated tests are automatically included when running:
```bash
pytest tests/  # Runs all tests including Clean Code tests
```

### Configuration Customization

Edit `.cursor/clean_code_test_config.yaml` to customize:

- **Source paths:** Add or remove source directories
- **Exclude patterns:** Add patterns to exclude from validation
- **Rule thresholds:** Adjust max function length, line length, etc.
- **Enable/disable rules:** Turn specific validators on or off

Example configuration:
```yaml
rules:
  function_length:
    enabled: true
    max_lines: 25  # Increase from default 20
    warn_threshold: 20
  line_length:
    enabled: true
    max_chars: 150  # Increase from default 120
    hard_max: 250
```

After modifying configuration, regenerate test files by running the command again.

## Troubleshooting

- **No languages detected:** Check project structure and ensure language files exist
- **Parser errors:** Verify language-specific parser dependencies are installed
- **Test failures:** Review generated test files and adjust configuration thresholds
- **Missing validators:** Check that rule parser correctly extracted rules from markdown
- **Import errors:** Ensure `tests/clean_code_validator/` is in Python path (should work automatically with pytest)
- **Config file not found:** Run the command to generate the configuration file first

