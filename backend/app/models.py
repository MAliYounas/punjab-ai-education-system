from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import relationship
from .database import Base


class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    division = Column(String(120), default="Lahore")
    schools = relationship("School", back_populates="district")


class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    emis_code = Column(String(40), unique=True)
    district_id = Column(Integer, ForeignKey("districts.id"))
    level = Column(String(40), default="High")
    shift = Column(String(20), default="Morning")
    district = relationship("District", back_populates="schools")
    classrooms = relationship("Classroom", back_populates="school")
    users = relationship("User", back_populates="school")


class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    grade = Column(Integer, default=7)
    section = Column(String(8), default="A")
    school_id = Column(Integer, ForeignKey("schools.id"))
    school = relationship("School", back_populates="classrooms")
    students = relationship("User", back_populates="classroom")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(160), nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(32), nullable=False)  # admin, teacher, student, management
    language = Column(String(8), default="en")
    grade = Column(Integer)
    school_id = Column(Integer, ForeignKey("schools.id"))
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    school = relationship("School", back_populates="users")
    classroom = relationship("Classroom", back_populates="students")


class SessionToken(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class CurriculumVersion(Base):
    __tablename__ = "curriculum_versions"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    board = Column(String(120), default="Punjab Curriculum and Textbook Board")
    year = Column(String(20), default="2024")
    status = Column(String(20), default="approved")  # draft, approved, archived
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    books = relationship("Book", back_populates="version")


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("curriculum_versions.id"))
    grade = Column(Integer, nullable=False)
    subject = Column(String(80), nullable=False)
    title = Column(String(240), nullable=False)
    language = Column(String(8), default="en")
    source_file = Column(String(400), default="")
    publisher = Column(String(200), default="PCTB")
    created_at = Column(DateTime, default=datetime.utcnow)
    version = relationship("CurriculumVersion", back_populates="books")
    chapters = relationship("Chapter", back_populates="book", order_by="Chapter.number")


class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    number = Column(Integer, nullable=False)
    title = Column(String(240), nullable=False)
    summary = Column(Text, default="")
    difficulty = Column(String(20), default="medium")
    page_start = Column(Integer, default=1)
    page_end = Column(Integer, default=1)
    expected_level = Column(String(80), default="Grade 7 / Middle")
    book = relationship("Book", back_populates="chapters")
    topics = relationship("Topic", back_populates="chapter", order_by="Topic.order")
    terms = relationship("Term", back_populates="chapter")


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    title = Column(String(240), nullable=False)
    order = Column(Integer, default=1)
    summary = Column(Text, default="")
    chapter = relationship("Chapter", back_populates="topics")
    subtopics = relationship("Subtopic", back_populates="topic", order_by="Subtopic.id")
    slos = relationship("SLO", back_populates="topic")
    concepts = relationship("Concept", back_populates="topic")


class Subtopic(Base):
    __tablename__ = "subtopics"
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    title = Column(String(240), nullable=False)
    content = Column(Text, default="")
    topic = relationship("Topic", back_populates="subtopics")


class SLO(Base):
    __tablename__ = "slos"
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    code = Column(String(40), nullable=False)
    statement = Column(Text, nullable=False)
    bloom_level = Column(String(24), default="Understand")
    topic = relationship("Topic", back_populates="slos")


class Concept(Base):
    __tablename__ = "concepts"
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    name = Column(String(200), nullable=False)
    explanation = Column(Text, default="")
    simple_explanation = Column(Text, default="")
    example = Column(Text, default="")
    difficulty = Column(String(20), default="medium")
    source_ref = Column(String(200), default="")
    source_excerpt = Column(Text, default="")
    topic = relationship("Topic", back_populates="concepts")


class Term(Base):
    __tablename__ = "terms"
    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    term = Column(String(120), nullable=False)
    definition = Column(Text, default="")
    source_ref = Column(String(200), default="")
    chapter = relationship("Chapter", back_populates="terms")


class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    text = Column(Text, nullable=False)
    source_ref = Column(String(200), default="")
    page = Column(Integer, default=1)


class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True)
    title = Column(String(240), nullable=False)
    type = Column(String(40), nullable=False)  # quiz, homework, assignment, exam, worksheet, chapter_test, practice
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    difficulty = Column(String(20), default="medium")
    total_marks = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String(24), default="pending_review")  # draft, pending_review, approved, published
    language = Column(String(8), default="en")
    grounded = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    qtype = Column(String(32), nullable=False)  # mcq, tf, fib, short, long, conceptual
    stem = Column(Text, nullable=False)
    options_json = Column(Text, default="[]")
    correct_answer = Column(Text, default="")
    explanation = Column(Text, default="")
    difficulty = Column(String(20), default="medium")
    bloom = Column(String(24), default="Understand")
    marks = Column(Integer, default=1)
    slo_id = Column(Integer, ForeignKey("slos.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)
    source_ref = Column(String(200), default="")
    source_excerpt = Column(Text, default="")
    assessment = relationship("Assessment", back_populates="questions")


class Attempt(Base):
    __tablename__ = "attempts"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Float, default=0)
    max_score = Column(Float, default=0)
    percent = Column(Float, default=0)
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer = Column(Text, default="")
    is_correct = Column(Boolean, default=False)
    marks_awarded = Column(Float, default=0)
    attempt = relationship("Attempt", back_populates="answers")


class Mastery(Base):
    __tablename__ = "mastery"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    slo_id = Column(Integer, ForeignKey("slos.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)
    score = Column(Float, default=0)
    attempts_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    attempt_id = Column(Integer, ForeignKey("attempts.id"), nullable=True)
    text = Column(Text, default="")
    activities_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class CopilotLog(Base):
    __tablename__ = "copilot_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prompt = Column(Text, default="")
    intent = Column(String(80), default="")
    response_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(80), nullable=False)
    entity = Column(String(80), default="")
    entity_id = Column(String(40), default="")
    details = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Approval(Base):
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True)
    content_type = Column(String(40), default="assessment")
    content_id = Column(Integer, nullable=False)
    status = Column(String(24), default="pending")
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
