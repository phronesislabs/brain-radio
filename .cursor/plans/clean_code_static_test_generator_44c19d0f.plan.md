---
name: Clean Code Static Test Generator
overview: Create a reusable Cursor command that parses Clean Code rules from markdown files and generates static, CI-compatible tests in the appropriate language(s) using AST/parser analysis. The command will be modular, language-agnostic, and work in any Cursor project (Python, TypeScript, Rust, C#, shell scripts, GitHub Actions, Terraform, etc.).
todos:
  - id: create_command_file
    content: Create .cursor/commands/generate-clean-code-tests.md command file with rule parsing logic
    status: pending
  - id: create_validator_module
    content: Create language-agnostic validator framework with language-specific parser adapters (Python AST, TypeScript parser, Rust parser, etc.)
    status: pending
  - id: create_rule_parser
    content: Create tests/_clean_code_rule_parser.py to parse markdown rules into structured data
    status: pending
  - id: implement_validators
    content: "Implement core validators: function length, line length, naming conventions, parameter count, etc."
    status: pending
    dependencies:
      - create_validator_module
  - id: create_config_system
    content: Create configuration system (.cursor/clean_code_test_config.yaml) for project-specific settings
    status: pending
  - id: generate_test_template
    content: Implement test file generation logic that creates test files in appropriate framework (pytest, jest, cargo test, etc.) based on detected project type
    status: pending
    dependencies:
      - create_validator_module
      - create_rule_parser
  - id: add_project_detection
    content: Add auto-detection of project structure (source paths, language, etc.)
    status: pending
    dependencies:
      - create_config_system
  - id: integrate_ci
    content: Ensure generated tests integrate with existing test suite and quality gate (pytest, jest, cargo test, etc. based on project)
    status: pending
    dependencies:
      - generate_test_template
  - id: add_language_parsers
    content: Implement language-specific parsers for Python (ast), TypeScript (typescript-eslint-parser), Rust (syn), shell (bash-parser), YAML (for GitHub Actions/Terraform)
    status: pending
    dependencies:
      - create_validator_module
  - id: add_documentation
    content: Add comprehensive documentation and usage examples to command file
    status: pending
    dependencies:
      - create_command_file
---

