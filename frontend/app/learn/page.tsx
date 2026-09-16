"use client";

import { FormEvent, Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { apiRequest } from "../../lib/api";
import ConceptVisual from "../../components/concept-visual";

type Turn = { stage: string; explanation: string; question: string | null; hint: string | null };

function LearnPageContent() {
  const searchParams = useSearchParams(); const subtopicId = searchParams.get("subtopicId"); const [turns, setTurns] = useState<Turn[]>([]); const [sessionId, setSessionId] = useState(""); const [isSending, setIsSending] = useState(false); const [error, setError] = useState("");
  useEffect(() => { const path = subtopicId ? "/tutor/sessions" : "/tutor/recommended-session"; const options = subtopicId ? { method: "POST", body: JSON.stringify({ subtopic_id: subtopicId }) } : { method: "POST" }; apiRequest<{ session_id: string; turn: Turn }>(path, options).then((response) => { setSessionId(response.session_id); setTurns([response.turn]); }).catch((reason) => setError(reason instanceof Error ? reason.message : "Unable to start lesson")); }, [subtopicId]);
  async function sendMessage(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (isSending) return; const formElement = event.currentTarget; const form = new FormData(formElement); const message = String(form.get("message") ?? "").trim(); if (!message) return; setIsSending(true); try { const nextTurn = await apiRequest<Turn>(`/tutor/sessions/${sessionId}/messages`, { method: "POST", body: JSON.stringify({ message }) }); setTurns((currentTurns) => [...currentTurns, nextTurn]); formElement.reset(); setError(""); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to continue lesson"); } finally { setIsSending(false); } }
  if (error && !turns.length) return <main className="form-page"><h1>Lesson unavailable</h1><p className="error">{error}</p><p>Configure the server-side AI provider, then try again.</p></main>;
  if (!turns.length) return <main className="form-page"><p>Preparing your next lesson…</p></main>;
  return <main className="lesson-page"><header className="lesson-header"><p className="eyebrow">Adaptive lesson</p><h1>Learn by thinking, not just reading.</h1><p>Work through the idea, then test it in your own words.</p></header><div className="lesson-layout"><div className="lesson-turns">{turns.map((turn, index) => <section className="lesson-turn" key={index}><div className="turn-meta"><span>{index + 1}</span><p className="eyebrow">{turn.stage.replace("_", " ")}</p></div><div className="turn-content"><p>{turn.explanation}</p><ConceptVisual content={`${turn.explanation} ${turn.question ?? ""}`} />{turn.question && <div className="thinking-prompt"><span>Try it</span><h2>{turn.question}</h2></div>}{turn.hint && <details><summary>Need a hint?</summary><p>{turn.hint}</p></details>}</div></section>)}</div><aside className="answer-panel"><p className="eyebrow">Your turn</p><h2>Put the idea into words.</h2><form onSubmit={sendMessage}><textarea name="message" placeholder="Write your answer, reasoning, or ask for a hint" required disabled={isSending} rows={5} /><button disabled={isSending}>{isSending ? "Thinking..." : "Continue lesson"}</button></form>{error && <p className="error">{error}</p>}<p className="answer-note">A rough answer is enough. The tutor will help you improve it.</p></aside></div></main>;
}

export default function LearnPage() {
  return <Suspense fallback={<main className="form-page"><p>Preparing your lesson…</p></main>}><LearnPageContent /></Suspense>;
}
