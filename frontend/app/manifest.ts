import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "AdaptiveAI - GATE Learning",
    short_name: "AdaptiveAI",
    description: "Personalized GATE CSE learning and practice.",
    start_url: "/",
    display: "standalone",
    background_color: "#f7f7f2",
    theme_color: "#147d75",
    icons: [
      { src: "/icon", sizes: "192x192", type: "image/png" },
      { src: "/icon", sizes: "512x512", type: "image/png" },
    ],
  };
}
