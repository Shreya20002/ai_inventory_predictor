import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Inventory Health",
  description: "Predictive dead stock analysis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

