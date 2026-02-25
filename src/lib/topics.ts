/**
 * Mapping from database topic codes to display metadata.
 * The real topical data lives in the uppercase domain codes (ANI, BIR, WIN, etc.)
 * which were tagged from entry definitions. The lowercase names (animals, birds, wind)
 * have very few entries due to a scraper tagging gap.
 *
 * Source: https://www.trussel2.com/HAW/topical.htm
 */

interface TopicMeta {
  display: string;
  description: string;
}

/**
 * Maps uppercase domain codes → display names.
 * Derived from trussel2.com/HAW/topical.htm (50 categories)
 * and the domain codes found in Pukui-Elbert / Māmaka Kaiao definitions.
 */
export const TOPIC_CODE_MAP: Record<string, TopicMeta> = {
  // === Direct matches to trussel2.com topical pages ===
  ANI:     { display: "Animals", description: "Animal names and related terms" },
  BAN:     { display: "Bananas", description: "Banana varieties and cultivation" },
  BIR:     { display: "Birds", description: "Bird species and related terms" },
  BOD:     { display: "Body, Illness", description: "Body parts, illness, and medicine" },
  BSK:     { display: "Basketball", description: "Basketball terminology" },
  BUI:     { display: "Building", description: "Building and construction" },
  CAN:     { display: "Canoes, Watercraft", description: "Canoe parts and watercraft terminology" },
  CLO:     { display: "Clothing", description: "Clothing and adornment" },
  CMP:     { display: "Computer", description: "Modern computer terminology" },
  CN:      { display: "Coconuts", description: "Coconut plant and uses" },
  COL:     { display: "Colors", description: "Color terms" },
  CRA:     { display: "Crabs", description: "Crabs and crustaceans" },
  ECO:     { display: "Economics", description: "Economic and trade terms" },
  EDU:     { display: "Education", description: "Education and learning" },
  FER:     { display: "Ferns", description: "Fern species" },
  FIS:     { display: "Fish, Sea Life", description: "Fish, shellfish, and marine life" },
  FLO:     { display: "Flowers", description: "Flowers and flowering plants" },
  FOO:     { display: "Food", description: "Food, cooking, and eating" },
  G:       { display: "Gazetteer", description: "Place names of Hawaiʻi" },
  GEO:     { display: "Geography", description: "Geographic terms" },
  GOV:     { display: "Government", description: "Government and politics" },
  HOU:     { display: "House", description: "House and dwelling terms" },
  HUL:     { display: "Hula", description: "Hula dance terminology" },
  IDI:     { display: "Idioms", description: "Idiomatic expressions" },
  ILL:     { display: "Illness, Medicine", description: "Illness, disease, and medical terms" },
  INS:     { display: "Insects", description: "Insects and small creatures" },
  KAV:     { display: "Kava", description: "Kava plant and ceremony" },
  LAND:    { display: "Land", description: "Land divisions and geography" },
  LAW:     { display: "Law", description: "Legal and governance terms" },
  LEI:     { display: "Lei", description: "Lei making and materials" },
  LNG:     { display: "Language", description: "Language and linguistic terms" },
  LUA:     { display: "Lua (Fighting)", description: "Lua martial art terminology" },
  MTH:     { display: "Mathematics", description: "Mathematical and numerical terms" },
  MUS:     { display: "Music", description: "Musical instruments and terms" },
  NET:     { display: "Nets", description: "Net fishing terminology" },
  PAN:     { display: "Pandanus", description: "Pandanus plant and weaving" },
  PLA:     { display: "Plants", description: "Plant species and cultivation" },
  POI:     { display: "Poi", description: "Poi preparation and related terms" },
  SCI:     { display: "Science", description: "Scientific terminology" },
  SEA:     { display: "Seaweed", description: "Seaweed and limu species" },
  SPO:     { display: "Sports", description: "Sports and games" },
  STA:     { display: "Stars, Sky", description: "Stars, sky, and celestial bodies" },
  STO:     { display: "Stones", description: "Stones, rocks, and minerals" },
  SUG:     { display: "Sugar Cane", description: "Sugar cane varieties" },
  SWD:     { display: "Swords, Weapons", description: "Weapons and warfare implements" },
  SWP:     { display: "Sweet Potatoes", description: "Sweet potato varieties and cultivation" },
  TAP:     { display: "Tapa", description: "Tapa cloth making" },
  TAR:     { display: "Taro", description: "Taro varieties and cultivation" },
  TII:     { display: "Ti Plant", description: "Ti plant and uses" },
  TOO:     { display: "Tools", description: "Tools and implements" },
  TRE:     { display: "Trees", description: "Tree species" },
  VOL:     { display: "Volcanoes", description: "Volcanic and geological terms" },
  WAR:     { display: "War", description: "Warfare and military terms" },
  WIN:     { display: "Wind, Rain, Clouds", description: "Wind names, rain, weather, and clouds" },

  // === Other tagged categories ===
  AltSpel: { display: "Alternative Spellings", description: "Entries with variant spellings" },
  CAR:     { display: "Carpentry", description: "Carpentry and woodworking" },
  VLB:     { display: "Basic Vocabulary", description: "Core vocabulary words" },
  SKY:     { display: "Sky", description: "Sky and atmospheric terms" },
  SOC:     { display: "Social", description: "Social and kinship terms" },
  PRF:     { display: "Prefixes", description: "Prefix forms and compounds" },
};

/** Returns true if the topic code should be shown on the topics page */
export function isDisplayableTopic(name: string): boolean {
  return name in TOPIC_CODE_MAP;
}

/** Get display name for a topic code */
export function getTopicDisplay(name: string): string {
  return TOPIC_CODE_MAP[name]?.display ?? name;
}

/** Get description for a topic code */
export function getTopicDescription(name: string): string {
  return TOPIC_CODE_MAP[name]?.description ?? "";
}
