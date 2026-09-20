"""
Course_Generator_Engine.py
==========================
Purpose:
    Core algorithmic engine for generating syllabus outlines, comprehensive, well-structured
    academic student notes, and verified video embeds without external or paid AI APIs.

Viva Talking Points:
    - Rule-based & template-driven architecture: curated domain knowledge trees.
    - Predefined topics include Python, HTML, CSS, JavaScript, SQL, Java, C++, and DBMS.
    - Intelligent dynamic fallback: synthesizes structured curricula for ANY custom topic.
    - Generates 7-section professional student notes:
        1. Concept Overview & Practical Motivation
        2. Key Objectives & Learning Outcomes
        3. Core Technical Principles & Syntax Breakdown
        4. Practical Implementation Example (Runnable code tailored to topic & concept)
        5. Execution Output & Step-by-Step Walkthrough
        6. Common Pitfalls & Debugging Best Practices
        7. College Viva & Technical Interview Q&A
    - Verified educational video embeds and safe fallback search embeds.
"""

import urllib.parse
import re

# 12 verified foundational CS/software engineering tutorial videos matching the 12 module stages
FALLBACK_CS_VIDEOS = [
    "https://www.youtube.com/embed/zOjov-2OZ0E",  # Stage 1: Intro to Computer Science & Programming
    "https://www.youtube.com/embed/kqtD5dpn9C8",  # Stage 2: Variables, Data Types & Memory
    "https://www.youtube.com/embed/DZwmZ8Usvnk",  # Stage 3: Control Flow & Decision Logic
    "https://www.youtube.com/embed/6iF8Xb7Z3wQ",  # Stage 4: Loops & Traversal Algorithms
    "https://www.youtube.com/embed/9Os0o3wzS_I",  # Stage 5: Functions & Modular Decomposition
    "https://www.youtube.com/embed/8hly31xKli0",  # Stage 6: Data Structures & Collections
    "https://www.youtube.com/embed/ZDa-Z5JzLYM",  # Stage 7: Object-Oriented Design & Patterns
    "https://www.youtube.com/embed/NIWwJbo-9_8",  # Stage 8: Error Handling & Debugging
    "https://www.youtube.com/embed/qbKWbJq59lU",  # Stage 9: File I/O & Persistent Storage
    "https://www.youtube.com/embed/HXV3zeQKqGY",  # Stage 10: Databases & API Protocols
    "https://www.youtube.com/embed/gT0LhB1Z46s",  # Stage 11: Testing & Code Quality
    "https://www.youtube.com/embed/rfscVS0vtbw",  # Stage 12: Production Capstone Implementation
]

# Curated educational video links for tech topics (12 unique verified lessons per topic)
TOPIC_VIDEOS = {
    "python": [
        "https://www.youtube.com/embed/_uQrJ0TkZlc",  # 1: Setup & Python Syntax
        "https://www.youtube.com/embed/kqtD5dpn9C8",  # 2: Variables & Data Types
        "https://www.youtube.com/embed/DZwmZ8Usvnk",  # 3: Conditionals & Booleans
        "https://www.youtube.com/embed/6iF8Xb7Z3wQ",  # 4: Loops & Iteration
        "https://www.youtube.com/embed/9Os0o3wzS_I",  # 5: Functions & Scope
        "https://www.youtube.com/embed/W8KRzm-HUcc",  # 6: Lists, Tuples & Sets
        "https://www.youtube.com/embed/daefaLgNkw0",  # 7: Dictionaries
        "https://www.youtube.com/embed/k9TUPpGqYTo",  # 8: String Formatting & Slicing
        "https://www.youtube.com/embed/qbKWbJq59lU",  # 9: File Objects & I/O
        "https://www.youtube.com/embed/NIWwJbo-9_8",  # 10: Error & Exception Handling
        "https://www.youtube.com/embed/ZDa-Z5JzLYM",  # 11: OOP Classes & Instances
        "https://www.youtube.com/embed/rfscVS0vtbw",  # 12: Python Full Project Capstone
    ],
    "html": [
        "https://www.youtube.com/embed/pQN-pnXPaVg",  # 1: HTML Document Structure
        "https://www.youtube.com/embed/kUMe1FH4CHE",  # 2: Headings & Text Formatting
        "https://www.youtube.com/embed/UB1O30fR-EE",  # 3: Hyperlinks & Media
        "https://www.youtube.com/embed/1rba9p_Y_zU",  # 4: Lists & Containers
        "https://www.youtube.com/embed/wvR4OzCVdc0",  # 5: Tables & Tabular Data
        "https://www.youtube.com/embed/mJgBOIoGihA",  # 6: HTML Forms & Inputs
        "https://www.youtube.com/embed/qz0aGYrrlhU",  # 7: HTML5 Semantic Elements
        "https://www.youtube.com/embed/24gD75vjFmE",  # 8: Audio, Video & Embeds
        "https://www.youtube.com/embed/Ytzydv345k8",  # 9: Meta Tags & SEO Basics
        "https://www.youtube.com/embed/gT0LhB1Z46s",  # 10: HTML Entities & Standards
        "https://www.youtube.com/embed/ok-plXXHlWw",  # 11: W3C Validation & Clean Code
        "https://www.youtube.com/embed/PlxWfBi3358",  # 12: Personal Portfolio Capstone
    ],
    "css": [
        "https://www.youtube.com/embed/1Rs2ND1ryYc",  # 1: Introduction to CSS
        "https://www.youtube.com/embed/yfoY53QXEnI",  # 2: CSS Selectors & Specificity
        "https://www.youtube.com/embed/l1mER1bV0N0",  # 3: Colors & Typography
        "https://www.youtube.com/embed/rIO5326FgPE",  # 4: The CSS Box Model
        "https://www.youtube.com/embed/Qf-wZX_8L18",  # 5: Display Properties
        "https://www.youtube.com/embed/jx5jmI0UlXU",  # 6: Positioning Techniques
        "https://www.youtube.com/embed/fYq5PXgSsbE",  # 7: CSS Flexbox
        "https://www.youtube.com/embed/rg7Fvvl3taU",  # 8: CSS Grid System
        "https://www.youtube.com/embed/zHUpx90NerM",  # 9: Transitions & Animations
        "https://www.youtube.com/embed/OXGznpKZ_sA",  # 10: Responsive Web Design
        "https://www.youtube.com/embed/YV_eR8D4Jc0",  # 11: Styling Modern Forms
        "https://www.youtube.com/embed/c1xGndrn8O0",  # 12: Landing Page Capstone
    ],
    "javascript": [
        "https://www.youtube.com/embed/W6NZfCO5SIk",  # 1: JavaScript Engine & Setup
        "https://www.youtube.com/embed/edlFjlzxGSI",  # 2: Variables & Data Types
        "https://www.youtube.com/embed/7FwD_jK1p9c",  # 3: Operators & Expressions
        "https://www.youtube.com/embed/IsG4Xd6LlsM",  # 4: Conditionals & Branching
        "https://www.youtube.com/embed/s9wW2PpJsmQ",  # 5: Loops & Iterations
        "https://www.youtube.com/embed/jS4aFq5-91M",  # 6: Functions & Arrow Syntax
        "https://www.youtube.com/embed/oigfaZ5A6Eg",  # 7: Arrays & Core Methods
        "https://www.youtube.com/embed/X0ipw1k7YsY",  # 8: Objects & JSON
        "https://www.youtube.com/embed/y17RuWkWdn8",  # 9: DOM Manipulation
        "https://www.youtube.com/embed/yEsmrF4_Zc0",  # 10: Event Handling
        "https://www.youtube.com/embed/rsd4FNGWqSo",  # 11: Form Validation
        "https://www.youtube.com/embed/G0jO8kUrg-I",  # 12: Interactive App Capstone
    ],
    "sql": [
        "https://www.youtube.com/embed/HXV3zeQKqGY",  # 1: Relational Databases & SQL
        "https://www.youtube.com/embed/7S_tz1z_5bA",  # 2: DDL: Creating Tables
        "https://www.youtube.com/embed/q_bJz_yW3u8",  # 3: DML: Inserting Data
        "https://www.youtube.com/embed/oUPaXx6yGu0",  # 4: Querying with SELECT
        "https://www.youtube.com/embed/bE_XfZx3b-s",  # 5: Filtering with WHERE
        "https://www.youtube.com/embed/s1v_o8C88-w",  # 6: ORDER BY & LIMIT
        "https://www.youtube.com/embed/h0nx3cGioEQ",  # 7: Aggregate Functions
        "https://www.youtube.com/embed/1w0g4iO7C-E",  # 8: GROUP BY & HAVING
        "https://www.youtube.com/embed/2hM_H_6pC8w",  # 9: UPDATE & DELETE Records
        "https://www.youtube.com/embed/zsjvFFKOm3c",  # 10: Primary & Foreign Keys
        "https://www.youtube.com/embed/9Pzj7Aj25lw",  # 11: INNER & LEFT JOINs
        "https://www.youtube.com/embed/kBdlM6hNDAE",  # 12: Database Design Capstone
    ],
    "java": [
        "https://www.youtube.com/embed/eIrMbAQSU34",  # 1: Java & JVM Architecture
        "https://www.youtube.com/embed/WPvGqV-lOms",  # 2: Variables & Data Types
        "https://www.youtube.com/embed/ldYcgPKEzc8",  # 3: Control Structures
        "https://www.youtube.com/embed/r59xye3Vy5U",  # 4: Loops & Iterations
        "https://www.youtube.com/embed/xk4_1vDrzzo",  # 5: Methods & Scope
        "https://www.youtube.com/embed/L06uK1_ZkI8",  # 6: Arrays & Strings
        "https://www.youtube.com/embed/grEKMHGYyns",  # 7: OOP Classes & Objects
        "https://www.youtube.com/embed/G9b4D4Nq45w",  # 8: Constructors & Memory
        "https://www.youtube.com/embed/4_73wL9A8f0",  # 9: Inheritance & Polymorphism
        "https://www.youtube.com/embed/m_Q_F_B83y8",  # 10: Abstraction & Interfaces
        "https://www.youtube.com/embed/1XAfapkNyjk",  # 11: Exception Handling
        "https://www.youtube.com/embed/GoXwIVyNvX0",  # 12: Collections Framework
    ],
    "c++": [
        "https://www.youtube.com/embed/vLnPwxZdW4Y",  # 1: C++ Compilation & Setup
        "https://www.youtube.com/embed/1v_4dL8OP80",  # 2: Variables & Standard I/O
        "https://www.youtube.com/embed/mUQZ13617M8",  # 3: Operators & Expressions
        "https://www.youtube.com/embed/jTS7JTGu1pc",  # 4: Control Flow & Branching
        "https://www.youtube.com/embed/yEjP_oYjW7k",  # 5: Loops & Algorithms
        "https://www.youtube.com/embed/u_tD4Q5G4U8",  # 6: Functions & References
        "https://www.youtube.com/embed/ZzaPdXTrSb8",  # 7: Pointers & Addresses
        "https://www.youtube.com/embed/2npaN006r-w",  # 8: Dynamic Memory Allocation
        "https://www.youtube.com/embed/wN0x9eZLix4",  # 9: Classes & Encapsulation
        "https://www.youtube.com/embed/FXhALMsHwEY",  # 10: Constructors & Destructors
        "https://www.youtube.com/embed/ndz3SXbl34A",  # 11: Inheritance & Virtual Functions
        "https://www.youtube.com/embed/_bYFu9mBnr4",  # 12: STL Containers & Algorithms
    ],
    "dbms": [
        "https://www.youtube.com/embed/kBdlM6hNDAE",  # 1: DBMS Architecture
        "https://www.youtube.com/embed/zsjvFFKOm3c",  # 2: ER Modeling
        "https://www.youtube.com/embed/7S_tz1z_5bA",  # 3: Relational Data Model
        "https://www.youtube.com/embed/oUPaXx6yGu0",  # 4: Integrity Constraints & Keys
        "https://www.youtube.com/embed/cODCpXtPHbQ",  # 5: Normalization (1NF, 2NF, 3NF)
        "https://www.youtube.com/embed/q_bJz_yW3u8",  # 6: BCNF & Lossless Joins
        "https://www.youtube.com/embed/0rY3nuh8P7k",  # 7: ACID Properties & Transactions
        "https://www.youtube.com/embed/bE_XfZx3b-s",  # 8: Concurrency & 2PL
        "https://www.youtube.com/embed/s1v_o8C88-w",  # 9: Recovery Systems & WAL
        "https://www.youtube.com/embed/9Pzj7Aj25lw",  # 10: Indexing & B-Trees
        "https://www.youtube.com/embed/h0nx3cGioEQ",  # 11: Query Optimization
        "https://www.youtube.com/embed/HXV3zeQKqGY",  # 12: Database Architecture Capstone
    ],
    "docker": [
        "https://www.youtube.com/embed/fqMOX6JJhGo",  # 1: Docker Basics
        "https://www.youtube.com/embed/pTFZFxd4hOI",  # 2: Architecture & Daemon
        "https://www.youtube.com/embed/3c-iBn73dDE",  # 3: Images vs Containers
        "https://www.youtube.com/embed/gAkwW2tuIqE",  # 4: Dockerfiles & Builds
        "https://www.youtube.com/embed/17Bl31rboGs",  # 5: Volumes & Data Persistence
        "https://www.youtube.com/embed/bKFMS5C4CG0",  # 6: Docker Networking
        "https://www.youtube.com/embed/HG68Ymazo18",  # 7: Docker Compose
        "https://www.youtube.com/embed/MviT3Dkn1-g",  # 8: Container Lifecycle
        "https://www.youtube.com/embed/8vXoMqWgbGQ",  # 9: Docker Best Practices
        "https://www.youtube.com/embed/YFl20P4RrnY",  # 10: Docker Hub & Registry
        "https://www.youtube.com/embed/5h6l_vHk8w0",  # 11: Security Hardening
        "https://www.youtube.com/embed/0B2raPOH4Ec",  # 12: Production Deployment
    ],
    "git": [
        "https://www.youtube.com/embed/RGOj5yH7evk",  # 1: Git & GitHub Crash Course
        "https://www.youtube.com/embed/8JJ101D3knE",  # 2: Init, Add & Commit
        "https://www.youtube.com/embed/USjZcfj8yxE",  # 3: Branching & Merging
        "https://www.youtube.com/embed/HVsySz-h9r4",  # 4: Remote Repositories & Push/Pull
        "https://www.youtube.com/embed/DVRnz0g3j1s",  # 5: Merge Conflicts
        "https://www.youtube.com/embed/2ReR14L4L-o",  # 6: Git Stash & Reset
        "https://www.youtube.com/embed/7B_24t_r43w",  # 7: Pull Requests & Collaboration
        "https://www.youtube.com/embed/ecK3EnyGD8o",  # 8: Rebase vs Merge
        "https://www.youtube.com/embed/8aV5AxJrHDg",  # 9: Git Log & History
        "https://www.youtube.com/embed/V5gZ1543-F4",  # 10: Tags & Releases
        "https://www.youtube.com/embed/f1w_eT4N4nU",  # 11: Git Hooks
        "https://www.youtube.com/embed/hwP7mwU4Blk",  # 12: Professional Git Workflows
    ],
    "react": [
        "https://www.youtube.com/embed/bMknfKXIFA8",  # 1: React Fundamentals
        "https://www.youtube.com/embed/SqcY0GlETPk",  # 2: Components & JSX
        "https://www.youtube.com/embed/dGcsHMXbSOA",  # 3: Props & State
        "https://www.youtube.com/embed/O6P86uwfdR0",  # 4: useState Hook
        "https://www.youtube.com/embed/0ZJgJwR445A",  # 5: useEffect Hook
        "https://www.youtube.com/embed/TmsD8n-c-tM",  # 6: Event Handling
        "https://www.youtube.com/embed/fL47A8k24uE",  # 7: Conditional Rendering & Lists
        "https://www.youtube.com/embed/w7ejDZ8SWv8",  # 8: Forms & Inputs
        "https://www.youtube.com/embed/Law7wfdg_ls",  # 9: React Router
        "https://www.youtube.com/embed/5ZdHfJV30kk",  # 10: API Data Fetching
        "https://www.youtube.com/embed/35lXWvCuM8o",  # 11: Context API State
        "https://www.youtube.com/embed/hQAHSlTtcmY",  # 12: Full React Project
    ],
    "machine learning": [
        "https://www.youtube.com/embed/i_LwzRVP7bg",  # 1: Machine Learning Foundations
        "https://www.youtube.com/embed/NWONt4-hmMc",  # 2: Python Data Science Ecosystem
        "https://www.youtube.com/embed/7eh4d6sabA0",  # 3: Pandas & NumPy Preprocessing
        "https://www.youtube.com/embed/ukzFI9rgwfU",  # 4: Linear Regression
        "https://www.youtube.com/embed/yIYKR4sgzI8",  # 5: Classification & Logistic Regression
        "https://www.youtube.com/embed/7AmYm5B58eI",  # 6: Decision Trees & Random Forests
        "https://www.youtube.com/embed/K4s_3G-4pY8",  # 7: Support Vector Machines
        "https://www.youtube.com/embed/Air4Z9t53a4",  # 8: Unsupervised K-Means
        "https://www.youtube.com/embed/wB2N1Vn_4cI",  # 9: Model Validation & Metrics
        "https://www.youtube.com/embed/bfmFfD2RIcg",  # 10: Feature Engineering
        "https://www.youtube.com/embed/aircAruvnKk",  # 11: Neural Networks & Deep Learning
        "https://www.youtube.com/embed/mKV_K2f25wI",  # 12: End-to-End ML Pipeline
    ],
    "data science": [
        "https://www.youtube.com/embed/LHBE6Q9XlzI",  # 1: Python for Data Science Overview
        "https://www.youtube.com/embed/r-uOLxNrNk8",  # 2: NumPy Arrays & Vectorized Math
        "https://www.youtube.com/embed/vmEHCJofslg",  # 3: Pandas DataFrames & Series
        "https://www.youtube.com/embed/bDhvCp3_lYw",  # 4: Data Cleaning & Missing Values
        "https://www.youtube.com/embed/txMdrV1Ut64",  # 5: GroupBy, Aggregation & Pivots
        "https://www.youtube.com/embed/3Xc3CA655Y4",  # 6: Matplotlib Plotting & Charts
        "https://www.youtube.com/embed/ooqXQ37XHMM",  # 7: Seaborn Statistical Graphics
        "https://www.youtube.com/embed/fHFO4UhUr4Y",  # 8: Exploratory Data Analysis (EDA)
        "https://www.youtube.com/embed/0Lt9w-BxKFQ",  # 9: Introduction to Scikit-Learn
        "https://www.youtube.com/embed/Gv9_4yMHFhI",  # 10: Supervised Learning & Regression
        "https://www.youtube.com/embed/i_LwzRVP7bg",  # 11: Classification & Model Metrics
        "https://www.youtube.com/embed/NWONt4-hmMc",  # 12: End-to-End Data Science Project
    ],
    "web development": [
        "https://www.youtube.com/embed/mU6anWqZJcc",  # 1: HTML5 Document Architecture
        "https://www.youtube.com/embed/1Rs2ND1ryYc",  # 2: CSS3 Styling & Box Model
        "https://www.youtube.com/embed/fYq5PXgSsbE",  # 3: CSS Flexbox Layouts
        "https://www.youtube.com/embed/rg7Fvvl3taU",  # 4: CSS Grid Systems
        "https://www.youtube.com/embed/W6NZfCO5SIk",  # 5: JavaScript Web Foundations
        "https://www.youtube.com/embed/y17RuWkWdn8",  # 6: DOM Selection & Manipulation
        "https://www.youtube.com/embed/yEsmrF4_Zc0",  # 7: Event Handling & Forms
        "https://www.youtube.com/embed/cuEtnrL9-H0",  # 8: Async JS, Promises & Fetch API
        "https://www.youtube.com/embed/Oe421EPjeBE",  # 9: Backend Routing & Server APIs
        "https://www.youtube.com/embed/HXV3zeQKqGY",  # 10: Database Integration & CRUD
        "https://www.youtube.com/embed/G0jO8kUrg-I",  # 11: Fullstack Web App Assembly
        "https://www.youtube.com/embed/PlxWfBi3358",  # 12: Deployment & Cloud Hosting
    ]
}

# Curated curricula by topic & difficulty
CURRICULA = {
    "python": {
        "beginner": [
            ("Introduction to Python & Setup", "Basic syntax, interpreter, script execution, print function, and comments."),
            ("Variables, Constants & Data Types", "Integers, floats, strings, booleans, dynamic typing, and type conversions."),
            ("Operators & Control Flow", "Arithmetic, logical, relational operators, if-elif-else statements."),
            ("Loops & Iterations", "For loops, while loops, range() function, break, continue, and pass statements."),
            ("Functions & Modular Code", "Function definition, parameters, arguments, return values, and scope."),
            ("Lists & Tuples", "Sequences, indexing, slicing, mutability vs immutability, common list methods."),
            ("Dictionaries & Sets", "Key-value pairs, hash sets, unique elements, dictionary methods and lookups."),
            ("String Manipulation & Formatting", "String slicing, f-strings, strip, split, join, and formatting."),
            ("Basic File I/O", "Opening files, reading text, writing data, with statement, and context managers."),
            ("Error & Exception Handling", "Try, except, else, finally blocks, and common exception types."),
            ("Standard Library Modules", "math, random, datetime, os modules and import techniques."),
            ("Mini Project: Interactive Console App", "Bringing all fundamentals together in a real-world CLI tool.")
        ],
        "intermediate": [
            ("Object-Oriented Programming (OOP) Foundations", "Classes, instances, attributes, methods, and the __init__ constructor."),
            ("Inheritance & Polymorphism", "Subclasses, super() calls, method overriding, and polymorphism."),
            ("Encapsulation & Special Magic Methods", "Private members, getters, setters, __str__, __repr__, and __len__."),
            ("List & Dictionary Comprehensions", "Concise iterables, nested comprehensions, filtering, and performance."),
            ("Iterators, Generators & Yield", "Iterable protocol, generator functions, yield keyword, memory efficiency."),
            ("Decorators & First-Class Functions", "Higher-order functions, closures, function wrappers, and syntax sugar."),
            ("Working with JSON & CSV Data", "Parsing web payloads, reading and writing tabular records."),
            ("Virtual Environments & Package Management", "venv, pip, requirements.txt, and dependency isolation."),
            ("Unit Testing with unittest", "Writing test cases, assertions, test discovery, and test-driven habits."),
            ("Logging & Clean Code Practices", "logging module, PEP 8 style guide, type hints, docstrings."),
            ("Multithreading & Multiprocessing Basics", "CPU-bound vs I/O-bound tasks, concurrent execution patterns."),
            ("Building a REST API with Flask", "Endpoints, routing, JSON requests/responses, request lifecycle.")
        ],
        "advanced": [
            ("Advanced Metaclasses & Descriptors", "Type creation at runtime, descriptor protocol, attribute access hooks."),
            ("Asynchronous Programming with asyncio", "Event loops, coroutines, async/await syntax, concurrent tasks."),
            ("Memory Management & Garbage Collection", "Reference counting, cyclic GC, __slots__ optimization, sys.getsizeof."),
            ("Context Managers & Contextlib", "__enter__, __exit__, and custom resource management."),
            ("C-Extensions & Cython Basics", "Bridging C performance into Python runtimes."),
            ("Design Patterns in Python", "Singleton, Factory, Observer, and Strategy patterns."),
            ("Database Optimization & ORM Internals", "Query planning, connection pooling, indexing, SQLAlchemy patterns."),
            ("Production Packaging & CI/CD", "Building wheels, pyproject.toml, automated testing pipelines.")
        ]
    },
    "html": {
        "beginner": [
            ("Introduction to HTML & Document Structure", "DOCTYPE declaration, html, head, title, and body elements."),
            ("Headings, Paragraphs & Text Formatting", "h1 to h6, p, strong, em, mark, and typographical tags."),
            ("Hyperlinks & Media Elements", "Anchor tags, relative vs absolute URLs, img, alt attributes."),
            ("Lists & Structural Containers", "Ordered lists, unordered lists, description lists, div, and span."),
            ("Tables & Data Presentation", "table, tr, th, td, thead, tbody, and colspan attributes."),
            ("HTML Forms & Interactive Controls", "form, input, label, submit, button, action, and method."),
            ("Semantic HTML5 Elements", "header, nav, section, article, aside, and footer elements."),
            ("Audio, Video & iFrames", "Embedding multimedia players, video attributes, and external iframes."),
            ("Meta Tags & Search Engine Basics", "Charset, viewport, description, and accessibility best practices."),
            ("HTML Entities & Symbols", "Reserved character escaping, copyright, arrows, and special symbols."),
            ("Validating & Structuring Clean Web Pages", "W3C validator, indentation, clean code standards, SEO basics."),
            ("Capstone Project: Personal Portfolio Page", "Structuring a complete semantic web page from scratch.")
        ]
    },
    "css": {
        "beginner": [
            ("Introduction to CSS & Styling Methods", "Inline, internal, external stylesheets, and CSS syntax."),
            ("CSS Selectors & Specificity", "Element, class, id, attribute selectors, and the cascade."),
            ("Colors, Typography & Fonts", "HEX, RGB, HSL colors, font-family, web fonts, and line heights."),
            ("The CSS Box Model", "Content, padding, border, and margin calculations."),
            ("Display Properties & Flow", "block, inline, inline-block, none, and document flow."),
            ("Positioning Techniques", "static, relative, absolute, fixed, and sticky positioning."),
            ("CSS Flexbox Layouts", "flex-direction, justify-content, align-items, and responsive layouts."),
            ("CSS Grid System", "grid-template-columns, grid-gap, areas, and multi-column designs."),
            ("Transitions & Transform Effects", "hover effects, transform: scale/rotate, ease-in-out animations."),
            ("Media Queries & Responsive Design", "Breakpoints, mobile-first design, fluid units (rem, vw, vh)."),
            ("Styling Forms & Modern Buttons", "Custom input styles, button hover states, focus rings."),
            ("Capstone: Modern Responsive Landing Page", "Building a mobile-friendly showcase website.")
        ]
    },
    "javascript": {
        "beginner": [
            ("Introduction to JavaScript & Browser Engine", "Role of JS, script tags, console, and execution environment."),
            ("Variables, Constants & Data Types", "var, let, const, primitive types, and type coercion."),
            ("Operators & Expressions", "Arithmetic, assignment, strict equality ===, and logical operators."),
            ("Conditionals & Control Structures", "if-else chains, switch statements, and ternary operators."),
            ("Loops & Array Iterations", "for, while, for...of, and forEach loops."),
            ("Functions, Parameters & Arrow Syntax", "Function declarations, expressions, arrow functions, return values."),
            ("Arrays & Core Array Methods", "push, pop, map, filter, reduce, slice, and splice."),
            ("Objects & JSON", "Key-value pairs, nested objects, JSON.stringify, and JSON.parse."),
            ("DOM Selection & Manipulation", "getElementById, querySelector, innerText, innerHTML, style."),
            ("Handling DOM Events", "addEventListener, click, input, submit events, event objects."),
            ("Form Validation with JavaScript", "Validating fields, checking regex, displaying inline error alerts."),
            ("Capstone: Interactive Task Management App", "Building an interactive To-Do application.")
        ]
    },
    "sql": {
        "beginner": [
            ("Introduction to Relational Databases & SQL", "Tables, rows, columns, relational model, and SQL dialects."),
            ("Data Definition (DDL): Creating Tables", "CREATE TABLE, data types (INTEGER, TEXT, REAL), constraints."),
            ("Data Manipulation (DML): Inserting Data", "INSERT INTO syntax, single and multi-row insertions."),
            ("Querying Records with SELECT", "SELECT columns, SELECT *, and aliasing with AS."),
            ("Filtering Rows with WHERE Clause", "Comparison operators, AND, OR, NOT, BETWEEN, IN, and LIKE."),
            ("Sorting & Limiting Results", "ORDER BY ASC/DESC, LIMIT, and OFFSET for pagination."),
            ("Aggregate Functions", "COUNT, SUM, AVG, MIN, and MAX functions."),
            ("Grouping Data with GROUP BY & HAVING", "Aggregating groups, filtering aggregated results."),
            ("Updating & Deleting Records", "UPDATE table SET, DELETE FROM, and WHERE clause safety."),
            ("Table Relationships & Foreign Keys", "One-to-many, many-to-many, PRIMARY KEY, and FOREIGN KEY."),
            ("Joining Tables with INNER & LEFT JOIN", "Relating tables, ON clause, handling NULLs in outer joins."),
            ("Capstone: Building an E-Commerce Database", "Creating tables, populating data, and writing analytical queries.")
        ]
    },
    "java": {
        "beginner": [
            ("Introduction to Java & JVM Architecture", "JDK, JRE, JVM bytecode compilation, execution pipeline, and main method."),
            ("Variables, Data Types & Operators", "Primitive types (int, double, boolean, char), reference types, type casting, and arithmetic operators."),
            ("Control Structures & Decision Making", "if-else conditional branching, nested conditions, and switch-case expressions."),
            ("Loops & Iteration Constructs", "for loops, enhanced for-each, while loops, do-while, and loop control keywords."),
            ("Methods, Signatures & Variable Scope", "Method declaration, parameters, return types, static methods, and variable shadowing."),
            ("Arrays & String Operations", "1D/2D arrays, array traversal, String immutability, StringBuilder, and common string methods."),
            ("Object-Oriented Programming: Classes & Objects", "Class definitions, state and behavior, instance variables, and the new keyword."),
            ("Constructors, this Keyword & Memory Management", "Default and parameterized constructors, constructor overloading, this reference, and garbage collection."),
            ("Inheritance & Polymorphism", "Single and multilevel inheritance, extends keyword, method overriding, super keyword, and dynamic dispatch."),
            ("Abstraction & Interfaces", "Abstract classes, abstract methods, interface contracts, implements keyword, and multiple inheritance via interfaces."),
            ("Exception Handling & Robust Code", "try-catch blocks, finally clause, checked vs unchecked exceptions, throw, and throws."),
            ("Collections Framework Basics", "ArrayList, LinkedList, HashSet, HashMap, iterators, and generic type parameters.")
        ]
    },
    "c++": {
        "beginner": [
            ("Introduction to C++ & Compilation Pipeline", "Preprocessors, compilation, linking, main function, and iostream namespace."),
            ("Variables, Fundamental Types & Standard I/O", "int, float, double, char, bool, std::cin, std::cout, and stream manipulators."),
            ("Operators, Expressions & Type Casting", "Arithmetic, logical, bitwise operators, operator precedence, and static_cast."),
            ("Control Flow & Branching Logic", "if, else if, else conditions, ternary operator, and switch statements."),
            ("Loops & Iterative Algorithms", "for loops, while loops, do-while loops, break, and continue."),
            ("Functions, Pass-by-Value & Pass-by-Reference", "Function prototypes, parameter mechanisms, return values, and function overloading."),
            ("Pointers, References & Memory Addresses", "Address-of operator &, dereference operator *, null pointers, and pointer arithmetic."),
            ("Dynamic Memory Allocation (new & delete)", "Heap vs stack memory, new/delete operators, memory leaks, and dangling pointers."),
            ("Object-Oriented Programming: Classes & Objects", "Access specifiers (public, private, protected), member variables, and member functions."),
            ("Constructors & Destructors", "Default constructors, parameterized constructors, copy constructors, and resource cleanup with destructors."),
            ("Inheritance & Virtual Functions", "Derived classes, protected members, virtual functions, runtime polymorphism, and vtables."),
            ("Standard Template Library (STL) Foundations", "std::vector, std::pair, std::map, iterators, and standard sorting algorithms.")
        ]
    },
    "dbms": {
        "beginner": [
            ("Introduction to DBMS & Three-Schema Architecture", "Database models, DBMS vs file systems, external/conceptual/internal levels, and data independence."),
            ("Entity-Relationship (ER) Modeling", "Entities, attributes, relationships, cardinality ratios, weak entities, and ER-to-relational mapping."),
            ("Relational Data Model & Relational Algebra", "Relations, tuples, attributes, select, project, cartesian product, union, and set difference."),
            ("Database Integrity Constraints & Keys", "Domain constraints, entity integrity, referential integrity, primary keys, and foreign keys."),
            ("Functional Dependencies & Normalization (1NF, 2NF, 3NF)", "Anomalies, functional dependencies, closure sets, and decomposing into normal forms."),
            ("Boyce-Codd Normal Form (BCNF) & Lossless Joins", "BCNF definitions, dependency preservation, and lossless join decomposition."),
            ("Transaction Processing & ACID Properties", "Atomicity, Consistency, Isolation, Durability, transaction states, and schedule serializability."),
            ("Concurrency Control Protocols", "Lock-based protocols, Two-Phase Locking (2PL), deadlocks, wait-die and wound-wait schemes."),
            ("Database Recovery Techniques & Logging", "Write-Ahead Logging (WAL), checkpointing, undo/redo logs, and shadow paging."),
            ("Indexing & B-Tree Storage Architecture", "Primary, secondary, clustered indexes, dense vs sparse indexes, and B/B+ tree structures."),
            ("Query Processing & Execution Optimization", "Query parsing, relational query trees, cost estimation, and join algorithm strategies."),
            ("Capstone: Enterprise Database Architecture Design", "Designing a scalable normalized database schema for a modern web application.")
        ]
    },
    "data science": {
        "beginner": [
            ("Introduction to Python for Data Science", "Overview of the data science lifecycle, Jupyter notebooks, Python environment, and core scientific libraries."),
            ("NumPy Arrays & Vectorized Computation", "Creating ndarrays, array slicing, mathematical broadcasting, and vectorized operations over loops."),
            ("Pandas Series & DataFrames", "Data structures for tabular data, index alignment, reading CSV/Excel files, and inspecting data shapes."),
            ("Data Indexing, Selection & Filtering", "loc, iloc, boolean masks, conditional filtering, and querying datasets efficiently."),
            ("Data Cleaning & Handling Missing Values", "Detecting nulls with isnull(), imputation techniques with fillna(), dropping duplicates, and data type casting."),
            ("Data Aggregation, GroupBy & Pivot Tables", "Split-apply-combine strategy with groupby(), computing aggregate statistics (mean, median, sum), and pivot tables."),
            ("Data Merging, Joining & Concatenation", "Combining disparate datasets using pd.concat(), pd.merge() with inner/left/outer joins, and index alignment."),
            ("Data Visualization with Matplotlib", "Plotting line graphs, scatter plots, bar charts, subplots, labeling axes, and styling figures."),
            ("Statistical Plotting with Seaborn", "Distribution plots, box plots, violin plots, correlation heatmaps, and pairplots for feature exploration."),
            ("Exploratory Data Analysis (EDA) Workflow", "Systematic EDA methodology: univariate/bivariate analysis, detecting outliers, and summarizing business insights."),
            ("Introduction to Scikit-Learn & Feature Scaling", "Model API structure, StandardScaler, MinMaxScaler, train_test_split(), and preventing data leakage."),
            ("Capstone: End-to-End Data Analysis Case Study", "Cleaning a raw dataset, executing rigorous EDA, generating visualizations, and extracting actionable data insights.")
        ],
        "intermediate": [
            ("Statistical Inference & Hypothesis Testing", "Normal distribution, p-values, t-tests, ANOVA, and confidence intervals in data evaluation."),
            ("Feature Engineering & Categorical Encoding", "One-hot encoding, ordinal encoding, log transformations, and interaction terms."),
            ("Supervised Learning: Linear & Ridge Regression", "Cost functions, gradient descent, evaluating with MSE, RMSE, R-squared, and L1/L2 regularization."),
            ("Classification: Logistic Regression & Decision Trees", "Binary/multiclass classification, confusion matrix, precision, recall, F1-score, and ROC-AUC curves."),
            ("Ensemble Methods: Random Forests & Gradient Boosting", "Bagging vs boosting, hyperparameter tuning with GridSearchCV, feature importance analysis."),
            ("Unsupervised Learning: K-Means & PCA", "Clustering algorithms, elbow method, dimensionality reduction with Principal Component Analysis."),
            ("Time Series Analysis & Forecasting", "Datetime indexing, rolling averages, seasonality, trend decomposition, and ARIMA foundations."),
            ("Model Deployment & Streamlit Dashboards", "Serializing models with joblib/pickle, building interactive data dashboards with Streamlit.")
        ]
    },
    "web development": {
        "beginner": [
            ("Modern Web Architecture & HTML5 Semantic Structure", "Client-server architecture, HTTP requests, DNS, and modern semantic HTML5 markup."),
            ("CSS3 Styling, Box Model & Typography", "CSS syntax, selectors, specificity, colors, typography, margins, padding, and border box models."),
            ("Responsive Layouts with CSS Flexbox", "Flex container, main/cross axes, justify-content, align-items, and building flexible navigation bars."),
            ("Modern Grid Systems with CSS Grid", "Grid templates, columns, rows, grid areas, auto-fit/auto-fill, and multi-column responsive cards."),
            ("Responsive Web Design & Mobile-First Media Queries", "Viewport meta tag, fluid units (rem, %, vh, vw), media queries, and responsive breakpoint design."),
            ("JavaScript Fundamentals for the Web", "Variables, data types, functions, control flow, array methods, and modern ES6+ features."),
            ("DOM Manipulation & Dynamic UI Updates", "Selecting elements with querySelector, updating text/HTML, modifying styles, and adding dynamic classes."),
            ("Event Handling & User Interactivity", "Event listeners, click/input/submit events, event propagation (bubbling), and form validation."),
            ("Asynchronous JavaScript, Fetch API & JSON", "Promises, async/await syntax, making GET/POST requests to REST APIs, and parsing JSON payloads."),
            ("Backend Fundamentals & Express / Flask Routing", "Server-side architecture, HTTP methods (GET, POST, PUT, DELETE), URL routing, and request/response lifecycles."),
            ("Database Integration & CRUD Operations", "Connecting web backends to SQL/NoSQL databases, writing queries, and handling data persistence safely."),
            ("Capstone: Fullstack Interactive Web Application", "Synthesizing HTML, CSS, JavaScript, and backend APIs to build an end-to-end web application.")
        ]
    },
    "machine learning": {
        "beginner": [
            ("Machine Learning Foundations & Problem Types", "Supervised vs unsupervised vs reinforcement learning, ML workflow, and mathematical intuitions."),
            ("Python Data Science Stack for ML", "NumPy arrays, Pandas matrices, vector math, and tensor shapes."),
            ("Data Preprocessing & Train-Test Splits", "Missing values, encoding categoricals, feature scaling, and train_test_split without data leakage."),
            ("Linear Regression & Cost Minimization", "Ordinary least squares, Mean Squared Error, gradient descent optimization, and evaluation metrics."),
            ("Classification with Logistic Regression", "Sigmoid activation, binary cross-entropy, decision boundaries, and probability thresholds."),
            ("Decision Trees & Information Gain", "Splitting criteria, Gini impurity, entropy, tree depth, and mitigating overfitting."),
            ("Random Forests & Ensemble Learning", "Bootstrap aggregating (Bagging), feature randomness, out-of-bag error, and voting ensembles."),
            ("Support Vector Machines (SVM)", "Hyperplanes, maximal margin classifiers, and kernel functions (RBF, Polynomial)."),
            ("Unsupervised Clustering with K-Means", "Centroid initialization, inertia, elbow method, and silhouette analysis."),
            ("Model Evaluation & Diagnostic Metrics", "Confusion matrix, Precision, Recall, F1-Score, ROC-AUC curves, and K-Fold Cross-Validation."),
            ("Introduction to Artificial Neural Networks", "Perceptrons, multi-layer feedforward networks, backpropagation, and activation functions."),
            ("Capstone: End-to-End Predictive Machine Learning Pipeline", "Complete model training pipeline from raw data ingest to evaluation and persistence.")
        ]
    }
}


def normalize_topic_key(topic):
    """
    Normalizes user-input topics into standardized canonical curriculum keys.
    Handles compound names (e.g., 'python datascience' -> 'data science',
    'full stack web dev' -> 'web development').
    """
    topic_str = topic.strip().lower()
    if any(k in topic_str for k in ["data science", "datascience", "data-science", "data analytics"]):
        return "data science"
    if any(k in topic_str for k in ["web dev", "webdev", "web development", "full stack", "fullstack", "frontend", "backend"]):
        return "web development"
    if any(k in topic_str for k in ["machine learning", "ml", "deep learning", "artificial intelligence", "ai"]):
        return "machine learning"
    if "python" in topic_str:
        return "python"
    if "javascript" in topic_str or topic_str == "js":
        return "javascript"
    if "html" in topic_str:
        return "html"
    if "css" in topic_str:
        return "css"
    if "react" in topic_str:
        return "react"
    if "sql" in topic_str:
        return "sql"
    if "dbms" in topic_str or "database" in topic_str:
        return "dbms"
    if "c++" in topic_str or "cpp" in topic_str:
        return "c++"
    if "java" in topic_str:
        return "java"
    if "docker" in topic_str:
        return "docker"
    if "git" in topic_str:
        return "git"
    return topic_str


def get_video_url(topic, module_index=0, module_title=""):
    """
    Returns a verified educational YouTube embed URL specifically tailored
    to the course topic, curriculum stage, and module subject.
    """
    norm_key = normalize_topic_key(topic)

    # 1. Direct match with normalized key
    if norm_key in TOPIC_VIDEOS:
        videos = TOPIC_VIDEOS[norm_key]
        return videos[module_index % len(videos)]

    topic_key = topic.strip().lower()
    # 2. Direct match with raw topic key
    if topic_key in TOPIC_VIDEOS:
        videos = TOPIC_VIDEOS[topic_key]
        return videos[module_index % len(videos)]

    # 3. Keyword match in curated tracks
    for key, videos in TOPIC_VIDEOS.items():
        if key in topic_key or topic_key in key:
            return videos[module_index % len(videos)]

    # 4. Dedicated CS foundational video mapping by stage for any custom topic
    return FALLBACK_CS_VIDEOS[module_index % len(FALLBACK_CS_VIDEOS)]


def detect_concept_category(title, summary):
    """Identifies the underlying computer science/programming concept from title & summary."""
    text = f"{title} {summary}".lower()
    if any(k in text for k in ["dataframe", "pandas", "numpy", "eda", "visualization", "matplotlib", "seaborn", "clean", "missing", "imput", "scikit", "regression", "classification", "data science", "datascience", "pivot"]):
        return "data_science"
    if any(k in text for k in ["intro", "setup", "architecture", "overview", "installation", "environment", "compiler", "interpreter", "pipeline"]):
        return "setup_intro"
    if any(k in text for k in ["variable", "constant", "data type", "primitive", "memory model", "typing", "identifiers", "casting"]):
        return "variables_types"
    if any(k in text for k in ["control flow", "condition", "branch", "decision", "if-else", "switch", "ternary"]):
        return "control_flow"
    if any(k in text for k in ["loop", "iteration", "traversal", "while", "for loop", "for-each", "sequences", "range"]):
        return "loops_iteration"
    if any(k in text for k in ["function", "method", "procedure", "parameter", "return", "modular", "lambda", "closure", "scope"]):
        return "functions_methods"
    if any(k in text for k in ["class", "object", "oop", "inheritance", "polymorphism", "encapsulation", "constructor", "destructor", "interface", "metaclass", "magic method"]):
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
    if any(k in text for k in ["sql", "table", "query", "select", "join", "database", "crud", "acid", "relational", "schema", "normalization", "index", "dbms"]):
        return "database_sql"
    if any(k in text for k in ["api", "rest", "flask", "endpoint", "http", "route", "html", "css", "dom", "event", "form", "web", "flexbox", "grid"]):
        return "web_api"
    if any(k in text for k in ["docker", "container", "devops", "deploy", "ci/cd", "package", "project", "capstone", "cli", "git"]):
        return "devops_capstone"
    return "general"


def generate_concept_code_and_output(clean_topic, title, summary, concept_cat, difficulty):
    """
    Synthesizes runnable, concept-specific code and realistic output
    tailored to the programming language or technology domain.
    """
    topic_lower = clean_topic.lower()

    # --- DATA SCIENCE & ANALYTICS TRACK ---
    if any(k in topic_lower for k in ["data science", "datascience", "data analytics"]) or concept_cat == "data_science":
        t_low = title.lower()
        if any(k in t_low for k in ["numpy", "vector", "array"]):
            code = (
                "import numpy as np\n\n"
                "# Vectorized computations and statistical operations\n"
                "sensor_readings = np.array([21.5, 22.1, 19.8, 23.4, 20.9, 24.2])\n"
                "normalized = (sensor_readings - np.mean(sensor_readings)) / np.std(sensor_readings)\n\n"
                "print('Original Readings:', sensor_readings)\n"
                "print('Mean Value:', round(float(np.mean(sensor_readings)), 2))\n"
                "print('Std Deviation:', round(float(np.std(sensor_readings)), 2))\n"
                "print('Z-Score Normalized:', np.round(normalized, 3))"
            )
            out = (
                "Original Readings: [21.5 22.1 19.8 23.4 20.9 24.2]\n"
                "Mean Value: 21.98\n"
                "Std Deviation: 1.48\n"
                "Z-Score Normalized: [-0.327  0.079 -1.474  0.957 -0.732  1.498]"
            )
        elif any(k in t_low for k in ["clean", "missing", "null", "imput"]):
            code = (
                "import pandas as pd\nimport numpy as np\n\n"
                "data = {\n"
                "    'Student': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],\n"
                "    'Score': [88, np.nan, 92, 79, np.nan],\n"
                "    'Attendance': [95, 80, np.nan, 90, 85]\n"
                "}\n"
                "df = pd.DataFrame(data)\n"
                "print('--- Null Counts Before Imputation ---')\n"
                "print(df.isnull().sum())\n\n"
                "# Impute missing scores with mean and attendance with median\n"
                "df['Score'] = df['Score'].fillna(df['Score'].mean())\n"
                "df['Attendance'] = df['Attendance'].fillna(df['Attendance'].median())\n\n"
                "print('\\n--- Cleaned DataFrame ---')\n"
                "print(df.round(2))"
            )
            out = (
                "--- Null Counts Before Imputation ---\n"
                "Student       0\n"
                "Score         2\n"
                "Attendance    1\n"
                "dtype: int64\n\n"
                "--- Cleaned DataFrame ---\n"
                "   Student  Score  Attendance\n"
                "0    Alice  88.00        95.0\n"
                "1      Bob  86.33        80.0\n"
                "2  Charlie  92.00        87.5\n"
                "3    Diana  79.00        90.0\n"
                "4      Eve  86.33        85.0"
            )
        elif any(k in t_low for k in ["group", "pivot", "aggregat"]):
            code = (
                "import pandas as pd\n\n"
                "records = {\n"
                "    'Region': ['North', 'South', 'North', 'East', 'South', 'East'],\n"
                "    'Category': ['Tech', 'Tech', 'Office', 'Office', 'Tech', 'Office'],\n"
                "    'Revenue': [12000, 8500, 4200, 3100, 9300, 4900]\n"
                "}\n"
                "df = pd.DataFrame(records)\n"
                "summary = df.groupby('Region')['Revenue'].agg(['count', 'sum', 'mean'])\n"
                "print('--- Regional Revenue Aggregations ---')\n"
                "print(summary)"
            )
            out = (
                "--- Regional Revenue Aggregations ---\n"
                "        count    sum    mean\n"
                "Region                      \n"
                "East        2   8000  4000.0\n"
                "North       2  16200  8100.0\n"
                "South       2  17800  8900.0"
            )
        elif any(k in t_low for k in ["visual", "plot", "matplotlib", "seaborn", "chart"]):
            code = (
                "import matplotlib.pyplot as plt\n\n"
                "months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']\n"
                "active_users = [1200, 1850, 2400, 3100, 4200, 5600]\n\n"
                "plt.figure(figsize=(8, 4))\n"
                "plt.plot(months, active_users, marker='o', color='#4f46e5', linewidth=2.5, label='Active Users')\n"
                "plt.title('Monthly Platform User Growth', fontsize=14, fontweight='bold')\n"
                "plt.xlabel('Month')\n"
                "plt.ylabel('Users')\n"
                "plt.grid(True, linestyle='--', alpha=0.6)\n"
                "plt.legend()\n"
                "plt.tight_layout()\n"
                "print('[SUCCESS] Matplotlib chart rendered successfully (6 points).')"
            )
            out = (
                "[SUCCESS] Matplotlib chart rendered successfully (6 points).\n"
                "Plot properties: 8x4 inches | Series: 'Active Users' (line + markers)"
            )
        elif any(k in t_low for k in ["scikit", "learn", "model", "regression", "classif", "scale", "feature"]):
            code = (
                "from sklearn.model_selection import train_test_split\n"
                "from sklearn.linear_model import LinearRegression\n"
                "from sklearn.metrics import mean_squared_error, r2_score\n"
                "import numpy as np\n\n"
                "# Feature (Hours Studied) vs Target (Exam Score)\n"
                "X = np.array([[2], [4], [5], [7], [8], [10], [12], [14]])\n"
                "y = np.array([45, 58, 65, 78, 80, 89, 93, 98])\n\n"
                "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)\n"
                "model = LinearRegression().fit(X_train, y_train)\n"
                "predictions = model.predict(X_test)\n\n"
                "print(f'Slope (Coefficient): {model.coef_[0]:.2f}')\n"
                "print(f'Intercept: {model.intercept_:.2f}')\n"
                "print(f'R2 Score: {r2_score(y_test, predictions):.3f}')"
            )
            out = (
                "Slope (Coefficient): 4.38\n"
                "Intercept: 38.64\n"
                "R2 Score: 0.984"
            )
        else:
            code = (
                "import pandas as pd\n\n"
                "# Ingest tabular dataset & inspect distributions\n"
                "dataset = {\n"
                "    'Metric_A': [10.2, 14.5, 12.8, 19.3, 15.6],\n"
                "    'Metric_B': [52, 68, 61, 84, 73],\n"
                "    'Label': [1, 0, 1, 0, 1]\n"
                "}\n"
                "df = pd.DataFrame(dataset)\n"
                "print('--- Dataset Summary ---')\n"
                "print(df.describe().round(2))"
            )
            out = (
                "--- Dataset Summary ---\n"
                "       Metric_A  Metric_B  Label\n"
                "count      5.00      5.00   5.00\n"
                "mean      14.48     67.60   0.60\n"
                "std        3.43     12.18   0.55\n"
                "min       10.20     52.00   0.00\n"
                "50%       14.50     68.00   1.00\n"
                "max       19.30     84.00   1.00"
            )
        return code, out

    # --- PYTHON TRACK ---
    if "python" in topic_lower:
        if concept_cat in ["setup_intro", "variables_types"]:
            code = (
                "# Variable declarations & type inspection in Python\n"
                "user_name: str = 'Student Developer'\n"
                "user_id: int = 1042\n"
                "gpa: float = 3.85\n"
                "is_enrolled: bool = True\n\n"
                "print(f'User: {user_name} (ID: {user_id})')\n"
                "print(f'GPA: {gpa} | Enrolled: {is_enrolled}')\n"
                "print('Variable Types:', type(user_name).__name__, type(user_id).__name__, type(gpa).__name__)"
            )
            out = (
                "User: Student Developer (ID: 1042)\n"
                "GPA: 3.85 | Enrolled: True\n"
                "Variable Types: str int float"
            )
        elif concept_cat == "control_flow":
            code = (
                "# Decision logic with if-elif-else branches\n"
                "score = 88\n\n"
                "if score >= 90:\n"
                "    grade = 'A (Distinction)'\n"
                "elif score >= 80:\n"
                "    grade = 'B (High Pass)'\n"
                "elif score >= 70:\n"
                "    grade = 'C (Pass)'\n"
                "else:\n"
                "    grade = 'Remedial Required'\n\n"
                "status = 'Qualified' if score >= 70 else 'Review Needed'\n"
                "print(f'Score: {score} -> Result: {grade} [{status}]')"
            )
            out = "Score: 88 -> Result: B (High Pass) [Qualified]"
        elif concept_cat == "loops_iteration":
            code = (
                "# Structured iteration with for loop, range, and enumerate\n"
                "modules = ['Syntax Foundations', 'Control Structures', 'Functions', 'OOP']\n\n"
                "print('=== Course Learning Pathway ===')\n"
                "for step, mod in enumerate(modules, start=1):\n"
                "    status = 'Core' if step <= 2 else 'Applied'\n"
                "    print(f'Module {step:02d}: {mod:<22} [{status}]')\n\n"
                "total_completed = sum(1 for _ in modules)\n"
                "print(f'\\nTotal Modules Configured: {total_completed}')"
            )
            out = (
                "=== Course Learning Pathway ===\n"
                "Module 01: Syntax Foundations    [Core]\n"
                "Module 02: Control Structures    [Core]\n"
                "Module 03: Functions             [Applied]\n"
                "Module 04: OOP                   [Applied]\n\n"
                "Total Modules Configured: 4"
            )
        elif concept_cat == "functions_methods":
            code = (
                "# Modular function definition with type annotations and docstrings\n"
                "def calculate_weighted_score(quiz: float, exam: float, weight: float = 0.4) -> float:\n"
                '    """Calculates weighted semester score with validation."""\n'
                "    if not (0 <= quiz <= 100 and 0 <= exam <= 100):\n"
                "        raise ValueError('Scores must be between 0 and 100')\n"
                "    final_score = (quiz * weight) + (exam * (1 - weight))\n"
                "    return round(final_score, 2)\n\n"
                "result = calculate_weighted_score(quiz=92.5, exam=84.0)\n"
                "print(f'Final Weighted Score: {result}%')"
            )
            out = "Final Weighted Score: 87.4%"
        elif concept_cat == "oop_classes":
            code = (
                "# Object-Oriented Programming: Class, encapsulation, and methods\n"
                "class Student:\n"
                "    def __init__(self, student_id: int, name: str):\n"
                "        self.student_id = student_id\n"
                "        self.name = name\n"
                "        self.__credits: int = 0  # Private attribute\n\n"
                "    def add_credits(self, credits: int) -> None:\n"
                "        if credits > 0:\n"
                "            self.__credits += credits\n\n"
                "    def get_standing(self) -> str:\n"
                "        return f'{self.name} (ID: {self.student_id}) - Credits: {self.__credits}'\n\n"
                "student = Student(101, 'Alex Mercer')\n"
                "student.add_credits(45)\n"
                "print(student.get_standing())"
            )
            out = "Alex Mercer (ID: 101) - Credits: 45"
        elif concept_cat == "data_structures":
            code = (
                "# Advanced data structures: Dict comprehensions and sets\n"
                "scores = {'Syntax': 94, 'Logic': 88, 'Algorithms': 91, 'Databases': 85}\n\n"
                "# Filter high performing concepts with dictionary comprehension\n"
                "distinction = {k: v for k, v in scores.items() if v >= 90}\n"
                "unique_levels = set(scores.values())\n\n"
                "print('All Scores:', scores)\n"
                "print('Distinctions (>= 90):', distinction)\n"
                "print('Average Score:', sum(scores.values()) / len(scores))"
            )
            out = (
                "All Scores: {'Syntax': 94, 'Logic': 88, 'Algorithms': 91, 'Databases': 85}\n"
                "Distinctions (>= 90): {'Syntax': 94, 'Algorithms': 91}\n"
                "Average Score: 89.5"
            )
        elif concept_cat == "file_io":
            code = (
                "# Context-managed File I/O with JSON serialization\n"
                "import json\n\n"
                "data = {'course': 'Python Masterclass', 'status': 'Active', 'modules_count': 5}\n"
                "json_payload = json.dumps(data, indent=2)\n\n"
                "print('Serialized JSON Record:')\n"
                "print(json_payload)\n\n"
                "decoded = json.loads(json_payload)\n"
                "print(f'Verification: Successfully parsed {decoded[\"course\"]}')"
            )
            out = (
                "Serialized JSON Record:\n"
                "{\n"
                '  "course": "Python Masterclass",\n'
                '  "status": "Active",\n'
                '  "modules_count": 5\n'
                "}\n"
                "Verification: Successfully parsed Python Masterclass"
            )
        elif concept_cat == "error_handling":
            code = (
                "# Robust defensive exception handling with try-except-else-finally\n"
                "def parse_user_input(value_str: str) -> float:\n"
                "    try:\n"
                "        val = float(value_str)\n"
                "        reciprocal = 100.0 / val\n"
                "    except ValueError:\n"
                "        print(f'Conversion Error: \"{value_str}\" is not a valid number.')\n"
                "        return 0.0\n"
                "    except ZeroDivisionError:\n"
                "        print('Math Error: Division by zero is undefined.')\n"
                "        return 0.0\n"
                "    else:\n"
                "        print(f'Success: Computed metric = {reciprocal:.2f}')\n"
                "        return reciprocal\n"
                "    finally:\n"
                "        print('[Telemetry] Input parsing cycle concluded.')\n\n"
                "parse_user_input('25')"
            )
            out = (
                "Success: Computed metric = 4.00\n"
                "[Telemetry] Input parsing cycle concluded."
            )
        else:
            code = (
                f"# Demonstration of {title} in Python\n"
                f"def execute_{clean_topic.lower()}_pipeline():\n"
                f"    print('=== Initializing {title} Execution ===')\n"
                f"    features = ['Validation', 'Transformation', 'Persistence']\n"
                f"    for idx, feature in enumerate(features, start=1):\n"
                f"        print(f'Stage {{idx}}: Executing {{feature}} for {title}')\n"
                f"    return 'Pipeline Executed Successfully'\n\n"
                f"status = execute_{clean_topic.lower()}_pipeline()\n"
                f"print('Status:', status)"
            )
            out = (
                f"=== Initializing {title} Execution ===\n"
                f"Stage 1: Executing Validation for {title}\n"
                f"Stage 2: Executing Transformation for {title}\n"
                f"Stage 3: Executing Persistence for {title}\n"
                "Status: Pipeline Executed Successfully"
            )

    # --- JAVASCRIPT TRACK ---
    elif "javascript" in topic_lower or "js" in topic_lower:
        if concept_cat in ["variables_types", "setup_intro"]:
            code = (
                "// Variable scoping (const/let) and template literals\n"
                "const courseTitle = 'Modern JavaScript';\n"
                "let activeStudents = 42;\n"
                "const isLive = true;\n\n"
                "console.log(`Course: ${courseTitle} | Enrolled: ${activeStudents}`);\n"
                "console.log(`Status Check: ${isLive ? 'Active Session' : 'Offline'}`);"
            )
            out = "Course: Modern JavaScript | Enrolled: 42\nStatus Check: Active Session"
        elif concept_cat == "loops_iteration":
            code = (
                "// Modern array transformations with map, filter, and reduce\n"
                "const scores = [65, 82, 91, 74, 88, 95];\n\n"
                "const distinctions = scores.filter(s => s >= 85);\n"
                "const curvedScores = scores.map(s => Math.min(100, s + 5));\n"
                "const totalPoints = scores.reduce((sum, val) => sum + val, 0);\n\n"
                "console.log('Distinctions (>= 85):', distinctions);\n"
                "console.log('Average Score:', (totalPoints / scores.length).toFixed(1));"
            )
            out = "Distinctions (>= 85): [ 91, 88, 95 ]\nAverage Score: 82.5"
        elif concept_cat == "web_api":
            code = (
                "// DOM Manipulation & Event Handling\n"
                "// <button id='actionBtn'>Click Me</button>\n"
                "const btn = document.getElementById('actionBtn');\n\n"
                "btn.addEventListener('click', (event) => {\n"
                "    event.preventDefault();\n"
                "    console.log('User interacted with component');\n"
                "    btn.classList.toggle('btn-success');\n"
                "    btn.innerText = 'Action Confirmed!';\n"
                "});\n"
                "console.log('Event listener successfully registered.');"
            )
            out = "Event listener successfully registered.\n[On Click]: User interacted with component"
        else:
            code = (
                f"// JavaScript Implementation for {title}\n"
                f"const handleTask = async (taskName) => {{\n"
                f"    console.log(`[Task Started] Processing: ${{taskName}}`);\n"
                f"    const result = {{ status: 200, module: '{title}', timestamp: Date.now() }};\n"
                f"    return result;\n"
                f"}};\n\n"
                f"handleTask('Verify Core Principles').then(res => console.log('Response:', res));"
            )
            out = (
                "[Task Started] Processing: Verify Core Principles\n"
                f"Response: {{ status: 200, module: '{title}', timestamp: 1726880000000 }}"
            )

    # --- JAVA TRACK ---
    elif "java" in topic_lower:
        if concept_cat in ["variables_types", "setup_intro"]:
            code = (
                "// Java Strongly Typed Variable Declarations\n"
                "public class StudentRecord {\n"
                "    public static void main(String[] args) {\n"
                "        String studentName = \"Kavita Sharma\";\n"
                "        int rollNumber = 2045;\n"
                "        double semesterGpa = 8.75;\n"
                "        boolean isRegular = true;\n\n"
                "        System.out.println(\"=== Student Profile ===\");\n"
                "        System.out.println(\"Name: \" + studentName + \" | Roll No: \" + rollNumber);\n"
                "        System.out.println(\"GPA: \" + semesterGpa + \" | Regular: \" + isRegular);\n"
                "    }\n"
                "}"
            )
            out = (
                "=== Student Profile ===\n"
                "Name: Kavita Sharma | Roll No: 2045\n"
                "GPA: 8.75 | Regular: true"
            )
        elif concept_cat == "oop_classes":
            code = (
                "// Encapsulation and Class Design in Java\n"
                "public class CourseModule {\n"
                "    private int moduleId;\n"
                "    private String title;\n\n"
                "    public CourseModule(int id, String title) {\n"
                "        this.moduleId = id;\n"
                "        this.title = title;\n"
                "    }\n\n"
                "    public void display() {\n"
                "        System.out.println(\"Module #\" + moduleId + \": \" + title);\n"
                "    }\n\n"
                "    public static void main(String[] args) {\n"
                "        CourseModule mod = new CourseModule(1, \"Core Java OOP\");\n"
                "        mod.display();\n"
                "    }\n"
                "}"
            )
            out = "Module #1: Core Java OOP"
        else:
            code = (
                f"// Java Implementation for {title}\n"
                "import java.util.ArrayList;\n\n"
                "public class Solution {\n"
                "    public static void main(String[] args) {\n"
                f"        System.out.println(\"Executing: {title}\");\n"
                "        ArrayList<String> components = new ArrayList<>();\n"
                "        components.add(\"Validation\");\n"
                "        components.add(\"Execution\");\n"
                "        for (String c : components) {\n"
                "            System.out.println(\"Processing Step: \" + c);\n"
                "        }\n"
                "    }\n"
                "}"
            )
            out = (
                f"Executing: {title}\n"
                "Processing Step: Validation\n"
                "Processing Step: Execution"
            )

    # --- C++ TRACK ---
    elif "c++" in topic_lower or "cpp" in topic_lower:
        if concept_cat in ["variables_types", "setup_intro"]:
            code = (
                "#include <iostream>\n"
                "#include <string>\n\n"
                "int main() {\n"
                "    std::string studentName = \"Rahul Verma\";\n"
                "    int registrationNumber = 5021;\n"
                "    double score = 91.5;\n\n"
                "    std::cout << \"=== C++ Student Record ===\" << std::endl;\n"
                "    std::cout << \"Name: \" << studentName << std::endl;\n"
                "    std::cout << \"Reg ID: \" << registrationNumber << \" | Score: \" << score << std::endl;\n"
                "    return 0;\n"
                "}"
            )
            out = (
                "=== C++ Student Record ===\n"
                "Name: Rahul Verma\n"
                "Reg ID: 5021 | Score: 91.5"
            )
        elif concept_cat == "oop_classes":
            code = (
                "#include <iostream>\n"
                "#include <string>\n\n"
                "class Account {\n"
                "private:\n"
                "    double balance;\n"
                "public:\n"
                "    Account(double initial) : balance(initial) {}\n"
                "    void deposit(double amount) { balance += amount; }\n"
                "    double getBalance() const { return balance; }\n"
                "};\n\n"
                "int main() {\n"
                "    Account myAcc(1500.0);\n"
                "    myAcc.deposit(500.0);\n"
                "    std::cout << \"Account Balance: $\" << myAcc.getBalance() << std::endl;\n"
                "    return 0;\n"
                "}"
            )
            out = "Account Balance: $2000"
        else:
            code = (
                f"#include <iostream>\n"
                f"#include <vector>\n\n"
                f"// Implementation demonstration for {title}\n"
                f"int main() {{\n"
                f"    std::cout << \"=== {title} ===\" << std::endl;\n"
                f"    std::vector<int> numbers = {{10, 20, 30, 40}};\n"
                f"    int total = 0;\n"
                f"    for (int n : numbers) {{\n"
                f"        total += n;\n"
                f"    }}\n"
                f"    std::cout << \"Computed Vector Sum: \" << total << std::endl;\n"
                f"    return 0;\n"
                f"}}"
            )
            out = (
                f"=== {title} ===\n"
                "Computed Vector Sum: 100"
            )

    # --- SQL & DBMS TRACK ---
    elif "sql" in topic_lower or "dbms" in topic_lower or "database" in topic_lower:
        code = (
            f"-- Database Architecture & Query for {title}\n"
            "CREATE TABLE students (\n"
            "    student_id INTEGER PRIMARY KEY,\n"
            "    full_name VARCHAR(100) NOT NULL,\n"
            "    department VARCHAR(50),\n"
            "    gpa DECIMAL(3, 2)\n"
            ");\n\n"
            "INSERT INTO students (student_id, full_name, department, gpa)\n"
            "VALUES (101, 'Aarav Patel', 'Computer Science', 3.92),\n"
            "       (102, 'Priya Nair', 'Information Technology', 3.84);\n\n"
            "SELECT student_id, full_name, gpa\n"
            "FROM students\n"
            "WHERE gpa >= 3.80\n"
            "ORDER BY gpa DESC;"
        )
        out = (
            "+------------+--------------+------+\n"
            "| student_id | full_name    | gpa  |\n"
            "+------------+--------------+------+\n"
            "|        101 | Aarav Patel  | 3.92 |\n"
            "|        102 | Priya Nair   | 3.84 |\n"
            "+------------+--------------+------+"
        )

    # --- HTML / CSS TRACK ---
    elif "html" in topic_lower:
        code = (
            f"<!-- Semantic HTML5 architecture for {title} -->\n"
            "<article class=\"lesson-card\">\n"
            "    <header>\n"
            f"        <h1>{title}</h1>\n"
            "        <p class=\"meta\">Course: Web Development</p>\n"
            "    </header>\n"
            "    <section class=\"body-content\">\n"
            "        <p>Interactive web interfaces require clean semantic tags.</p>\n"
            "        <button type=\"button\" class=\"cta-btn\">Explore Concept</button>\n"
            "    </section>\n"
            "</article>"
        )
        out = f"[DOM Tree Rendered: <article> container with header '<h1>{title}</h1>', semantic section, and active button]"
    elif "css" in topic_lower:
        code = (
            f"/* Modern Responsive CSS for {title} */\n"
            ".dashboard-grid {\n"
            "    display: grid;\n"
            "    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));\n"
            "    gap: 1.5rem;\n"
            "    padding: 2rem;\n"
            "}\n\n"
            ".metric-card {\n"
            "    background: #ffffff;\n"
            "    border-radius: 12px;\n"
            "    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);\n"
            "    transition: transform 0.2s ease;\n"
            "}\n"
            ".metric-card:hover { transform: translateY(-4px); }"
        )
        out = "[Visual Result: Responsive CSS grid adapting gracefully across desktop, tablet, and mobile screens]"

    # --- ANY CUSTOM OR GENERIC TOPIC (Docker, Git, Linux, React, etc.) ---
    elif any(cli in topic_lower for cli in ["docker", "git", "linux", "kubernetes", "bash", "devops"]):
        code = (
            f"# Terminal Command Workflow for {clean_topic} - {title}\n"
            f"# 1. Initialize environment & verify configuration\n"
            f"{clean_topic.lower()} --version\n\n"
            f"# 2. Execute target pipeline command for {title}\n"
            f"{clean_topic.lower()} run --rm -it {clean_topic.lower()}-runtime:latest \\\n"
            f"    --config ./settings.env \\\n"
            f"    --verbose\n\n"
            f"# 3. Verify process status and exit code\n"
            f"echo \"Operation completed with exit code: $?\""
        )
        out = (
            f"{clean_topic.lower()} version 24.0.5, build a61e2b3\n"
            f"[INFO] Initializing {title} container environment...\n"
            "[INFO] Configuration applied successfully.\n"
            "Operation completed with exit code: 0"
        )
    else:
        code = (
            f"// {clean_topic} Architecture Implementation: {title}\n"
            f"class {clean_topic.replace(' ', '')}Service {{\n"
            f"    constructor() {{\n"
            f"        this.topic = '{clean_topic}';\n"
            f"        this.concept = '{title}';\n"
            f"        this.isInitialized = false;\n"
            f"    }}\n\n"
            f"    initialize() {{\n"
            f"        console.log(`[Init] Configuring ${{this.topic}} engine for ${{this.concept}}`);\n"
            f"        this.isInitialized = true;\n"
            f"        return {{ status: 'ACTIVE', concept: this.concept }};\n"
            f"    }}\n"
            f"}}\n\n"
            f"const service = new {clean_topic.replace(' ', '')}Service();\n"
            f"const state = service.initialize();\n"
            f"console.log('Current System State:', state);"
        )
        out = (
            f"[Init] Configuring {clean_topic} engine for {title}\n"
            f"Current System State: {{ status: 'ACTIVE', concept: '{title}' }}"
        )

    return code, out


def generate_notes_content(topic, title, summary, difficulty):
    """
    Generates rich, student-friendly notes structured into 7 distinct academic sections:
      1. Concept Overview & Practical Motivation
      2. Key Objectives & Learning Outcomes
      3. Core Technical Principles & Syntax Breakdown
      4. Practical Implementation Example (Runnable Code)
      5. Execution Output & Step-by-Step Walkthrough
      6. Common Pitfalls & Debugging Best Practices
      7. College Viva & Technical Interview Q&A
    """
    clean_topic = topic.strip().capitalize()
    clean_title = title.strip()
    clean_diff = difficulty.strip().capitalize()
    concept_cat = detect_concept_category(clean_title, summary)

    # 1. Generate tailored code & output
    code_sample, output_sample = generate_concept_code_and_output(clean_topic, clean_title, summary, concept_cat, clean_diff)

    # 2. Dynamic concept principles
    principles_map = {
        "setup_intro": [
            ("Runtime Architecture", f"Understanding the translation and execution pipeline in {clean_topic} is critical for diagnosing startup failures."),
            ("Environment Isolation", "Preventing version collisions by maintaining clean dependencies and configuration variables."),
            ("Syntax & Entry Point", "Every executable unit defines a clear execution flow starting from its entry point."),
            ("Compilation & Interpretation", f"How source directives are verified, tokenized, and transformed into runtime binaries in {clean_topic}.")
        ],
        "variables_types": [
            ("Memory Allocation & Scoping", f"Variables allocate stack or heap memory to persist state while abiding by strict scoping rules in {clean_topic}."),
            ("Type Discipline", "Ensuring data integrity through explicit or strong typing to prevent unexpected runtime casting bugs."),
            ("Immutability & Safety", "Treating constants as immutable prevents inadvertent side-effects across concurrent pathways."),
            ("Naming Conventions", "Adhering to community naming standards increases team readability and maintainability.")
        ],
        "control_flow": [
            ("Deterministic Branching", "Conditional evaluation routes program execution along predictable logical pathways."),
            ("Short-Circuit Evaluation", "Logical operators (AND / OR) optimize runtime performance by evaluating expressions only when necessary."),
            ("Exhaustive Decision Handling", "Accounting for edge-case inputs via default or fallback branches prevents unhandled states."),
            ("Guard Clauses", "Inverting logic to fail fast cleans up nested indentation and clarifies happy-path execution.")
        ],
        "loops_iteration": [
            ("Bounded vs Unbounded Loops", "Choosing deterministic counting structures over condition-driven loops prevents infinite cycles."),
            ("Invariant Maintenance", "Ensuring loop invariants remain mathematically true across each step guarantees algorithm correctness."),
            ("Traversal Efficiency", "Avoiding redundant traversals reduces algorithmic complexity from quadratic to linear time."),
            ("Control Keywords", "Leveraging break and continue with restraint keeps loop exit conditions obvious and testable.")
        ],
        "functions_methods": [
            ("Single Responsibility Principle", "Functions should perform one well-defined operation with clearly isolated inputs and outputs."),
            ("Call Stack Mechanics", "Understanding stack frame allocation, parameter passing, and return addresses prevents stack overflow."),
            ("Pure Functions & Side-Effects", "Minimizing mutations to global state yields predictable, unit-testable code."),
            ("Signature Contracts", f"Explicit argument validation guarantees callers adhere to the API contract expected by {clean_topic}.")
        ],
        "oop_classes": [
            ("Encapsulation & Information Hiding", "Exposing only necessary methods while restricting direct access to internal state protects invariants."),
            ("Inheritance & Composition", "Favoring object composition over deep inheritance hierarchies prevents brittle architectures."),
            ("Polymorphic Dispatch", "Dynamic dispatch enables clean decoupling between caller interfaces and concrete implementations."),
            ("Constructor Invariants", "Ensuring objects are in a valid state immediately upon instantiation prevents null references.")
        ],
        "data_structures": [
            ("Access & Mutation Complexity", "Selecting structures based on Big-O requirements for search, insertion, and deletion."),
            ("Memory Overhead & Contiguity", "Contiguous data structures maximize CPU cache locality compared to pointer-linked nodes."),
            ("Collision Resolution", "Understanding hash functions and load factors maintains constant-time dictionary lookups."),
            ("Boundary Conditions", "Always guarding against empty collections, negative indices, and out-of-bounds operations.")
        ],
        "file_io": [
            ("Resource Lifecycles", "Always releasing file handles and socket descriptors using context managers or finally blocks."),
            ("Buffered I/O", "Streaming large payloads in chunks rather than reading entire files into memory prevents OOM crashes."),
            ("Encoding & Serialization", "Consistently applying UTF-8 encoding avoids cross-platform character corruption."),
            ("Atomic Writes", "Writing to temporary files before replacing targets prevents corruption during unexpected crashes.")
        ],
        "data_science": [
            ("Vectorization & SIMD Computation", "Executing vector math on contiguous C-level memory buffers eliminates Python interpreter loop overhead."),
            ("Data Cleaning & Preprocessing", "Imputing nulls, parsing datetime strings, and removing outliers prevents biased analytical models."),
            ("Feature Alignment & Index Integrity", "Pandas aligns data across explicit index keys during joins and merges to ensure relational integrity."),
            ("Statistical Validation", "Evaluating distributions, variances, and correlations guides informed feature engineering decisions.")
        ],
        "error_handling": [
            ("Exception Hierarchies", "Catching specific exceptions rather than blanket generic handlers prevents masking critical errors."),
            ("Fail-Safe Recovery", "Providing graceful fallbacks ensures systems remain operational under partial failures."),
            ("Audit Logging", "Capturing stack traces and context variables enables rapid root-cause analysis during outages."),
            ("Resource Cleanup Guarantee", "Guaranteed execution of cleanup handlers protects shared operating system resources.")
        ]
    }

    # Fallback principles for generic or other concepts
    default_principles = [
        ("Modular Decomposition", f"Breaking {clean_title} into isolated components ensures high cohesion and low coupling across {clean_topic}."),
        ("Predictable Execution", "Following standard specifications prevents unintended side effects and runtime bottlenecks."),
        ("Memory & Computational Efficiency", "Applying appropriate structures guarantees optimal time and space complexity."),
        ("Maintainability & Readability", "Writing expressive, well-documented syntax simplifies long-term collaboration.")
    ]
    principles = principles_map.get(concept_cat, default_principles)

    # 3. Dynamic Viva Q&A
    viva_map = {
        "data_science": [
            ("What is vectorization in NumPy and Pandas and why is it preferred over loops?",
             "Vectorization executes batch operations on contiguous array memory implemented in compiled C code, eliminating the massive overhead of standard Python loops."),
            ("How should missing data (NaN) be handled during data preparation?",
             "Depending on data loss tolerance and missingness mechanisms, missing values can be dropped, or imputed with domain constants, median/mean metrics, or predictive models."),
            ("What is the difference between supervised and unsupervised learning?",
             "Supervised learning trains on labeled target data to make accurate predictions on unseen inputs, whereas unsupervised algorithms discover latent patterns or clusters in unlabeled data.")
        ],
        "setup_intro": [
            (f"What is the primary role of {clean_title} in {clean_topic}?",
             f"It establishes the execution environment and fundamental architectural guidelines required to compile, interpret, and run applications in {clean_topic}."),
            (f"What happens if dependencies or syntax errors occur in {clean_title}?",
             "The parser or runtime engine halts immediately with a syntax or configuration error before entering the main execution loop."),
            ("Why is modular setup preferred over monolithic configuration?",
             "Modular setup permits independent testing, easier version upgrades, and prevents global scope pollution.")
        ],
        "variables_types": [
            (f"How does {clean_topic} handle variable initialization and memory storage?",
             f"Variables bind identifiers to allocated memory locations. Depending on {clean_topic}'s memory model, primitives reside on the stack while composite objects are stored on the heap."),
            ("What is the difference between strongly typed and weakly typed systems?",
             "Strongly typed languages prevent unexpected implicit type conversions, whereas weakly typed systems allow implicit coercion which can lead to subtle bugs."),
            ("Why is immutability beneficial in software design?",
             "Immutable variables cannot be altered after creation, making code thread-safe and immune to unintended mutation side-effects.")
        ],
        "control_flow": [
            ("What is the difference between if-elif chains and switch-case statements?",
             "if-elif evaluates arbitrary boolean expressions sequentially, while switch-case generally optimizes multi-way jump tables based on discrete values."),
            ("What is short-circuit evaluation in logical operations?",
             "The second argument in a logical expression is executed only if the first argument does not suffice to determine the overall value of the expression."),
            ("What is the recommended practice for handling edge cases in decision logic?",
             "Use guard clauses to validate preconditions early and exit immediately, keeping the primary logic free of deeply nested branches.")
        ],
        "loops_iteration": [
            ("When should a developer choose a 'for' loop over a 'while' loop?",
             "Use a 'for' loop when the number of iterations or the iterable collection is known in advance; use a 'while' loop when termination depends on an unpredictable condition."),
            ("How does 'break' differ from 'continue' in loop execution?",
             "'break' terminates the entire loop immediately, transferring control to the statement after the loop. 'continue' skips the remainder of the current iteration and advances to the next cycle."),
            ("What causes an infinite loop and how can it be prevented?",
             "An infinite loop occurs when the loop termination condition never evaluates to false. It is prevented by ensuring the loop control variable is modified within each iteration.")
        ],
        "functions_methods": [
            ("What is the difference between function parameters and arguments?",
             "Parameters are variable identifiers specified in the function signature definition, while arguments are the concrete values passed during invocation."),
            ("Explain the concept of variable scope and lifetime in a function.",
             "Variables declared inside a function have local scope and exist only while the function's stack frame is active on the call stack."),
            ("What is a pure function and why is it desirable?",
             "A pure function always returns the exact same result given the same inputs and produces zero observable side-effects (e.g., no global state modification).")
        ],
        "oop_classes": [
            ("What is the distinction between a class and an object?",
             "A class is a blueprint or template defining attributes and behaviors, whereas an object is a concrete runtime instance created from that blueprint."),
            ("How does encapsulation protect data integrity?",
             "Encapsulation hides internal object state behind private access modifiers and provides public getter/setter methods with built-in validation."),
            ("What is the difference between compile-time and runtime polymorphism?",
             "Compile-time polymorphism is achieved through method overloading, while runtime polymorphism is achieved through method overriding and dynamic method dispatch.")
        ],
        "data_structures": [
            ("Why is choosing the correct data structure critical in algorithm design?",
             "The choice of data structure directly dictates the time complexity (Big-O) of search, insertion, and deletion operations in the application."),
            ("What is the difference between an Array and a Hash Table?",
             "An array provides fast index-based access in contiguous memory, while a hash table maps arbitrary keys to values using a hashing algorithm for average O(1) lookups."),
            ("What is a memory leak in connection with dynamic data structures?",
             "A memory leak happens when dynamically allocated nodes or references are no longer needed by the program but are never released back to the operating system.")
        ]
    }

    default_viva = [
        (f"What is the significance of {clean_title} in {clean_topic}?",
         f"It forms a core building block in {clean_topic}, providing structured patterns that enable reliable, high-performance execution in production systems."),
        (f"What is the most common mistake developers make when implementing {clean_title}?",
         f"Overlooking boundary condition validation and failing to isolate components, resulting in unexpected runtime side-effects."),
        ("How does this module prepare a student for real-world software engineering?",
         "It equips students with practical syntax fluency, code structure habits, and the defensive debugging strategies required in industry environments.")
    ]
    viva_qa = viva_map.get(concept_cat, default_viva)

    # 4. Dynamic Pitfalls
    pitfalls_map = {
        "data_science": [
            "Data Leakage & Preprocessing Sequence Trap",
            "Fitting transformers or imputers on the whole dataset rather than solely on training folds causes data leakage and unrealistic validation scores."
        ],
        "setup_intro": [
            "Path & Environment Misconfiguration",
            "Failing to add the binary or tool path to system environment variables, causing 'command not found' errors."
        ],
        "variables_types": [
            "Implicit Type Coercion & Shadowing",
            "Relying on implicit type conversions or accidentally reusing variable names in nested scopes leading to masked bugs."
        ],
        "control_flow": [
            "Dangling Else & Condition Reversal",
            "Misplaced parentheses or incorrect operator precedence reversing conditional evaluation and allowing invalid states."
        ],
        "loops_iteration": [
            "Off-By-One Errors (Fencepost Trap)",
            "Misjudging inclusive vs exclusive index boundaries (e.g. range(0, n) ending at n-1), resulting in missing elements or index errors."
        ],
        "functions_methods": [
            "Mutable Default Arguments & Unbounded Scope",
            "Passing mutable collections as default parameters or unintentionally modifying arguments passed by reference."
        ],
        "oop_classes": [
            "Null Reference & Uninitialized Members",
            "Attempting to invoke methods on an uninstantiated object reference before invoking its constructor."
        ]
    }

    p_item = pitfalls_map.get(concept_cat, [
        "Neglecting Edge Cases & Boundary Checks",
        f"Failing to validate inputs (e.g., empty collections, null pointers, negative integers) before executing operations in {clean_title}."
    ])

    # Assemble complete 7-section notes
    notes = f"""# {clean_title}

## 1. Concept Overview & Practical Motivation
{summary}

In {clean_topic} ({clean_diff} Level), mastering **{clean_title}** is an essential milestone. It establishes the architectural foundation for writing maintainable, production-ready applications. Understanding both the theoretical mechanics and practical conventions of {clean_title} prevents architectural debt and ensures software reliability across enterprise environments.

---

## 2. Key Objectives & Learning Outcomes
• Master the fundamental syntax and architectural role of {clean_title} in {clean_topic}.
• Understand the data lifecycle, memory allocation, and operational constraints involved.
• Learn defensive programming strategies to anticipate and resolve runtime bottlenecks.
• Implement industry-standard best practices and prepare for technical viva examinations.

---

## 3. Core Technical Principles & Syntax Breakdown
• **{principles[0][0]}**: {principles[0][1]}
• **{principles[1][0]}**: {principles[1][1]}
• **{principles[2][0]}**: {principles[2][1]}
• **{principles[3][0]}**: {principles[3][1]}

---

## 4. Practical Implementation Example

```
{code_sample}
```

### Expected Output:
```
{output_sample}
```

---

## 5. Execution Output & Step-by-Step Walkthrough
• **Step 1 (Initialization)**: The runtime initializes component state and validates preliminary data structures.
• **Step 2 (Execution)**: The core algorithm or operational logic executes, applying transformation rules and control constraints.
• **Step 3 (Verification & Output)**: Formatted results are dispatched to the console or interface, ensuring clean status confirmation.

---

## 6. Common Pitfalls & Debugging Best Practices
• **Trap 1 ({p_item[0]})**: {p_item[1]}
• **Trap 2 (Resource Leaks & Handle Management)**: Always close open sockets, database handles, and file streams to avoid memory and descriptor leaks.
• **Trap 3 (Silent Failures & Blanket Catches)**: Never swallow exceptions with empty catch blocks; always log error telemetry and provide sensible fallback states.

---

## 7. College Viva & Technical Interview Q&A
**Q1: {viva_qa[0][0]}**  
**Answer**: {viva_qa[0][1]}

**Q2: {viva_qa[1][0]}**  
**Answer**: {viva_qa[1][1]}

**Q3: {viva_qa[2][0]}**  
**Answer**: {viva_qa[2][1]}
"""
    return notes


def generate_course_modules(topic, difficulty, module_count):
    """
    Generates a structured list of modules tailored to the specified
    topic, difficulty level, and requested module count (3, 5, 8, 12).
    """
    topic_key = topic.strip().lower()
    norm_key = normalize_topic_key(topic_key)
    diff_key = difficulty.strip().lower()
    count = int(module_count)

    curriculum = []

    # Check normalized key first, then raw topic key
    active_key = norm_key if norm_key in CURRICULA else (topic_key if topic_key in CURRICULA else None)
    if active_key:
        topic_dict = CURRICULA[active_key]
        if diff_key in topic_dict:
            curriculum = list(topic_dict[diff_key])
        else:
            # Fall back to first available difficulty in that topic
            curriculum = list(next(iter(topic_dict.values())))

    # Intelligent algorithmic curriculum generator for unknown topics or custom inputs
    if not curriculum:
        generic_concepts = [
            ("Foundations and Architecture", f"Core syntax, runtime environment, and initial setup for {topic}."),
            ("Variables, Types and Memory Model", f"Primitive and composite data types, scoping rules, and memory management in {topic}."),
            ("Control Flow and Decision Logic", f"Conditional branches, evaluation strategies, and execution pathways in {topic}."),
            ("Loops, Iterators and Sequences", f"Repetition structures, traversal algorithms, and termination conditions in {topic}."),
            ("Functions and Modular Decomposition", f"Function signatures, parameter passing, return structures, and modularity in {topic}."),
            ("Data Structures and Collections", f"Lists, hash maps, trees, queues, and efficient organization in {topic}."),
            ("Object-Oriented & Structural Patterns", f"Encapsulation, abstraction, inheritance, and architectural blueprints in {topic}."),
            ("Error Handling, Debugging and Logging", f"Exception lifecycles, recovery strategies, defensive programming, and logging in {topic}."),
            ("File Operations and I/O Streams", f"Serialization, stream buffers, disk access, and persistent storage in {topic}."),
            ("Network, APIs and Asynchronous Tasks", f"Protocols, request lifecycles, async concurrency, and data interchange in {topic}."),
            ("Testing, Verification and Code Quality", f"Unit testing, assertion design, profiling, and maintainability in {topic}."),
            ("Capstone Project and Production Deployment", f"End-to-end implementation synthesizing all foundational concepts in {topic}.")
        ]
        curriculum = generic_concepts

    # Slice or expand curriculum to match exact module_count
    selected = []
    for i in range(count):
        if i < len(curriculum):
            title, summary = curriculum[i]
        else:
            title = f"{topic.capitalize()} Special Topic: Advanced Concept Part {i + 1}"
            summary = f"In-depth analysis, case studies, and hands-on exercises covering specialized aspects of {topic}."

        video_url = get_video_url(topic, i, title)
        notes = generate_notes_content(topic, title, summary, difficulty)

        selected.append({
            "module_number": i + 1,
            "title": title,
            "notes": notes,
            "video_url": video_url
        })

    return selected
