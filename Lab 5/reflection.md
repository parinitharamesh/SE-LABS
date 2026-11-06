# Lab 5 — Reflection

**Important:** The supplied three-page handout refers to reflection questions but does not include their exact wording. The responses below address four common reflection themes; replace the prompts with the exact questions if your instructor provided them separately.

## 1. What is static code analysis, and why is it useful?

Static code analysis examines source code without running the program. It helps identify potential bugs, unsafe patterns, maintainability concerns, and style violations early. This makes code easier to review and reduces the chance that avoidable problems reach users.

## 2. What is the difference between Pylint, Bandit, and Flake8?

Pylint checks code quality and possible programming mistakes, including naming and design concerns. Bandit focuses on common Python security risks. Flake8 checks style and formatting, including many PEP 8 violations. Using all three provides complementary checks rather than relying on a single tool.

## 3. What issues did you identify and how did you fix them?

The supplied scheduler had a mutable list as a default argument, a bare exception handler that silently swallowed errors, file handling without a context manager, and a shell command constructed using a filename. It also allowed duplicate bookings, did not validate time slots, and could decrement equipment inventory below zero. I changed the default argument to `None`, handled missing reservations explicitly, used context managers, removed the shell command, validated time slots and equipment, and rejected conflicting bookings.

## 4. What did you learn, and what are the limitations of static analysis?

The exercise shows that static analysis can reveal issues that are easy to overlook during manual review. However, tools cannot prove that the program's behavior is correct in every situation. For example, business rules such as preventing double bookings and maintaining equipment inventory need suitable logic and tests. Tool output should be reviewed, and the program should also be run with valid and invalid inputs. The final reports and score must be generated locally to verify the fixes.
