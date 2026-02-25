import Link from "next/link";
import { notFound } from "next/navigation";
import { getTopicByName, getEntriesByTopic } from "@/lib/queries";
import { getTopicDisplay, isDisplayableTopic } from "@/lib/topics";
import { SourceBadges, Pagination } from "@/components/shared";

const ITEMS_PER_PAGE = 100;

export default async function TopicPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { slug } = await params;
  const sp = await searchParams;
  const topicName = decodeURIComponent(slug);
  const page = Math.max(1, parseInt(sp.page || "1", 10));

  if (!isDisplayableTopic(topicName)) notFound();

  const topic = await getTopicByName(topicName);
  if (!topic) notFound();

  const { entries, total } = await getEntriesByTopic(topic.id, page, ITEMS_PER_PAGE);
  const displayName = getTopicDisplay(topicName);

  return (
    <>
      <p><Link href="/topics">&larr; Back to topics</Link></p>
      <h1>{displayName} ({topicName})</h1>
      <p className="small muted">{total.toLocaleString()} entries</p>

      <table>
        <thead>
          <tr>
            <th>Headword</th>
            <th>Sources</th>
            <th>Definition</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e) => (
            <tr key={e.id}>
              <td>
                <Link href={`/entry/${e.id}`}>
                  {e.headword_display || e.headword}
                  {e.subscript && <sub>{e.subscript}</sub>}
                </Link>
              </td>
              <td><SourceBadges in_pe={e.in_pe} in_mk={e.in_mk} in_andrews={e.in_andrews} is_from_eh_only={e.is_from_eh_only} /></td>
              <td className="small">{e.sense?.[0]?.definition_text?.slice(0, 120) || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {entries.length === 0 && <p className="muted">No entries in this topic.</p>}

      <Pagination
        currentPage={page}
        totalItems={total}
        itemsPerPage={ITEMS_PER_PAGE}
        basePath={`/topics/${encodeURIComponent(topicName)}`}
      />
    </>
  );
}
