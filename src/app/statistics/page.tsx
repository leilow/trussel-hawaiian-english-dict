"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const stats = [
  { label: "Entries", value: "59,417" },
  { label: "Definitions", value: "69,847" },
  { label: "Examples", value: "16,769" },
  { label: "Concordance", value: "133,684" },
  { label: "Cross-refs", value: "16,129" },
  { label: "Etymologies", value: "2,637" },
];

const sourceData = [
  { source: "PE", entries: 42000 },
  { source: "MK", entries: 8500 },
  { source: "Andrews", entries: 5200 },
  { source: "EH", entries: 2800 },
  { source: "Other", entries: 917 },
];

export default function StatisticsPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-8">Statistics</h1>

      {/* Big Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-12">
        {stats.map((stat) => (
          <div key={stat.label} className="card p-5 text-center">
            <div className="text-2xl sm:text-3xl font-bold text-foreground mb-1">
              {stat.value}
            </div>
            <div className="font-mono text-xs uppercase tracking-wider text-muted">
              {stat.label}
            </div>
          </div>
        ))}
      </div>

      {/* Entries by Source */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-6">Entries by Source</h2>
        <div className="card p-6">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sourceData} layout="vertical" margin={{ left: 60 }}>
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis
                  type="category"
                  dataKey="source"
                  tick={{ fontSize: 12, fontFamily: "var(--font-redhat-mono), monospace" }}
                />
                <Tooltip
                  formatter={(value) => [Number(value).toLocaleString(), "Entries"]}
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--card-border)",
                    borderRadius: "0.5rem",
                    fontSize: "0.875rem",
                  }}
                />
                <Bar dataKey="entries" fill="var(--accent)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Letter Distribution */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-6">Letter Distribution</h2>
        <div className="card p-6 text-center text-muted">
          Chart coming soon
        </div>
      </section>
    </div>
  );
}
