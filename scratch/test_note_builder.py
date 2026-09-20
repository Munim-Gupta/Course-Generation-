"""
scratch/test_note_builder.py
"""
import urllib.parse
import re

def detect_concept_category(title, summary):
    text = f"{title} {summary}".lower()
    if any(k in text for k in ["intro", "setup", "architecture", "overview", "installation", "environment", "compiler", "interpreter"]):
        return "setup_intro"
    if any(k in text for k in ["variable", "constant", "data type", "primitive", "memory model", "typing"]):
        return "variables_types"
    if any(k in text for k in ["control flow", "condition", "branch", "decision", "if-else", "switch"]):
        return "control_flow"
    if any(k in text for k in ["loop", "iteration", "traversal", "while", "for loop", "sequences"]):
        return "loops_iteration"
    if any(k in text for k in ["function", "method", "procedure", "parameter", "return", "modular", "lambda", "closure", "scope"]):
        return "functions_methods"
    if any(k in text for k in ["class", "object", "oop", "inheritance", "polymorphism", "encapsulation", "constructor", "interface", "metaclass", "magic method"]):
        return "oop_classes"
    if any(k in text for k in ["list", "array", "tuple", "set", "dictionary", "map", "hash", "tree", "queue", "stack", "collection", "stl"]):
        return "data_structures"
    if any(k in text for k in ["string", "text", "formatting", "slicing", "regex", "parsing"]):
        return "strings_text"
    if any(k in text for k in ["file", "i/o", "stream", "disk", "serialization", "json", "csv"]):
        return "file_io"
    if any(k in text for k in ["error", "exception", "try", "catch", "debugging", "logging", "assert"]):
        return "error_handling"
    if any(k in text for k in ["thread", "concurrency", "async", "await", "multiprocessing", "event loop", "asynchronous"]):
        return "async_concurrency"
    if any(k in text for k in ["sql", "table", "query", "select", "join", "database", "crud", "acid", "relational", "schema", "normalization", "index"]):
        return "database_sql"
    if any(k in text for k in ["api", "rest", "flask", "endpoint", "http", "route", "html", "css", "dom", "event", "form", "web"]):
        return "web_api"
    if any(k in text for k in ["docker", "container", "devops", "deploy", "ci/cd", "package", "project", "capstone", "cli"]):
        return "devops_capstone"
    return "general"

print("Category detection function defined.")
