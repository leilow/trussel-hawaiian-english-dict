"use client";

import { useState } from "react";

export function FavoriteButton() {
  const [favorited, setFavorited] = useState(false);

  return (
    <button
      onClick={() => setFavorited(!favorited)}
      className="p-2 rounded-md text-muted hover:text-foreground transition-colors cursor-pointer"
      aria-label={favorited ? "Remove from favorites" : "Add to favorites"}
    >
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill={favorited ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
      </svg>
    </button>
  );
}
