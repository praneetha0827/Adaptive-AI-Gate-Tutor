import Dashboard from "../components/dashboard";

export default function DashboardPage() {
  return (
    <main>
      <header>
        <p className="eyebrow">AdaptiveAI · GATE CSE</p>
        <h1>Know exactly what to study next.</h1>
        <p className="intro">Your plan responds to your answers, pace, and topics that need another look.</p>
      </header>
      <Dashboard />
    </main>
  );
}
