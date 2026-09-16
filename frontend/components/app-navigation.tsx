"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const learnerLinks = [
  { href: "/", label: "Dashboard" },
  { href: "/learn", label: "Lesson" },
  { href: "/quiz", label: "Practice" },
  { href: "/topics", label: "Topics" },
];

export default function AppNavigation() {
  const pathname = usePathname();
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    setIsAuthenticated(Boolean(sessionStorage.getItem("access_token")));
  }, [pathname]);

  function signOut() {
    sessionStorage.removeItem("access_token");
    setIsAuthenticated(false);
    router.push("/login");
  }

  return (
    <nav className="app-nav" aria-label="Primary navigation">
      <Link className="brand" href="/">AdaptiveAI</Link>
      <div className="nav-links">
        {isAuthenticated && learnerLinks.map((link) => <Link className={pathname === link.href ? "nav-link active" : "nav-link"} href={link.href} key={link.href}>{link.label}</Link>)}
      </div>
      <div className="nav-actions">
        {isAuthenticated ? <button className="text-button" onClick={signOut}>Sign out</button> : <><Link className="nav-link" href="/login">Sign in</Link><Link className="button compact-button" href="/register">Create account</Link></>}
      </div>
    </nav>
  );
}
