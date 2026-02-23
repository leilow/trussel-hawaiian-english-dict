import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-card-border mt-16 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-sm">
          <div>
            <h4 className="font-mono text-xs uppercase tracking-wider text-muted mb-3">
              Dictionary
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/browse" className="text-muted hover:text-foreground transition-colors">
                  Browse
                </Link>
              </li>
              <li>
                <Link href="/topics" className="text-muted hover:text-foreground transition-colors">
                  Topics
                </Link>
              </li>
              <li>
                <Link href="/concordance" className="text-muted hover:text-foreground transition-colors">
                  Concordance
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-mono text-xs uppercase tracking-wider text-muted mb-3">
              Resources
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/textbooks" className="text-muted hover:text-foreground transition-colors">
                  Textbooks
                </Link>
              </li>
              <li>
                <Link href="/word-lists" className="text-muted hover:text-foreground transition-colors">
                  Word Lists
                </Link>
              </li>
              <li>
                <Link href="/references" className="text-muted hover:text-foreground transition-colors">
                  References
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-mono text-xs uppercase tracking-wider text-muted mb-3">
              Account
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/favorites" className="text-muted hover:text-foreground transition-colors">
                  Favorites
                </Link>
              </li>
              <li>
                <Link href="/mind-map" className="text-muted hover:text-foreground transition-colors">
                  Mind Map
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-mono text-xs uppercase tracking-wider text-muted mb-3">
              About
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/about" className="text-muted hover:text-foreground transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link href="/statistics" className="text-muted hover:text-foreground transition-colors">
                  Statistics
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-6 border-t border-card-border text-center text-xs text-muted">
          <p>
            Based on the{" "}
            <a
              href="https://trussel2.com/HAW/"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-foreground transition-colors"
            >
              Combined Hawaiian Dictionary
            </a>{" "}
            by Kepano Trussel
          </p>
        </div>
      </div>
    </footer>
  );
}
