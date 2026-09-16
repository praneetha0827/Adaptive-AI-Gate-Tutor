"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "../../lib/api";

type Question = { id: string; question_type: string; prompt: string; options: { label: string; text: string }[] | null };
type Diagnostic = { id: string; questions: Question[] };

export default function DiagnosticPage() {
  const router = useRouter(); const [diagnostic, setDiagnostic] = useState<Diagnostic | null>(null); const [answers, setAnswers] = useState<Record<string, string>>({}); const [answeredAt, setAnsweredAt] = useState<Record<string, number>>({}); const [startedAt, setStartedAt] = useState(0); const [error, setError] = useState("");
  useEffect(() => { apiRequest<{ id: string }[]>("/curriculum/versions").then((versions) => apiRequest<Diagnostic>("/diagnostics/start", { method: "POST", body: JSON.stringify({ curriculum_version_id: versions[0]?.id, question_limit: 6 }) })).then((response) => { setDiagnostic(response); setStartedAt(Date.now()); }).catch((reason) => setError(reason instanceof Error ? reason.message : "Unable to start diagnostic")); }, []);
  async function submit() { if (!diagnostic) return; if (Object.keys(answers).length !== diagnostic.questions.length) { setError("Answer every question before submitting."); return; } try { await apiRequest(`/diagnostics/${diagnostic.id}/submit`, { method: "POST", body: JSON.stringify({ answers: diagnostic.questions.map((question) => ({ question_id: question.id, answer: answers[question.id], response_time_ms: Math.min(7_200_000, Math.max(1, answeredAt[question.id] - startedAt)) })) }) }); router.push("/"); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to submit diagnostic"); } }
  if (error && !diagnostic) return <main className="form-page"><h1>Diagnostic unavailable</h1><p className="error">{error}</p></main>;
  if (!diagnostic) return <main className="form-page"><p>Preparing your diagnostic…</p></main>;
  return <main className="form-page"><p className="eyebrow">Step 2 of 2</p><h1>Quick diagnostic</h1>{diagnostic.questions.map((question, index) => <section className="diagnostic-question" key={question.id}><strong>{index + 1}. {question.prompt}</strong>{question.options ? question.options.map((option) => <label key={option.label}><input type="radio" name={question.id} value={option.label} onChange={() => { setAnswers({ ...answers, [question.id]: option.label }); setAnsweredAt({ ...answeredAt, [question.id]: Date.now() }); setError(""); }} /> {option.label}. {option.text}</label>) : <input aria-label={`Answer for question ${index + 1}`} inputMode={question.question_type === "nat" ? "decimal" : "text"} placeholder="Your answer" value={answers[question.id] ?? ""} onChange={(event) => { setAnswers({ ...answers, [question.id]: event.target.value }); setAnsweredAt({ ...answeredAt, [question.id]: Date.now() }); setError(""); }} />}</section>)}<button onClick={submit}>Submit diagnostic</button>{error && <p className="error">{error}</p>}</main>;
}
