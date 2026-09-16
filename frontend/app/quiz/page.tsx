"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { apiRequest } from "../../lib/api";

type Question = { id: string; question_type: string; prompt: string; options: { label: string; text: string }[] | null };
type Quiz = { attempt_id: string; title: string; questions: Question[] };
type Result = { score_percent: number; correct_count: number; question_count: number; mistakes_created: number; reviews: { prompt: string; submitted_answer: string; correct_answer: string; explanation: string; is_correct: boolean }[] };

function QuizPageContent() {
  const searchParams = useSearchParams(); const selectedSubtopicId = searchParams.get("subtopicId");
  const [quiz, setQuiz] = useState<Quiz | null>(null); const [answers, setAnswers] = useState<Record<string, string>>({}); const [answeredAt, setAnsweredAt] = useState<Record<string, number>>({}); const [startedAt, setStartedAt] = useState(0); const [result, setResult] = useState<Result | null>(null); const [error, setError] = useState("");
  useEffect(() => { const subtopic = selectedSubtopicId ? Promise.resolve(selectedSubtopicId) : apiRequest<{ subtopic_id: string | null }>("/recommendations/next").then((next) => next.subtopic_id); subtopic.then((subtopicId) => { if (!subtopicId) throw new Error("Complete a diagnostic assessment before starting practice."); return apiRequest<Quiz>("/assessment/quizzes", { method: "POST", body: JSON.stringify({ subtopic_ids: [subtopicId], question_count: 1, title: selectedSubtopicId ? "Topic practice" : "Recommended practice" }) }); }).then((response) => { setQuiz(response); setStartedAt(Date.now()); }).catch((reason) => setError(reason instanceof Error ? reason.message : "Unable to start quiz")); }, [selectedSubtopicId]);
  async function submit() { if (!quiz) return; if (Object.keys(answers).length !== quiz.questions.length) { setError("Answer every question before submitting."); return; } try { const response = await apiRequest<Result>(`/assessment/quiz-attempts/${quiz.attempt_id}/submit`, { method: "POST", body: JSON.stringify({ answers: quiz.questions.map((question) => ({ question_id: question.id, answer: answers[question.id], response_time_ms: Math.min(7_200_000, Math.max(1, answeredAt[question.id] - startedAt)) })) }) }); setResult(response); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to submit quiz"); } }
  if (error && !quiz) return <main className="form-page"><h1>Quiz unavailable</h1><p className="error">{error}</p><Link href="/">Back to dashboard</Link></main>;
  if (result) return <main className="form-page"><p className="eyebrow">Practice complete</p><h1>{result.score_percent}%</h1><p>{result.correct_count} of {result.question_count} correct. {result.mistakes_created ? "Your learning plan has been updated for revision." : "Great work—your mastery has been updated."}</p>{result.reviews.map((review, index) => <section className="recommendation" key={index}><p className="eyebrow">{review.is_correct ? "Correct" : "Review this"}</p><h2>{review.prompt}</h2><p>Your answer: {review.submitted_answer}</p>{!review.is_correct && <p>Correct answer: {review.correct_answer}</p>}<p>{review.explanation}</p></section>)}<Link className="button" href="/">Return to dashboard</Link></main>;
  if (!quiz) return <main className="form-page"><p>Preparing your quiz…</p></main>;
  return <main className="form-page"><h1>{quiz.title}</h1>{quiz.questions.map((question, index) => <section className="diagnostic-question" key={question.id}><strong>{question.prompt}</strong>{question.options ? question.options.map((option) => <label key={option.label}><input type="radio" name={question.id} value={option.label} onChange={() => { setAnswers({ ...answers, [question.id]: option.label }); setAnsweredAt({ ...answeredAt, [question.id]: Date.now() }); setError(""); }} /> {option.label}. {option.text}</label>) : <input aria-label={`Answer for question ${index + 1}`} inputMode={question.question_type === "nat" ? "decimal" : "text"} placeholder="Your answer" value={answers[question.id] ?? ""} onChange={(event) => { setAnswers({ ...answers, [question.id]: event.target.value }); setAnsweredAt({ ...answeredAt, [question.id]: Date.now() }); setError(""); }} />}</section>)}<button onClick={submit}>Submit answer</button>{error && <p className="error">{error}</p>}</main>;
}

export default function QuizPage() {
  return <Suspense fallback={<main className="form-page"><p>Preparing your quiz…</p></main>}><QuizPageContent /></Suspense>;
}
