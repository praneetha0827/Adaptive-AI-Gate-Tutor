import { ImageResponse } from "next/og";

export const size = { width: 512, height: 512 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    <div style={{ alignItems: "center", background: "#147d75", color: "white", display: "flex", fontFamily: "Arial", fontSize: 192, fontWeight: 800, height: "100%", justifyContent: "center", width: "100%" }}>A</div>,
    size,
  );
}
