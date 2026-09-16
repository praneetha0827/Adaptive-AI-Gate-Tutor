"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "../../lib/api";

type Subject = { title: string; topics: { title: string; subtopics: { id: string; title: string }[] }[] };

export default function TopicsPage() {
  const router = useRouter(); const [subjects, setSubjects] = useState<Subject[]>([]); const [loadingSubtopicId, setLoadingSubtopicId] = useState(""); const [error, setError] = useState("");
  useEffect(() => { apiRequest<{ id: string }[]>("/curriculum/versions").then((versions) => apiRequest<Subject[]>(`/curriculum/subjects?curriculum_version_id=${versions[0]?.id}`)).then(setSubjects).catch((reason) => setError(reason instanceof Error ? reason.message : "Unable to load curriculum")); }, []);
  async function assign(subtopicId: string) { setLoadingSubtopicId(subtopicId); try { const result = await apiRequest<{ status: string; subtopic_id: string; prerequisite_subtopic_id: string | null }>("/topics/assign", { method: "POST", body: JSON.stringify({ subtopic_id: subtopicId }) }); const lessonSubtopicId = result.status === "assigned" ? result.subtopic_id : result.prerequisite_subtopic_id; if (lessonSubtopicId) router.push(`/learn?subtopicId=${encodeURIComponent(lessonSubtopicId)}`); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to open topic"); } finally { setLoadingSubtopicId(""); } }
  return <main className="topics-page"><p className="eyebrow">Choose a topic</p><h1>What do you want to learn?</h1><p className="intro">Pick any concept to begin. If it depends on an earlier idea, AdaptiveAI will start you there.</p>{error && <p className="error">{error}</p>}<div className="topic-subjects">{subjects.map((subject) => { const subtopics = subject.topics.flatMap((topic) => topic.subtopics); return <section className="topic-subject" key={subject.title}><h2>{subject.title}</h2>{subtopics.length ? <div className="topic-chip-list">{subtopics.map((subtopic) => <button className="topic-chip" disabled={Boolean(loadingSubtopicId)} key={subtopic.id} onClick={() => assign(subtopic.id)}>{loadingSubtopicId === subtopic.id ? "Opening..." : subtopic.title}</button>)}</div> : <p>No reviewed subtopics available yet.</p>}</section>; })}</div></main>;
}
