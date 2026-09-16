# Curriculum Sourcing

The `2027` GATE CS curriculum seed is sourced from the official IIT Madras GATE 2027 CS syllabus PDF. It creates the exam, the curriculum version, and its ten top-level sections. It also adds the explicitly listed Programming and Data Structures and Algorithms subtopics for the MVP.

The learning-objective wording is curated product content, not an official syllabus quote. The seed deliberately does not add prerequisites or previous-year questions. Add production content through a reviewed curriculum-content process that links each item to its source and reviewer.

For local development, the seed also adds six basic questions labelled `AI_GENERATED`. They are neither official nor previous-year questions and must be reviewed or replaced before production use.

Run the seed only after database migrations:

```text
cd backend
python scripts/seed_gate_2027.py
```
