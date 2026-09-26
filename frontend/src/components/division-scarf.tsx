import type { Scarf } from "@/lib/divisions"
import { cn } from "@/lib/utils"

/**
 * The khăn quàng itself: the folded scarf with its cross, drawn in the ngành's
 * two colours. Showing the colour as the object it belongs to keeps pale
 * scarves (Chiên Con) readable, which colouring text with them would not.
 */
export function ScarfMark({
  className,
  scarf,
}: {
  className?: string
  scarf: Scarf
}) {
  return (
    <svg
      aria-hidden="true"
      className={cn("size-5", className)}
      fill="none"
      viewBox="0 0 24 24"
    >
      <path d="M1 4h22L12 21Z" fill={scarf.scarf} />
      <path
        d="M10.4 7.4h3.2v1.1h1.1v3.2h-1.1v1.1h-3.2v-1.1H9.3V8.5h1.1Z"
        fill={scarf.emblem}
      />
    </svg>
  )
}

/**
 * The ngành's name next to its scarf. The label stays in the normal text
 * colour; the scarf carries the colour, so every ngành reads the same way.
 */
export function ScarfBadge({
  className,
  label,
  scarf,
}: {
  className?: string
  label?: string
  scarf: Scarf
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-sm font-medium",
        className
      )}
      style={{
        backgroundColor: `color-mix(in oklab, ${scarf.scarf} 22%, var(--card))`,
        borderColor: `color-mix(in oklab, ${scarf.scarf} 55%, var(--card))`,
      }}
    >
      <ScarfMark className="size-4" scarf={scarf} />
      {label ?? scarf.label}
    </span>
  )
}
