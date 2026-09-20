"""
scratch/test_notes_structure.py
================================
Validates that generated notes for any course (standard or custom) adhere to the
7-section academic structure, contain concept-specific code, valid Viva Q&As,
clean Markdown-to-HTML rendering, and valid PDF export.
"""

import sys
import os
import io
import markdown
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Course_Generator_Engine import generate_course_modules
from PDF_Generator import build_pdf_styles, parse_markdown_to_flowables

REQUIRED_SECTIONS = [
    "## 1. Concept Overview & Practical Motivation",
    "## 2. Key Objectives & Learning Outcomes",
    "## 3. Core Technical Principles & Syntax Breakdown",
    "## 4. Practical Implementation Example",
    "## 5. Execution Output & Step-by-Step Walkthrough",
    "## 6. Common Pitfalls & Debugging Best Practices",
    "## 7. College Viva & Technical Interview Q&A"
]

TEST_TOPICS = [
    ("Python", "Beginner", 3),
    ("Java", "Beginner", 3),
    ("C++", "Beginner", 3),
    ("SQL", "Beginner", 3),
    ("HTML", "Beginner", 3),
    ("CSS", "Beginner", 3),
    ("DBMS", "Beginner", 3),
    ("Docker", "Beginner", 3),
    ("Machine Learning", "Intermediate", 3)
]

def test_note_structures():
    print("=== Testing Well-Structured Notes Across All Courses ===")
    
    for topic, diff, count in TEST_TOPICS:
        print(f"\n--> Testing topic: {topic} ({diff})...")
        modules = generate_course_modules(topic, diff, count)
        assert len(modules) == count, f"Expected {count} modules, got {len(modules)}"
        
        for mod in modules:
            notes = mod["notes"]
            assert notes.startswith(f"# {mod['title']}"), f"Missing module title header in: {mod['title']}"
            
            # Check all 7 sections
            for sec in REQUIRED_SECTIONS:
                assert sec in notes, f"Topic '{topic}', Module '{mod['title']}' missing section: {sec}"
            
            # Verify code sample block exists
            assert "```" in notes, f"Missing code block in {mod['title']}"
            assert "### Expected Output:" in notes, f"Missing Expected Output block in {mod['title']}"
            
            # Verify Viva Q&A structure
            assert "**Q1:" in notes and "**Answer**:" in notes, f"Missing Viva Q&A format in {mod['title']}"
            
            # Verify HTML conversion
            html = markdown.markdown(notes, extensions=["fenced_code", "tables", "nl2br"])
            assert "<h2>1. Concept Overview" in html or "<h2>1. Concept Overview &amp; Practical Motivation</h2>" in html, f"HTML header 2 failed for {mod['title']}"
            assert "<pre><code>" in html, f"HTML code block failed for {mod['title']}"
            
            # Verify PDF Generation without error
            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=letter)
            styles = build_pdf_styles()
            flowables = parse_markdown_to_flowables(notes, styles)
            assert len(flowables) > 10, "Flowables generation too short"
            doc.build(flowables)
            assert buf.getvalue().startswith(b"%PDF"), f"Invalid PDF output for {mod['title']}"
            
        print(f"    [OK] All {count} modules for '{topic}' passed 7-section structure, HTML & PDF tests!")

    print("\n=======================================================")
    print(" ALL 9 TOPICS & NOTE STRUCTURE CHECKS PASSED 100%! ")
    print("=======================================================")

if __name__ == "__main__":
    test_note_structures()
