import { EntryCard } from "@/components/EntryCard";

const mockTopicEntries = [
  { id: "20", headword: "manu", source: "PE", definition: "Bird, any winged creature." },
  { id: "21", headword: "ʻalalā", source: "PE", definition: "Hawaiian crow (Corvus hawaiiensis)." },
  { id: "22", headword: "nēnē", source: "PE", definition: "The Hawaiian goose (Branta sandvicensis), the state bird." },
  { id: "23", headword: "pueo", source: "PE", definition: "Hawaiian short-eared owl (Asio flammeus sandwichensis)." },
  { id: "24", headword: "ʻiʻiwi", source: "PE", definition: "A Hawaiian honeycreeper with vermilion plumage (Drepanis coccinea)." },
  { id: "25", headword: "ʻapapane", source: "PE", definition: "A Hawaiian honeycreeper (Himatione sanguinea)." },
  { id: "26", headword: "kolea", source: "PE", definition: "Pacific golden plover (Pluvialis fulva)." },
  { id: "27", headword: "ʻalae", source: "PE", definition: "Hawaiian coot, Hawaiian gallinule, mudhen." },
];

export default async function TopicPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const topicName = slug
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">{topicName}</h1>
      <p className="text-sm text-muted font-mono mb-8">187 entries</p>

      <div className="space-y-3">
        {mockTopicEntries.map((entry) => (
          <EntryCard
            key={entry.id}
            id={entry.id}
            headword={entry.headword}
            source={entry.source}
            definition={entry.definition}
          />
        ))}
      </div>
    </div>
  );
}
