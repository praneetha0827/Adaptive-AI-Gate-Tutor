import type { Metadata } from "next";
import AppNavigation from "../components/app-navigation";
import "./globals.css";

export const metadata: Metadata = {
  title: "AdaptiveAI",
  description: "Your adaptive GATE learning companion",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body><AppNavigation />{children}</body>
    </html>
  );
}
