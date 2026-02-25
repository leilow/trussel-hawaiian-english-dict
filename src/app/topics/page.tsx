import Link from "next/link";
import { getTopics } from "@/lib/queries";
import { TOPIC_CODE_MAP, isDisplayableTopic } from "@/lib/topics";

export default async function TopicsPage() {
  const allTopics = await getTopics();

  const topics = allTopics
    .filter((t) => isDisplayableTopic(t.name))
    .map((t) => ({
      ...t,
      display: TOPIC_CODE_MAP[t.name].display,
      description: TOPIC_CODE_MAP[t.name].description,
    }))
    .sort((a, b) => a.display.localeCompare(b.display));

  return (
    <>
      <h1>Topics</h1>
      <p className="muted">{topics.length} topical categories</p>

      <table>
        <thead>
          <tr>
            <th>Code</th>
            <th>Topic</th>
            <th>Description</th>
            <th>Entries</th>
          </tr>
        </thead>
        <tbody>
          {topics.map((t) => (
            <tr key={t.id}>
              <td className="mono">{t.name}</td>
              <td><Link href={`/topics/${encodeURIComponent(t.name)}`}>{t.display}</Link></td>
              <td className="small muted">{t.description}</td>
              <td>{t.entry_count.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
