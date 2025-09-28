"use client"

import React, { useState } from "react"

export type EmojiRatingProps = {
  value?: number
  defaultValue?: number
  onChange?: (value: number) => void
  sizeClass?: string
  readOnly?: boolean
  name?: string
}

const EMOJIS = ["😞", "😕", "😐", "🙂", "😄"]
const LABELS = ["FOMO", "Greed", "Neutral", "Confident", "Excited"]

export default function EmojiRating({
  value,
  defaultValue = 0,
  onChange,
  sizeClass = "text-2xl",
  readOnly = false,
  name = "emoji-rating",
}: EmojiRatingProps) {
  const [internal, setInternal] = useState<number>(defaultValue)
  const [hover, setHover] = useState<number | null>(null)

  const current = typeof value === "number" ? value : internal

  function setRating(v: number) {
    if (readOnly) return
    if (typeof value !== "number") setInternal(v)
    onChange?.(v)
  }

  return (
    <div role="radiogroup" aria-label="Emoji rating" className="flex flex-row  justify-between items-center gap-4">
      {EMOJIS.map((emoji, i) => {
        const idx = i + 1
        const isActive = hover != null ? idx <= hover : idx <= current
        return (
          <div key={emoji} className="relative flex flex-col items-center">
            <button
              type="button"
              role="radio"
              aria-checked={current === idx}
              aria-label={`${LABELS[i]} (${idx}/5)`}
              name={name}
              onClick={() => setRating(idx)}
              onMouseEnter={() => setHover(idx)}
              onMouseLeave={() => setHover(null)}
              onFocus={() => setHover(idx)}
              onBlur={() => setHover(null)}
              className={`
                ${sizeClass}
                rounded-md
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-400
                transition-transform
                ${isActive ? "scale-110" : "scale-100"}
                ${readOnly ? "cursor-default" : "cursor-pointer"}
              `}
              aria-disabled={readOnly}
            >
              <span aria-hidden="true">{emoji}</span>
            </button>

            {/* Label tooltip */}
            <span
              className={`
                absolute top-full mt-1 px-2 py-1 text-sm rounded-md bg-gray-800 text-white
                whitespace-nowrap transition-opacity
                ${hover === idx ? "opacity-100" : "opacity-0"}
              `}
            >
              {LABELS[i]}
            </span>
          </div>
        )
      })}
    </div>
  )
}
