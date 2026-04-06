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
        <footer className="site-footer">
          <p>
            Made by Faruk Avcı ·{" "}
            <a href="mailto:itsfarukavci@gmail.com">itsfarukavci@gmail.com</a>
          </p>
        </footer>
      </body>
    </html>
  );
}
