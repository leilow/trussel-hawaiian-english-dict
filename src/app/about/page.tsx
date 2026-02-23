import { SourceBadge } from "@/components/SourceBadge";

export default function AboutPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-8">About This Dictionary</h1>

      <div className="prose max-w-3xl">
        <div className="card p-6 mb-8">
          <p className="text-muted leading-relaxed mb-4">
            The Trussel Hawaiian-English Dictionary is a digital interface for the
            Combined Hawaiian Dictionary (CHD), originally compiled by Kepano Trussel
            and hosted at{" "}
            <a
              href="https://trussel2.com/HAW/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent underline hover:text-foreground transition-colors"
            >
              trussel2.com
            </a>
            . This project merges five major Hawaiian dictionary sources into a single
            searchable reference with over 59,000 entries.
          </p>
          <p className="text-muted leading-relaxed">
            The goal of this digital edition is to make these invaluable resources more
            accessible to students, scholars, and speakers of the Hawaiian language through
            modern search, cross-referencing, concordance, and topical browsing.
          </p>
        </div>

        <h2 className="text-2xl font-bold mb-6">Sources</h2>

        <div className="space-y-6 mb-8">
          <div className="card p-5">
            <div className="flex items-center gap-2 mb-2">
              <SourceBadge source="PE" />
              <h3 className="font-semibold text-foreground">Pukui &amp; Elbert Hawaiian Dictionary</h3>
            </div>
            <p className="text-sm text-muted leading-relaxed">
              Mary Kawena Pukui and Samuel H. Elbert, <em>Hawaiian Dictionary: Hawaiian-English,
              English-Hawaiian</em>, Revised and Enlarged Edition (1986). The most comprehensive
              and widely used Hawaiian dictionary, with approximately 42,000 entries covering
              vocabulary from traditional to modern Hawaiian.
            </p>
          </div>

          <div className="card p-5">
            <div className="flex items-center gap-2 mb-2">
              <SourceBadge source="MK" />
              <h3 className="font-semibold text-foreground">Mamaka Kaiao</h3>
            </div>
            <p className="text-sm text-muted leading-relaxed">
              Komike Huaʻolelo, Hale Kuamoʻo, ʻAha Punana Leo, <em>Mamaka Kaiao: A Modern
              Hawaiian Vocabulary</em> (2003). A collection of modern Hawaiian words coined
              to meet the needs of contemporary life, including terms for technology, science,
              and modern concepts.
            </p>
          </div>

          <div className="card p-5">
            <div className="flex items-center gap-2 mb-2">
              <SourceBadge source="Andrews" />
              <h3 className="font-semibold text-foreground">Lorrin Andrews Dictionary</h3>
            </div>
            <p className="text-sm text-muted leading-relaxed">
              Lorrin Andrews, <em>A Dictionary of the Hawaiian Language</em> (1865).
              One of the earliest comprehensive Hawaiian dictionaries, compiled by a
              missionary and educator who spent decades in the Hawaiian Islands. Contains
              many archaic terms and historical usage.
            </p>
          </div>

          <div className="card p-5">
            <div className="flex items-center gap-2 mb-2">
              <SourceBadge source="EH" />
              <h3 className="font-semibold text-foreground">English-Hawaiian Section</h3>
            </div>
            <p className="text-sm text-muted leading-relaxed">
              The English-Hawaiian section from the Pukui &amp; Elbert dictionary, providing
              reverse lookup from English terms to their Hawaiian equivalents. Contains
              approximately 20,700 entries with translations.
            </p>
          </div>

          <div className="card p-5">
            <div className="flex items-center gap-2 mb-2">
              <SourceBadge source="Other" />
              <h3 className="font-semibold text-foreground">Additional Sources</h3>
            </div>
            <p className="text-sm text-muted leading-relaxed">
              Supplementary material from Parker&apos;s Hawaiian-English Dictionary, place name
              references, and other historical and linguistic resources compiled in
              Trussel&apos;s Combined Hawaiian Dictionary.
            </p>
          </div>
        </div>

        <h2 className="text-2xl font-bold mb-4">Credits</h2>
        <div className="card p-6">
          <p className="text-muted leading-relaxed mb-4">
            The Combined Hawaiian Dictionary was compiled by <strong>Kepano Trussel</strong>,
            who painstakingly merged multiple dictionary sources into a single unified reference.
            His work has been an invaluable resource for the Hawaiian language community.
          </p>
          <p className="text-muted leading-relaxed">
            This digital interface is an independent project that aims to provide a modern,
            searchable, and accessible way to explore the wealth of information in the
            Combined Hawaiian Dictionary. It is not affiliated with or endorsed by the
            original authors of the source dictionaries.
          </p>
        </div>
      </div>
    </div>
  );
}
