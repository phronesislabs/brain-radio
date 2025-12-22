---
description: "Generate a comprehensive code review checklist as todos and documentation based on Clean Code principles"
---

# Code Review Checklist Generator

**CRITICAL INSTRUCTION: You MUST use the `todo_write` tool to create todos. Creating only a markdown file is NOT sufficient. This command requires BOTH todos AND optional documentation.**

## Step 1: Create Todos (MANDATORY)

You MUST call `todo_write` with `merge=false` to create a fresh todo list containing ALL Clean Code review checklist items.

### Todo Categories and Items

Create todos for each of these items. Use the format: `"[Category] - [Item Name]: [Description]"`

#### Meaningful Names (14 items)
- Intention-Revealing Names: Verify all variables, functions, and classes have names that clearly reveal their intent
- No Single-Letter Names: Check that single-letter names are only used for loop counters (i, j, k) or lambda parameters
- Meaningful Distinctions: Ensure no noise words (data, info, object, variable) or number series (a1, a2, a3)
- Pronounceable Names: Verify all names are pronounceable and easy to say
- Searchable Names: Check that magic numbers are replaced with named constants
- No Mental Mapping: Verify names don't require mental translation
- Class Names: Check that classes use nouns or noun phrases
- Method Names: Verify methods use verbs or verb phrases
- Accessor/Mutator Names: Check accessors, mutators, and predicates are named for their value
- One Word per Concept: Verify consistent terminology throughout (don't mix fetch, retrieve, get)
- No Puns: Check that the same word is not used for two different purposes
- Solution Domain Names: Verify computer science terms are used appropriately
- Problem Domain Names: Check problem domain terminology is used when no programming term exists
- Meaningful Context: Verify prefixes or classes/namespaces provide context when needed

#### Functions (11 items)
- Small Functions: Verify all functions are small (ideally < 20 lines)
- Single Responsibility: Check each function does one thing and does it well
- One Level of Abstraction: Verify statements in functions are at the same abstraction level
- Descriptive Names: Check function names clearly describe what they do
- Few Arguments: Verify functions have minimal arguments (zero is best, one is good, two is acceptable, three should be avoided)
- No Flag Arguments: Check boolean flags that indicate multiple behaviors are replaced with separate functions
- No Side Effects: Verify functions don't have hidden side effects
- Command Query Separation: Check functions either do something (command) or answer something (query), not both
- Prefer Exceptions: Verify exceptions are used instead of error return codes
- Extracted Try-Catch: Check try-catch blocks are extracted into separate functions
- DRY Principle: Verify no code duplication; common functionality is extracted

#### Comments (6 items)
- Self-Documenting Code: Verify code is clear enough that comments are rarely needed
- No Redundant Comments: Check no comments simply restate what the code does
- No Commented-Out Code: Verify all commented-out code is removed (use version control instead)
- Good Comments Only: Check comments explain "why" not "what" (legal, informative, intent, warnings, TODOs with references)
- No Bad Comments: Verify no mumbling, misleading, mandated, journal, noise, scary, HTML, or non-local comments
- Public API Documentation: Check public APIs have appropriate documentation

#### Formatting (9 items)
- Vertical Formatting: Verify related concepts are kept close together vertically
- Variable Declarations: Check variables are declared close to their usage
- Instance Variables: Verify instance variables are declared at top of class
- Dependent Functions: Check caller functions appear above callee functions when possible
- Conceptual Affinity: Verify related concepts are grouped together
- Horizontal Formatting: Check lines are kept short (ideally < 120 characters, max 200)
- Indentation: Verify proper indentation is used to show scope
- Team Formatting Rules: Check code follows team's agreed-upon formatting style
- Automated Formatting: Verify automated formatters (ruff, black, prettier) are used and passing

#### Objects and Data Structures (6 items)
- Data Abstraction: Verify internal structure is hidden behind abstract interfaces
- No Exposed Internals: Check internal data is not exposed through accessors/mutators unnecessarily
- Data/Object Separation: Verify clear distinction between objects (hide data, expose functions) and data structures (expose data, no functions)
- Law of Demeter: Check no chained method calls (obj.get_a().get_b().get_c())
- Encapsulated Chains: Verify method chains are encapsulated within appropriate methods
- DTOs When Appropriate: Check Data Transfer Objects are used appropriately for simple data structures

#### Error Handling (7 items)
- Exceptions Over Return Codes: Verify exceptions are used instead of error return codes
- Try-Catch-Finally First: Check exception handling is written before business logic
- Context in Exceptions: Verify exceptions include enough context to locate source and cause
- Exception Classes: Check exception classes are defined based on how they're caught
- Wrapped Third-Party APIs: Verify third-party APIs are wrapped with custom exception types
- No Null Returns: Check methods don't return null; use exceptions or special case objects
- No Null Arguments: Verify methods don't accept null; validate and throw exceptions

#### Boundaries (5 items)
- Wrapped Third-Party Code: Verify third-party APIs are wrapped to avoid dependency on their interfaces
- Adapter Layers: Check adapter layers isolate external dependencies
- Learning Tests: Verify learning tests are written for third-party code
- Clean Boundaries: Check boundaries are kept clean and well-defined
- Minimal Third-Party Knowledge: Verify code doesn't expose too much third-party implementation detail

#### Unit Tests (7 items)
- TDD Followed: Check tests are written before production code (Three Laws of TDD)
- Clean Test Code: Verify test code is clean, readable, and maintainable
- One Assert per Test: Check each test verifies one concept
- F.I.R.S.T. Principles: Verify tests are Fast, Independent, Repeatable, Self-Validating, and Timely
- Test Coverage: Check adequate test coverage (≥95% as per project standards)
- Test Readability: Verify tests are clear, concise, and expressive
- Test Organization: Check tests are organized logically and consistently

#### Classes (5 items)
- Small Classes: Verify classes are small and focused
- Single Responsibility: Check each class has only one reason to change (SRP)
- High Cohesion: Verify classes have high cohesion (methods and variables are dependent on each other)
- Organized for Change: Check classes are organized to make change easy
- Isolated Changes: Verify changes are isolated to specific classes

#### SOLID Principles (5 items)
- Single Responsibility Principle (SRP): Check each class has a single, well-defined purpose
- Open/Closed Principle (OCP): Verify classes are open for extension, closed for modification
- Liskov Substitution Principle (LSP): Check subtypes are substitutable for their base types
- Interface Segregation Principle (ISP): Verify clients are not forced to depend on unused interfaces
- Dependency Inversion Principle (DIP): Check dependencies are on abstractions, not concretions

#### Systems (4 items)
- Construction Separated from Use: Verify startup process (construction) is separated from runtime logic (use)
- Dependency Injection: Check dependencies are injected through constructors or setters
- Abstractions Over Concretions: Verify code depends on abstractions, not concrete implementations
- Appropriate Architecture: Check appropriate architectural patterns are used for system design

#### Emergence (5 items)
- Simple Design Rules: Verify code follows simple design rules (runs all tests, no duplication, expresses intent, minimizes classes/methods)
- Continuous Refactoring: Check code is continuously refactored to improve design
- No Duplication: Verify duplication is eliminated through abstraction
- Clear Intent: Check code clearly expresses intent
- Minimal Complexity: Verify classes and methods are minimized

#### Concurrency (10 items)
- Concurrency Code Separated: Check concurrency code is separated from business logic (SRP)
- Limited Scope of Data: Verify access to shared data is limited
- Copies of Data: Check copies of data are used to avoid shared mutable state
- Independent Threads: Verify threads are as independent as possible
- Known Libraries: Check concurrency libraries are understood and used correctly
- Known Execution Model: Verify execution model (thread pools, producer-consumer, etc.) is understood
- Synchronized Methods: Check dependencies between synchronized methods are understood
- Small Synchronized Sections: Verify synchronized sections are kept small
- Thread-Safe Code: Check critical sections are thread-safe
- No Shared Mutable State: Verify immutable objects are preferred over shared mutable state

#### Code Smells (14 items)
- No Excessive Comments: Check too many comments don't indicate unclear code
- No Long Methods: Verify methods are short and focused
- No Long Parameter Lists: Check parameter lists are short (use parameter objects if needed)
- No Duplicated Code: Verify duplication is eliminated
- No Dead Code: Check unused code, variables, and methods are removed
- No Speculative Generality: Verify no "just in case" functionality (YAGNI)
- No Feature Envy: Check methods don't use more features of another class than their own
- No Data Clumps: Verify groups of related data are extracted into objects
- No Primitive Obsession: Check value objects are used instead of primitives for meaningful concepts
- No Long Classes: Verify classes are small and focused
- No Large Classes: Check classes don't do too much
- No Large Switch Statements: Verify polymorphism is used instead of large switch statements
- No Temporary Fields: Check fields only used in certain circumstances are extracted into separate classes
- No Refused Bequest: Verify composition is considered over inheritance when subclasses don't use inherited functionality

#### Heuristics (9 items)
- Boy Scout Rule: Check code is left cleaner than it was found
- Continuous Refactoring: Verify code is refactored continuously
- TDD Practice: Check test-driven development is followed
- Small Functions: Verify functions are kept small
- Small Classes: Check classes are kept small
- Meaningful Names: Verify names are meaningful and intention-revealing
- No Duplication: Check duplication is avoided
- Clear Intent: Verify intent is expressed clearly
- Minimal Complexity: Check complexity is minimized

#### Additional Custom Checks (variable items)
- Add any custom code review tasks that should be checked (read from project-specific requirements)

## Step 2: Create Documentation File (OPTIONAL)

After creating todos, you may optionally create `docs/CODE_REVIEW.md` with the full checklist for historical documentation.

## Implementation Requirements

**YOU MUST:**

1. Call `todo_write` with `merge=false` immediately
2. Create todos for ALL items listed above (approximately 120+ todos)
3. Use descriptive todo content in format: `"[Category] - [Item]: [Description]"`
4. Set initial status to `pending` for all todos
5. Use unique IDs for each todo (e.g., `clean-code-names-intention`, `clean-code-functions-small`)

**Example todo:**

```json
{
  "id": "clean-code-names-intention",
  "status": "pending",
  "content": "Meaningful Names - Intention-Revealing Names: Verify all variables, functions, and classes have names that clearly reveal their intent"
}
```

**After creating todos, you may optionally:**

- Create `docs/CODE_REVIEW.md` with the full checklist for documentation purposes

## Important Notes

- **Todos are MANDATORY** - The command is not complete without creating todos using `todo_write`
- **Documentation is OPTIONAL** - The markdown file is for reference only
- **Deterministic** - Same todos should be created every time this command runs
- **Extensible** - Additional custom checks can be added to the "Additional Custom Checks" category

## Related Rules

- [clean_code.mdc](mdc:.cursor/rules/clean_code.mdc): Complete Clean Code principles and guidelines
- [auto-checks.mdc](mdc:.cursor/rules/auto-checks.mdc): Automatic quality checks
- [cursor_rules.mdc](mdc:.cursor/rules/cursor_rules.mdc): Guidelines for creating and maintaining rules
