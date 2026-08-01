# Learnings from custom_logger.py

## OOP Fundamentals Covered

### What is a Class?
- A **blueprint** — describes what every object built from it will look like
- Example: `CustomLogger` is the blueprint

### What is an Object / Instance?
- The actual thing created from the blueprint
- `logger_one = CustomLogger("logs/app")` → `logger_one` is the object
- Object and Instance mean the same thing

### What is `self`?
- Means "me" — the specific object being worked on right now
- Every instance method must have `self` as first parameter
- Python automatically passes the object in when you call a method
- `logger_one.get_logger()` → Python translates to `CustomLogger.get_logger(logger_one)`

### `self` — Parameter vs Attribute

| Thing | What it is | Example |
|---|---|---|
| `self` in the signature | **Parameter** — receives the object | `def __init__(self):` |
| `self.logs_dir` | **Instance attribute** — stored on the object | `self.logs_dir = "logs/"` |

- `self` is just the parameter that holds a reference to the current object — not special syntax, just a convention
- When you write `self.logs_dir = "logs/"` you are **attaching** `logs_dir` to the object
- Think of it as: the object is a box, `logs_dir` is a label on the box, `"logs/"` is what's inside
- Each object gets its own box with its own labels and values

### What is `__init__`?
- A special **dunder method** (double underscore = called automatically by Python)
- Runs immediately when an object is created
- Its job: fill in the object's fields at birth
- You never call it directly — Python calls it for you

### Three Types of Variables

| Type | Syntax | Lives until |
|---|---|---|
| Local variable | `x = ...` inside a method | Method finishes |
| Instance variable | `self.x = ...` | Object is destroyed |
| Class variable | defined in class body | Program ends |

### Instance Variables
- Start with `self.` inside a class
- Owned by one specific object
- Each object has its own independent copy
- Example: `self.logs_dir` — each logger has its own logs folder path

### Class Variables
- Defined directly in the class body, outside any method
- Shared across ALL objects
- Changing it affects every object
- Accessed via `ClassName.variable_name`
- Example use case: `log_count` to track how many loggers were created

---

## Production Bug Found in custom_logger.py

### The Bug
`logging.basicConfig` only works **once per program run**. If you create two `CustomLogger` objects, the second one's configuration is silently ignored.

```python
logger1 = CustomLogger("logs/app")     # works fine
logger2 = CustomLogger("logs/errors")  # basicConfig silently ignored!
# logger2 logs still go to logger1's file
```

### Why Python Does This
`basicConfig` checks `if len(root.handlers) == 0` — if handlers already exist, it skips silently. Design decision: "user probably configured this intentionally."

### The Fix (for later)
Use `logging.getLogger()` with explicit handlers instead of `basicConfig`. Gives full control, no silent failures.

---

## Other Observations

### `exist_ok=True` in `os.makedirs`
- If the folder already exists → does nothing, no error
- Safe to call multiple times

### Local variables in `__init__`
- `log_file` and `log_file_path` are local variables (no `self.`)
- They disappear after `__init__` finishes
- But the **file on disk** already exists independently — the variable dying doesn't affect it
- Each new `CustomLogger` object creates a brand new timestamped log file

### `__file__` as default parameter
- `def get_logger(self, name=__file__)` — default is the current file's path
- `os.path.basename(name)` extracts just the filename without the full path

---

## Key Mindset Shift
> Code that *runs* but does the *wrong thing* silently is worse than code that crashes.
> A crash tells you something is wrong. Silent failures hide bugs.
