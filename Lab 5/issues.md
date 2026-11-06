# Lab 5 — Static Code Analysis Issue Table

**File analyzed:** `scheduler_system.py`

> The line numbers below refer to the original version supplied in the repository. Re-run Pylint, Bandit, and Flake8 locally and update this table if your reports show additional findings or different line numbers.

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---:|---|---|
| Shell command built from a filename | Security (Bandit; potentially medium) | 32–35 | `os.system("cat " + file)` invokes a shell with a value that can be influenced by the caller, creating command-injection risk and depending on a Unix-specific command. | Removed `os.system`; use `Path.read_text()` to read and print the log directly. |
| Broad exception handler | Bug / reliability | 24–28 | Bare `except:` catches every exception and silently ignores errors, hiding programming and data problems. | Use `reservations.pop(reservation_id, None)` and return `False` when the reservation does not exist. |
| Mutable default argument | Bug / maintainability | 10 | `equipment_list=[]` uses a shared mutable default across calls. | Changed the default to `None` and create a new list inside the function. |
| File opened without a context manager | Reliability / resource management | 29–32 | `export_schedule` opens a file and closes it manually; an exception could prevent the close. | Use `with Path(file).open(...)` so the file is reliably closed. |
| Missing input/type validation | Bug / robustness | 13, 18–19, 36–38 | Malformed time slots or a non-string slot can cause unexpected exceptions; an end time earlier than the start can produce a negative duration. | Added `validate_time_slot`, validating the input format, integer hours, range, and start-before-end condition. |
| Double-booking is detected but not prevented | Logic bug | 12–15 | A conflicting reservation is appended to `conflicts` but the booking is still stored. | Reject duplicate room/time bookings with `ValueError` after recording the conflict. |
| Equipment availability is not checked | Logic bug | 16–17 | Equipment quantities can become negative, and unknown equipment names can cause a `KeyError`. | Validate equipment names and quantities before changing inventory. |
| Script runs on import | Maintainability / testability | 48 | `main()` runs immediately when the module is imported, making isolated testing or reuse harder. | Added the `if __name__ == "__main__":` guard. |
| Naming and formatting | Style (Pylint/Flake8) | 36 | `logConflicts` does not follow the usual `snake_case` function naming convention. | Renamed it to `log_conflicts` and formatted the updated code consistently. |

## Verification notes

The original source was inspected and the fixes above were applied. The analysis tools could not be installed in the execution environment used to prepare this submission because package downloads were unavailable. Therefore, no genuine before/after Pylint, Bandit, or Flake8 output or final Pylint score is claimed here. Run the commands in `README.md` on your machine and save the actual reports before submitting.
