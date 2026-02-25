import Link from "next/link";
import { notFound } from "next/navigation";
import { getEntry, getSubEntries, getEntriesByAnchor } from "@/lib/queries";
import { SourceBadges, trusselUrl } from "@/components/shared";

export default async function EntryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const entry = await getEntry(id);
  if (!entry) notFound();

  const [subEntries, siblingEntries] = await Promise.all([
    getSubEntries(entry.id),
    entry.headword_ascii
      ? getEntriesByAnchor(entry.headword_ascii).then((entries) =>
          entries.filter((e) => e.id !== entry.id)
        )
      : Promise.resolve([]),
  ]);

  const topics = entry.entry_topic?.map((et) => et.topic).filter(Boolean) ?? [];

  return (
    <>
      {/* Header */}
      <h1>
        {entry.headword_display || entry.headword}
        {entry.subscript && <sub> {entry.subscript}</sub>}
        {" "}
        <SourceBadges in_pe={entry.in_pe} in_mk={entry.in_mk} in_andrews={entry.in_andrews} is_from_eh_only={entry.is_from_eh_only} />
      </h1>

      {/* Metadata line */}
      <p className="small muted">
        ID: {entry.id} | Type: {entry.display_type} | Letter: {entry.letter_page}
        {entry.parent_entry_id && <> | Parent: <Link href={`/entry/${entry.parent_entry_id}`}>{entry.parent_entry_id}</Link></>}
        {entry.source_tag && <> | Tag: {entry.source_tag}</>}
      </p>

      {entry.is_loanword && (
        <p className="small">
          <strong>Loanword</strong>
          {entry.loan_language && <> from {entry.loan_language}</>}
          {entry.loan_source && <>: {entry.loan_source}</>}
        </p>
      )}

      {entry.alt_spelling && entry.alt_spelling.length > 0 && (
        <p className="small">Alt spellings: {entry.alt_spelling.map((a) => a.spelling).join(", ")}</p>
      )}

      {entry.syllable_breakdown && (
        <p className="small mono">Syllables: {entry.syllable_breakdown}</p>
      )}

      {/* Etymology */}
      {entry.etymology && entry.etymology.length > 0 && (
        <div className="detail-section">
          <h2>Etymology</h2>
          {entry.etymology.map((ety) => (
            <div key={ety.id} style={{ marginBottom: 8 }}>
              {ety.proto_form && <><strong>{ety.proto_form}</strong> </>}
              {ety.proto_language && <span className="muted">({ety.proto_language})</span>}
              {ety.meaning && <> &ldquo;{ety.meaning}&rdquo;</>}
              {ety.qualifier && <> [{ety.qualifier}]</>}
              {ety.raw_text && <div className="small muted">{ety.raw_text}</div>}
              {ety.pollex_url && <> <a href={ety.pollex_url} target="_blank" rel="noopener noreferrer">[POLLEX]</a></>}
            </div>
          ))}
        </div>
      )}

      {/* Senses / Definitions */}
      {entry.sense && entry.sense.length > 0 && (
        <div className="detail-section">
          <h2>Definitions ({entry.sense.length})</h2>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Source</th>
                <th>POS</th>
                <th>Definition</th>
              </tr>
            </thead>
            <tbody>
              {entry.sense.map((s) => (
                <tr key={s.id}>
                  <td>{s.sense_num}</td>
                  <td><SourceBadges source={s.source_dict} /></td>
                  <td className="small">{s.pos_raw || "—"}</td>
                  <td>
                    {s.definition_html ? (
                      <span dangerouslySetInnerHTML={{ __html: s.definition_html }} />
                    ) : (
                      s.definition_text || "—"
                    )}
                    {s.hawaiian_gloss && <div className="small muted">Haw: {s.hawaiian_gloss}</div>}

                    {/* Sub-definitions */}
                    {s.sub_definition && s.sub_definition.length > 0 && (
                      <ul style={{ margin: "4px 0", paddingLeft: 20 }}>
                        {s.sub_definition.map((sd) => (
                          <li key={sd.id} className="small">
                            {sd.text}
                            {sd.is_figurative && <em> (fig.)</em>}
                            {sd.is_rare && <em> (rare)</em>}
                            {sd.is_archaic && <em> (arch.)</em>}
                            {sd.sub_definition_domain && sd.sub_definition_domain.length > 0 && (
                              <span className="muted"> [{sd.sub_definition_domain.map((d) => d.code).join(", ")}]</span>
                            )}
                            {sd.linked_word && sd.linked_word.length > 0 && (
                              <span className="muted">
                                {" → "}
                                {sd.linked_word.map((lw, i) => (
                                  <span key={lw.id}>
                                    {i > 0 && ", "}
                                    {lw.target_anchor ? (
                                      <Link href={`/entry/${lw.target_anchor}`}>{lw.surface}</Link>
                                    ) : (
                                      lw.surface
                                    )}
                                  </span>
                                ))}
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}

                    {/* Linked words at sense level */}
                    {s.linked_word && s.linked_word.length > 0 && (
                      <div className="small muted">
                        Links:{" "}
                        {s.linked_word.map((lw, i) => (
                          <span key={lw.id}>
                            {i > 0 && ", "}
                            {lw.target_anchor ? (
                              <Link href={`/entry/${lw.target_anchor}`}>{lw.surface}</Link>
                            ) : (
                              lw.surface
                            )}
                          </span>
                        ))}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Examples */}
      {entry.example && entry.example.length > 0 && (
        <div className="detail-section">
          <h2>Examples ({entry.example.length})</h2>
          <table>
            <thead>
              <tr>
                <th>Hawaiian</th>
                <th>English</th>
                <th>Source</th>
                <th>Note</th>
              </tr>
            </thead>
            <tbody>
              {entry.example.map((ex) => (
                <tr key={ex.id}>
                  <td><em>{ex.hawaiian_text}</em></td>
                  <td>{ex.english_text}</td>
                  <td className="small">
                    <SourceBadges source={ex.source_dict} />
                    {ex.bible_ref && <> {ex.bible_ref}</>}
                    {ex.olelo_noeau_num && <> ON#{ex.olelo_noeau_num}</>}
                  </td>
                  <td className="small muted">{ex.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Images */}
      {entry.image && entry.image.length > 0 && (
        <div className="detail-section">
          <h2>Images ({entry.image.length})</h2>
          {entry.image.map((img) => (
            <div key={img.id} style={{ marginBottom: 8 }}>
              {img.thumbnail_url && (
                <a href={trusselUrl(img.full_image_url || img.thumbnail_url)} target="_blank" rel="noopener noreferrer">
                  <img src={trusselUrl(img.thumbnail_url)} alt={img.alt_text || entry.headword} style={{ maxHeight: 150, border: "1px solid #ccc" }} />
                </a>
              )}
              {img.alt_text && <div className="small muted">{img.alt_text}</div>}
            </div>
          ))}
        </div>
      )}

      {/* Cross-References */}
      {entry.cross_ref && entry.cross_ref.length > 0 && (
        <div className="detail-section">
          <h2>Cross-References ({entry.cross_ref.length})</h2>
          <table>
            <thead>
              <tr><th>Type</th><th>Target</th><th>Source</th></tr>
            </thead>
            <tbody>
              {entry.cross_ref.map((cr) => (
                <tr key={cr.id}>
                  <td className="small">{cr.ref_type || "see"}</td>
                  <td>
                    {cr.target_anchor ? (
                      <Link href={`/entry/${cr.target_anchor}`}>{cr.target_headword || cr.target_anchor}</Link>
                    ) : (
                      cr.target_headword || "—"
                    )}
                  </td>
                  <td><SourceBadges source={cr.source_dict} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Grammar References */}
      {entry.grammar_ref && entry.grammar_ref.length > 0 && (
        <div className="detail-section">
          <h2>Grammar References ({entry.grammar_ref.length})</h2>
          <ul>
            {entry.grammar_ref.map((gr) => (
              <li key={gr.id}>
                {gr.label || gr.section}
                {gr.pdf_url && <> — <a href={trusselUrl(gr.pdf_url)} target="_blank" rel="noopener noreferrer">PDF</a></>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Hawaiian Glosses */}
      {entry.hawaiian_gloss && entry.hawaiian_gloss.length > 0 && (
        <div className="detail-section">
          <h2>Hawaiian Glosses ({entry.hawaiian_gloss.length})</h2>
          <ul>
            {entry.hawaiian_gloss.map((hg) => (
              <li key={hg.id}>
                <em>{hg.gloss}</em>
                {hg.source_ref && <span className="small muted"> ({hg.source_ref})</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Topics */}
      {topics.length > 0 && (
        <div className="detail-section">
          <h2>Topics</h2>
          <p>
            {topics.map((t, i) => (
              <span key={t.id}>
                {i > 0 && ", "}
                <Link href={`/topics/${encodeURIComponent(t.name)}`}>{t.name}</Link>
              </span>
            ))}
          </p>
        </div>
      )}

      {/* Related entries (same headword) */}
      {siblingEntries.length > 0 && (
        <div className="detail-section">
          <h2>Related Entries ({siblingEntries.length})</h2>
          <table>
            <thead>
              <tr><th>Headword</th><th>Sources</th><th>Definition</th></tr>
            </thead>
            <tbody>
              {siblingEntries.map((sib) => (
                <tr key={sib.id}>
                  <td>
                    <Link href={`/entry/${sib.id}`}>
                      {sib.headword_display || sib.headword}
                      {sib.subscript && <sub>{sib.subscript}</sub>}
                    </Link>
                  </td>
                  <td><SourceBadges in_pe={sib.in_pe} in_mk={sib.in_mk} in_andrews={sib.in_andrews} is_from_eh_only={sib.is_from_eh_only} /></td>
                  <td className="small">{sib.sense?.[0]?.definition_text?.slice(0, 100) || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Sub-entries */}
      {subEntries.length > 0 && (
        <div className="detail-section">
          <h2>Sub-entries ({subEntries.length})</h2>
          <table>
            <thead>
              <tr><th>Headword</th><th>Sources</th><th>Definition</th></tr>
            </thead>
            <tbody>
              {subEntries.map((sub) => (
                <tr key={sub.id}>
                  <td>
                    <Link href={`/entry/${sub.id}`}>
                      {sub.headword_display || sub.headword}
                      {sub.subscript && <sub>{sub.subscript}</sub>}
                    </Link>
                  </td>
                  <td><SourceBadges in_pe={sub.in_pe} in_mk={sub.in_mk} in_andrews={sub.in_andrews} is_from_eh_only={sub.is_from_eh_only} /></td>
                  <td className="small">{sub.sense?.[0]?.definition_text?.slice(0, 100) || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="small muted" style={{ marginTop: 32 }}>Entry ID: {entry.id}</p>
    </>
  );
}
