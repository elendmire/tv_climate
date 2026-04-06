import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Climate mentions — Turkish news",
  description: "Climate-related keyword matches across Turkish news listings and feeds.",
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
              Climate pulse
            </Link>
            <Link href="/methodology">Methodology</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
