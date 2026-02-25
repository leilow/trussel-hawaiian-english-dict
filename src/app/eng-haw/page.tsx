import { EnglishLetterNav } from "@/components/shared";

export default function EngHawPage() {
  return (
    <>
      <h1>English-Hawaiian: Browse by Letter</h1>
      <p className="muted">Select a letter to browse English-Hawaiian entries.</p>
      <EnglishLetterNav basePath="/eng-haw" />
    </>
  );
}
