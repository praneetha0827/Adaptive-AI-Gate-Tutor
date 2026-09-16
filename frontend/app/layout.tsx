import type { Metadata, Viewport } from "next";
import AppNavigation from "../components/app-navigation";
import PwaRegistration from "../components/pwa-registration";
import "./globals.css";

export const metadata: Metadata = {
  applicationName: "AdaptiveAI",
  title: { default: "AdaptiveAI", template: "%s | AdaptiveAI" },
  description: "Your adaptive GATE learning companion",
  manifest: "/manifest.webmanifest",
  appleWebApp: { capable: true, statusBarStyle: "default", title: "AdaptiveAI" },
  icons: { apple: "/apple-icon" },
};

export const viewport: Viewport = { themeColor: "#147d75", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body><AppNavigation />{children}<PwaRegistration /></body>
    </html>
  );
}
