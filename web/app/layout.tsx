import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Turkey news — climate mentions",
  description:
    "Headline-level scan of major Turkish outlets for climate-related keywords (research / transparency).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <nav>
            <Link href="/" className="brand">
              Turkey climate headlines
            </Link>
            <Link href="/methodology">Methodology</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
