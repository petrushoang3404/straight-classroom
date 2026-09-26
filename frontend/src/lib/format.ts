const vietnameseDateFormatter = new Intl.DateTimeFormat("vi-VN", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
})

export function formatDate(value: string | null | undefined) {
  if (!value) return null

  const [year, month, day] = value.split("-").map(Number)
  if (!year || !month || !day) return value

  const date = new Date(year, month - 1, day)
  return Number.isNaN(date.getTime()) ? value : vietnameseDateFormatter.format(date)
}

const vietnameseDateTimeFormatter = new Intl.DateTimeFormat("vi-VN", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
})

// Unlike formatDate, this takes a full ISO timestamp (e.g. a material's
// created_at) rather than a date-only string.
export function formatDateTime(value: string | null | undefined) {
  if (!value) return null

  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? value
    : vietnameseDateTimeFormatter.format(date)
}

export function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${Math.round(size / 1024)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}
