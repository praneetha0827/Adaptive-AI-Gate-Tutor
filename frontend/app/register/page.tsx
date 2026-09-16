"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "../../lib/api";

export default function RegisterPage() {
  const router = useRouter(); const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const form = new FormData(event.currentTarget); const email = String(form.get("email")); const password = String(form.get("password")); try { await apiRequest("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }); const token = await apiRequest<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }); sessionStorage.setItem("access_token", token.access_token); router.push("/onboarding"); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to create account"); } }
  return <main className="form-page"><h1>Create your learning profile</h1><form onSubmit={submit}><input name="email" type="email" placeholder="Email" required /><input name="password" type="password" minLength={12} placeholder="Password (12+ characters)" required /><button>Create account</button>{error && <p className="error">{error}</p>}</form><p>Already registered? <Link href="/login">Sign in</Link>.</p></main>;
}
