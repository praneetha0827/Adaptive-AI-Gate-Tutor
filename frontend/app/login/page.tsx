"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "../../lib/api";

export default function LoginPage() {
  const router = useRouter(); const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const form = new FormData(event.currentTarget); try { const token = await apiRequest<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email: form.get("email"), password: form.get("password") }) }); sessionStorage.setItem("access_token", token.access_token); const user = await apiRequest<{ onboarding_completed: boolean }>("/me"); router.push(user.onboarding_completed ? "/" : "/onboarding"); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to sign in"); } }
  return <main className="form-page"><h1>Welcome back</h1><form onSubmit={submit}><input name="email" type="email" placeholder="Email" required /><input name="password" type="password" placeholder="Password" required /><button>Sign in</button>{error && <p className="error">{error}</p>}</form><p>New here? <Link href="/register">Create an account</Link>.</p></main>;
}
