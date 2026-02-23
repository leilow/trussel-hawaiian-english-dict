export default function ReferencesPage() {
  const generalRefs = [
    { abbr: "PE", text: 'Pukui, Mary Kawena, and Samuel H. Elbert. Hawaiian Dictionary: Hawaiian-English, English-Hawaiian. Revised and Enlarged Edition. Honolulu: University of Hawaiʻi Press, 1986.' },
    { abbr: "MK", text: 'Komike Huaʻolelo, Hale Kuamoʻo, ʻAha Pūnana Leo. Māmaka Kaiao: A Modern Hawaiian Vocabulary. Honolulu: University of Hawaiʻi Press, 2003.' },
    { abbr: "And.", text: 'Andrews, Lorrin. A Dictionary of the Hawaiian Language, to Which Is Appended an English-Hawaiian Vocabulary. Honolulu: Henry M. Whitney, 1865.' },
    { abbr: "Par.", text: 'Parker, Henry H. A Dictionary of the Hawaiian Language. Honolulu: Board of Commissioners of Public Archives of the Territory of Hawaii, 1922.' },
    { abbr: "CHD", text: 'Trussel, Kepano. Combined Hawaiian Dictionary. trussel2.com/HAW/. Web resource combining multiple Hawaiian dictionary sources.' },
  ];

  const biblicalRefs = [
    { abbr: "Kin.", text: 'Kinohi (Genesis). Ka Baibala Hemolele. Honolulu: American Bible Society, 1868.' },
    { abbr: "Mat.", text: 'Mataio (Matthew). Ka Baibala Hemolele. Honolulu: American Bible Society, 1868.' },
    { abbr: "Hal.", text: 'Halelu (Psalms). Ka Baibala Hemolele. Honolulu: American Bible Society, 1868.' },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-8">References &amp; Bibliography</h1>

      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-6">General References</h2>
        <div className="space-y-4">
          {generalRefs.map((ref) => (
            <div key={ref.abbr} className="card p-4">
              <span className="font-mono font-bold text-accent text-sm mr-3">{ref.abbr}</span>
              <span className="text-muted text-sm leading-relaxed">{ref.text}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-6">Biblical References</h2>
        <div className="space-y-4">
          {biblicalRefs.map((ref) => (
            <div key={ref.abbr} className="card p-4">
              <span className="font-mono font-bold text-accent text-sm mr-3">{ref.abbr}</span>
              <span className="text-muted text-sm leading-relaxed">{ref.text}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
