import Link from "next/link";

export default function FavoritesPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-8">My Favorites</h1>

      <div className="card p-8 text-center">
        <div className="text-4xl mb-4">
          <svg
            className="mx-auto text-muted/40"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
        </div>
        <p className="text-muted text-lg mb-4">
          Sign in to save and organize your favorite entries
        </p>
        <Link
          href="/sign-in"
          className="inline-block px-6 py-2.5 bg-accent text-white rounded-lg font-mono text-sm hover:opacity-90 transition-opacity"
        >
          Sign In
        </Link>
      </div>
    </div>
  );
}
