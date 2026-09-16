"""Seed verified GATE 2027 CS section metadata.

Run after migrations from the backend directory:
    python scripts/seed_gate_2027.py
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.curriculum import CurriculumStatus, CurriculumVersion, Exam, LearningObjective, Subject, Subtopic, Topic
from app.models.learning import Question, QuestionSource, QuestionType

OFFICIAL_SOURCE_URL = "https://gate2027.iitm.ac.in/static/doc/GATE2027_Syllabus/CS_GATE2027_Syllabus.pdf"
SUBJECTS = [
    ("engineering-mathematics", "Engineering Mathematics"),
    ("digital-logic", "Digital Logic"),
    ("computer-organization", "Computer Organization and Architecture"),
    ("programming-data-structures", "Programming and Data Structures"),
    ("algorithms", "Algorithms"),
    ("theory-of-computation", "Theory of Computation"),
    ("compiler-design", "Compiler Design"),
    ("operating-systems", "Operating System"),
    ("databases", "Databases"),
    ("computer-networks", "Computer Networks"),
]
MVP_CONTENT = {
    "engineering-mathematics": [
        ("engineering-mathematics", "Engineering Mathematics", ["Propositional and First Order Logic", "Sets, Relations and Functions", "Partial Orders and Lattices", "Monoids and Groups", "Graphs", "Combinatorics", "Matrices and Determinants", "System of Linear Equations", "Eigenvalues and Eigenvectors", "LU Decomposition", "Limits, Continuity and Differentiability", "Maxima and Minima", "Mean Value Theorem", "Integration", "Random Variables", "Probability Distributions", "Conditional Probability and Bayes Theorem"]),
    ],
    "digital-logic": [
        ("digital-logic", "Digital Logic", ["Boolean Algebra and Minimization", "Karnaugh Maps", "Tabular Method", "Combinational Circuits", "Sequential Circuits", "Number Representation", "Fixed Point Arithmetic", "Floating Point Arithmetic"]),
    ],
    "computer-organization": [
        ("computer-organization", "Computer Organization and Architecture", ["Instruction Set and Addressing Modes", "Arithmetic and Logic Unit", "Hardwired Control Unit", "Microprogrammed Control Unit", "Memory Interfacing and Hierarchy", "Cache Memory Mapping", "Interrupts and DMA", "Instruction Pipelining", "Pipeline Hazards"]),
    ],
    "programming-data-structures": [
        ("programming-data-structures", "Programming and Data Structures", ["Programming in C", "Recursion", "Arrays", "Stacks", "Queues", "Linked Lists", "Trees", "Binary Search Trees", "Binary Heaps", "Graphs"]),
    ],
    "algorithms": [
        ("algorithms", "Algorithms", ["Searching", "Sorting", "Hashing", "Asymptotic Worst-Case Time and Space Complexity", "Greedy", "Dynamic Programming", "Divide-and-Conquer", "Graph Traversals", "Minimum Spanning Trees", "Shortest Paths"]),
    ],
    "theory-of-computation": [
        ("theory-of-computation", "Theory of Computation", ["Regular Expressions", "Finite Automata", "Context-Free Grammars", "Push-Down Automata", "Regular Languages", "Context-Free Languages", "Pumping Lemma", "Turing Machines", "Undecidability"]),
    ],
    "compiler-design": [
        ("compiler-design", "Compiler Design", ["Lexical Analysis", "Parsing", "Syntax-Directed Translation", "Runtime Environments", "Intermediate Code Generation", "Local Optimisation", "Data Flow Analyses", "Constant Propagation", "Liveness Analysis", "Common Subexpression Elimination"]),
    ],
    "operating-systems": [
        ("operating-systems", "Operating System", ["System Calls", "Processes", "Threads", "Inter-Process Communication", "Concurrency and Synchronization", "Deadlock", "CPU Scheduling", "I/O Scheduling", "Memory Management", "Virtual Memory", "File Systems"]),
    ],
    "databases": [
        ("databases", "Databases", ["ER Model", "Relational Algebra", "Tuple Calculus", "SQL", "Integrity Constraints", "Normal Forms", "File Organization", "Indexing", "B Trees and B+ Trees", "Transactions", "Concurrency Control"]),
    ],
    "computer-networks": [
        ("computer-networks", "Computer Networks", ["Principles of Layering", "Switching", "Performance Metrics", "Error Detection", "Medium Access Control", "Ethernet", "Distance Vector Routing", "Link State Routing", "IPv4 Fragmentation", "CIDR Notation", "Network Address Translation", "TCP Flow Control", "TCP Congestion Control", "Socket API", "DNS", "HTTP"]),
    ],
}
PRACTICE_QUESTIONS = [
    ("recursion", "What is the base case in a recursive function?", [("A", "The condition that stops further recursive calls"), ("B", "The first recursive call"), ("C", "The largest input"), ("D", "A global variable")], "A", "Recursion", "Identify recursion termination"),
    ("stacks", "Which operation removes the most recently inserted item from a stack?", [("A", "enqueue"), ("B", "dequeue"), ("C", "pop"), ("D", "peek")], "C", "Stack operations", "Apply LIFO behavior"),
    ("binary-search-trees", "In a binary search tree, where are keys smaller than a node stored?", [("A", "Only in the right subtree"), ("B", "In the left subtree"), ("C", "At the root only"), ("D", "They cannot be stored")], "B", "BST ordering", "Apply BST invariant"),
    ("asymptotic-worst-case-time-and-space-complexity", "What is the worst-case time complexity of linear search on n elements?", [("A", "O(1)"), ("B", "O(log n)"), ("C", "O(n)"), ("D", "O(n log n)")], "C", "Asymptotic complexity", "Analyze worst-case complexity"),
    ("sorting", "Which sorting algorithm repeatedly selects the smallest remaining item?", [("A", "Selection sort"), ("B", "Merge sort"), ("C", "Quick sort"), ("D", "Heap sort")], "A", "Sorting", "Recognize sorting algorithms"),
    ("dynamic-programming", "Dynamic programming is most appropriate when a problem has:", [("A", "Only one possible solution"), ("B", "Overlapping subproblems and optimal substructure"), ("C", "No repeated computation"), ("D", "A sorted input only")], "B", "Dynamic programming", "Identify dynamic-programming conditions"),
]


def code_for(title: str) -> str:
    return "-".join("".join(character.lower() if character.isalnum() else " " for character in title).split())


def seed() -> None:
    with SessionLocal() as database:
        exam = database.scalar(select(Exam).where(Exam.code == "GATE-CS"))
        if exam is None:
            exam = Exam(code="GATE-CS", name="GATE Computer Science and Information Technology")
            database.add(exam)
            database.flush()
        version = database.scalar(select(CurriculumVersion).where(CurriculumVersion.exam_id == exam.id, CurriculumVersion.label == "2027"))
        if version is None:
            version = CurriculumVersion(exam_id=exam.id, label="2027", status=CurriculumStatus.PUBLISHED, official_source_url=OFFICIAL_SOURCE_URL)
            database.add(version)
            database.flush()
        existing_codes = set(database.scalars(select(Subject.code).where(Subject.curriculum_version_id == version.id)))
        database.add_all(Subject(curriculum_version_id=version.id, code=code, title=title, display_order=index) for index, (code, title) in enumerate(SUBJECTS, start=1) if code not in existing_codes)
        database.flush()
        subjects = {subject.code: subject for subject in database.scalars(select(Subject).where(Subject.curriculum_version_id == version.id))}
        for subject_code, topics in MVP_CONTENT.items():
            subject = subjects[subject_code]
            existing_topics = {topic.code: topic for topic in database.scalars(select(Topic).where(Topic.subject_id == subject.id))}
            for topic_order, (topic_code, topic_title, subtopics) in enumerate(topics, start=1):
                topic = existing_topics.get(topic_code)
                if topic is None:
                    topic = Topic(subject_id=subject.id, code=topic_code, title=topic_title, display_order=topic_order)
                    database.add(topic)
                    database.flush()
                existing_subtopics = {subtopic.code: subtopic for subtopic in database.scalars(select(Subtopic).where(Subtopic.topic_id == topic.id))}
                for subtopic_order, subtopic_title in enumerate(subtopics, start=1):
                    subtopic_code = code_for(subtopic_title)
                    subtopic = existing_subtopics.get(subtopic_code)
                    if subtopic is None:
                        subtopic = Subtopic(topic_id=topic.id, code=subtopic_code, title=subtopic_title, display_order=subtopic_order)
                        database.add(subtopic)
                        database.flush()
                    if database.scalar(select(LearningObjective).where(LearningObjective.subtopic_id == subtopic.id, LearningObjective.code == "apply")) is None:
                        database.add(LearningObjective(subtopic_id=subtopic.id, code="apply", statement=f"Explain and apply {subtopic_title} in GATE-style problems.", display_order=1))
        subtopics_by_code = {subtopic.code: subtopic for subtopic in database.scalars(select(Subtopic).join(Topic).join(Subject).where(Subject.curriculum_version_id == version.id))}
        for subtopic_code, prompt, options, correct_answer, concept, skill_tested in PRACTICE_QUESTIONS:
            subtopic = subtopics_by_code[subtopic_code]
            existing_question = database.scalar(select(Question).where(Question.subtopic_id == subtopic.id, Question.prompt == prompt))
            if existing_question is None:
                database.add(Question(subtopic_id=subtopic.id, source=QuestionSource.AI_GENERATED, question_type=QuestionType.MCQ, prompt=prompt, options=[{"label": label, "text": text} for label, text in options], correct_answer=correct_answer, explanation=f"The correct option is {correct_answer}.", concept=concept, skill_tested=skill_tested, difficulty=1, is_diagnostic_eligible=True, is_active=True))
        database.commit()


if __name__ == "__main__":
    seed()
