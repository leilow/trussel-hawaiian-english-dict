import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Trussel Hawaiian-English Dictionary — Test UI",
    template: "%s | Trussel Test UI",
  },
  description: "Data validation browser for the Combined Hawaiian Dictionary scraper.",
};

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/browse", label: "Haw-Eng" },
  { href: "/eng-haw", label: "Eng-Haw" },
  { href: "/concordance", label: "Concordance" },
  { href: "/topics", label: "Topics" },
  { href: "/references", label: "References" },
  { href: "/sources", label: "Sources" },
  { href: "/prefaces", label: "Prefaces" },
  { href: "/wordlists", label: "Wordlists" },
  { href: "/gloss-sources", label: "Glosses" },
  { href: "/images", label: "Images" },
  { href: "/pages", label: "Pages" },
  { href: "/statistics", label: "Stats" },
  { href: "/search", label: "Search" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <nav className="main-nav">
          {navLinks.map((link) => (
            <Link key={link.href} href={link.href}>
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="container">{children}</div>
      </body>
    </html>
  );
}
