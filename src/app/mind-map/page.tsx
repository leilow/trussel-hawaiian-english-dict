import Link from "next/link";

export default function MindMapPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-4">Mind Map</h1>
      <p className="text-muted mb-8">
        Sign in and add favorites to build your word mind map
      </p>

      <div className="card p-8 mb-8 text-center">
        <Link
          href="/sign-in"
          className="inline-block px-6 py-2.5 bg-accent text-white rounded-lg font-mono text-sm hover:opacity-90 transition-opacity"
        >
          Sign In to Get Started
        </Link>
      </div>

      <div className="border-2 border-dashed border-card-border rounded-lg p-16 text-center">
        <p className="text-muted">
          Interactive mind map visualization will appear here
        </p>
      </div>
    </div>
  );
}
