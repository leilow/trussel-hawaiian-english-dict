import Link from "next/link";
import { SearchBar } from "@/components/SearchBar";

const stats = [
  { label: "Entries", value: "59,417" },
  { label: "Definitions", value: "69,847" },
  { label: "Concordance", value: "133,684" },
  { label: "Sources", value: "5" },
];

const quickLinks = [
  { href: "/browse", title: "Browse by Letter", description: "Explore entries alphabetically through the Hawaiian alphabet" },
  { href: "/topics", title: "Topics", description: "Find words organized by subject: animals, plants, stars, and more" },
  { href: "/concordance", title: "Concordance", description: "Search through sentences from Hawaiian language texts" },
  { href: "/word-lists", title: "Word Lists", description: "Historical word lists from early Western visitors to Hawaiʻi" },
];

export default function HomePage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6">
      {/* Hero */}
      <section className="py-16 sm:py-24 text-center">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
          Trussel Hawaiian-English Dictionary
        </h1>
        <p className="text-lg text-muted mb-8 max-w-2xl mx-auto">
          A comprehensive merged dictionary of the Hawaiian language
        </p>
        <SearchBar />
      </section>

      {/* Stats Row */}
      <section className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-16">
        {stats.map((stat) => (
          <div key={stat.label} className="card p-5 text-center">
            <div className="text-2xl sm:text-3xl font-bold text-foreground mb-1">
              {stat.value}
            </div>
            <div className="font-mono text-xs uppercase tracking-wider text-muted">
              {stat.label}
            </div>
          </div>
        ))}
      </section>

      {/* Word of the Day */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-4">Word of the Day</h2>
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-3">
            <Link href="/entry/1" className="text-2xl font-bold text-foreground hover:text-accent transition-colors">
              aloha
            </Link>
            <span className="source-badge bg-source-pe/15 text-source-pe">PE</span>
          </div>
          <p className="text-muted leading-relaxed">
            Love, affection, compassion, mercy, sympathy, pity, kindness, sentiment, grace, charity;
            greeting, salutation, regards; sweetheart, lover, loved one; beloved, loving, kind,
            compassionate, charitable, lovable; to love, be fond of; to show kindness, mercy,
            pity, charity, affection; to venerate; to remember with affection; to greet, hail.
          </p>
        </div>
      </section>

      {/* Quick Links */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-4">Explore</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickLinks.map((link) => (
            <Link key={link.href} href={link.href} className="block">
              <div className="card p-5 h-full hover:shadow-md transition-shadow">
                <h3 className="font-semibold text-foreground mb-2">{link.title}</h3>
                <p className="text-sm text-muted">{link.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
