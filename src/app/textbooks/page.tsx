export default function TextbooksPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-4">Hawaiian Language Textbooks</h1>
      <p className="text-muted leading-relaxed mb-8 max-w-3xl">
        Frequency analysis of vocabulary across six major Hawaiian language textbooks.
        Words are ranked by how many of the six textbooks include them, providing an
        indication of core vocabulary importance for learners.
      </p>

      {/* 6/6 Tier */}
      <section className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <h2 className="text-xl font-bold">6/6</h2>
          <span className="font-mono text-xs text-muted uppercase tracking-wider">
            Highest Frequency
          </span>
        </div>
        <div className="card p-5">
          <div className="flex flex-wrap gap-3">
            {["aloha", "mahalo", "ʻae", "ʻaʻole", "hele"].map((word) => (
              <span
                key={word}
                className="px-3 py-1.5 rounded-md bg-accent/10 text-accent font-semibold text-sm"
              >
                {word}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* 5/6 Tier */}
      <section className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <h2 className="text-xl font-bold">5/6</h2>
          <span className="font-mono text-xs text-muted uppercase tracking-wider">
            Very High Frequency
          </span>
        </div>
        <div className="card p-5">
          <div className="flex flex-wrap gap-3">
            {["maikaʻi", "nui", "hana", "wai", "mea"].map((word) => (
              <span
                key={word}
                className="px-3 py-1.5 rounded-md bg-accent/10 text-accent font-semibold text-sm"
              >
                {word}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* 4/6 Tier */}
      <section className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <h2 className="text-xl font-bold">4/6</h2>
          <span className="font-mono text-xs text-muted uppercase tracking-wider">
            High Frequency
          </span>
        </div>
        <div className="card p-5">
          <p className="text-sm text-muted">Additional frequency tiers coming soon...</p>
        </div>
      </section>
    </div>
  );
}
