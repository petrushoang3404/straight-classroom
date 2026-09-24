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
