import { HawaiianLetterNav } from "@/components/shared";

export default function BrowsePage() {
  return (
    <>
      <h1>Hawaiian-English: Browse by Letter</h1>
      <p className="muted">Select a letter to browse entries.</p>
      <HawaiianLetterNav basePath="/browse" />
    </>
  );
}
