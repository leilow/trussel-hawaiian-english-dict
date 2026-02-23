import Link from "next/link";
import { SourceBadge } from "@/components/SourceBadge";
import { FavoriteButton } from "@/components/FavoriteButton";

export default async function EntryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <h1 className="text-4xl font-bold">aloha</h1>
        <SourceBadge source="PE" />
        <FavoriteButton />
      </div>

      {/* Etymology */}
      <div className="card p-4 mb-6 bg-card/50">
        <h2 className="font-mono text-xs uppercase tracking-wider text-muted mb-2">Etymology</h2>
        <p className="text-sm text-muted italic">PPN *alofa</p>
      </div>

      {/* Definitions */}
      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4">Definitions</h2>
        <div className="space-y-4">
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-xs text-accent font-semibold">1.</span>
              <span className="font-mono text-xs text-muted italic">n.</span>
            </div>
            <p className="text-foreground">
              Love, affection, compassion, mercy, sympathy, pity, kindness, sentiment, grace, charity;
              greeting, salutation, regards; sweetheart, lover, loved one.
            </p>
          </div>
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-xs text-accent font-semibold">2.</span>
              <span className="font-mono text-xs text-muted italic">v.t.</span>
            </div>
            <p className="text-foreground">
              To love, be fond of; to show kindness, mercy, pity, charity, affection; to venerate;
              to remember with affection; to greet, hail.
            </p>
          </div>
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-mono text-xs text-accent font-semibold">3.</span>
              <span className="font-mono text-xs text-muted italic">interj.</span>
            </div>
            <p className="text-foreground">
              Hello! Goodbye! An exclamation of greeting or farewell.
            </p>
          </div>
        </div>
      </section>

      {/* Examples */}
      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4">Examples</h2>
        <div className="space-y-3">
          <div className="card p-4">
            <p className="text-foreground italic mb-1">Aloha kākou.</p>
            <p className="text-sm text-muted">Greetings to all of us (inclusive).</p>
          </div>
          <div className="card p-4">
            <p className="text-foreground italic mb-1">Ke aloha nō!</p>
            <p className="text-sm text-muted">Alas! (An exclamation of pity or sympathy.)</p>
          </div>
        </div>
      </section>

      {/* Cross-References */}
      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4">See Also</h2>
        <div className="flex flex-wrap gap-2">
          <Link
            href="/entry/100"
            className="card px-3 py-1.5 text-sm text-accent hover:shadow-md transition-shadow"
          >
            aroha
          </Link>
          <Link
            href="/entry/2"
            className="card px-3 py-1.5 text-sm text-accent hover:shadow-md transition-shadow"
          >
            aloha ʻāina
          </Link>
        </div>
      </section>

      {/* Topics */}
      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4">Topics</h2>
        <div className="flex flex-wrap gap-2">
          <Link
            href="/topics/greetings"
            className="font-mono text-xs bg-accent/10 text-accent px-3 py-1 rounded-full hover:bg-accent/20 transition-colors"
          >
            Greetings
          </Link>
          <Link
            href="/topics/emotions"
            className="font-mono text-xs bg-accent/10 text-accent px-3 py-1 rounded-full hover:bg-accent/20 transition-colors"
          >
            Emotions
          </Link>
        </div>
      </section>

      {/* Sub-entries */}
      <section className="mb-8">
        <h2 className="text-xl font-bold mb-4">Sub-entries</h2>
        <div className="space-y-3">
          <Link href="/entry/2" className="block">
            <div className="card p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-lg font-semibold">aloha ʻāina</h3>
                <SourceBadge source="PE" />
              </div>
              <p className="text-sm text-muted">Love of the land, patriotism.</p>
            </div>
          </Link>
          <Link href="/entry/6" className="block">
            <div className="card p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-lg font-semibold">aloha nui</h3>
                <SourceBadge source="PE" />
              </div>
              <p className="text-sm text-muted">Much love, great affection; very much loved.</p>
            </div>
          </Link>
        </div>
      </section>

      {/* Entry ID for debugging */}
      <div className="text-xs text-muted/50 font-mono mt-12">
        Entry ID: {id}
      </div>
    </div>
  );
}
