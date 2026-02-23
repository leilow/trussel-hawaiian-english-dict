import Link from "next/link";

const topics = [
  { name: "Animals", slug: "animals", count: 342 },
  { name: "Birds", slug: "birds", count: 187 },
  { name: "Body Parts", slug: "body-parts", count: 256 },
  { name: "Colors", slug: "colors", count: 48 },
  { name: "Dance", slug: "dance", count: 134 },
  { name: "Fish", slug: "fish", count: 412 },
  { name: "Food", slug: "food", count: 289 },
  { name: "Greetings", slug: "greetings", count: 67 },
  { name: "Music", slug: "music", count: 156 },
  { name: "Plants", slug: "plants", count: 523 },
  { name: "Stars", slug: "stars", count: 98 },
  { name: "Weather", slug: "weather", count: 175 },
];

export default function TopicsPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">Topics</h1>
      <p className="text-muted mb-8">Browse Hawaiian vocabulary organized by subject</p>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {topics.map((topic) => (
          <Link key={topic.slug} href={`/topics/${topic.slug}`} className="block">
            <div className="card p-5 hover:shadow-md transition-shadow h-full">
              <h2 className="text-lg font-semibold text-foreground mb-1">{topic.name}</h2>
              <p className="font-mono text-xs text-muted">
                {topic.count.toLocaleString()} entries
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
