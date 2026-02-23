import Link from "next/link";
import { SourceBadge } from "./SourceBadge";

interface EntryCardProps {
  id: string;
  headword: string;
  source: string;
  definition: string;
  pos?: string;
}

export function EntryCard({ id, headword, source, definition, pos }: EntryCardProps) {
  return (
    <Link href={`/entry/${id}`} className="block">
      <div className="card p-4 hover:shadow-md transition-shadow">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="text-lg font-semibold text-foreground">{headword}</h3>
          <SourceBadge source={source} />
          {pos && (
            <span className="font-mono text-xs text-muted italic">{pos}</span>
          )}
        </div>
        <p className="text-sm text-muted leading-relaxed line-clamp-2">
          {definition}
        </p>
      </div>
    </Link>
  );
}
