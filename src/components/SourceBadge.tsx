const sourceColors: Record<string, string> = {
  PE: "bg-source-pe/15 text-source-pe",
  MK: "bg-source-mk/15 text-source-mk",
  Andrews: "bg-source-andrews/15 text-source-andrews",
  EH: "bg-source-eh/15 text-source-eh",
  Other: "bg-source-other/15 text-source-other",
};

export function SourceBadge({ source }: { source: string }) {
  const colorClass = sourceColors[source] || sourceColors["Other"];
  return (
    <span className={`source-badge ${colorClass}`}>
      {source}
    </span>
  );
}
