import type { Classroom } from "@/lib/models"

/**
 * The five ngành (divisions) and the colours of their khăn quàng.
 *
 * `scarf` is the colour of the scarf itself and `emblem` the colour of the
 * cross on it, taken from the parish's own reference sheet. They are fixed
 * brand colours, not theme tokens, so they are written as plain hex.
 */
export type Scarf = {
  label: string
  scarf: string
  emblem: string
}

export const DIVISION_SCARVES: Scarf[] = [
  { label: "Chiên Con", scarf: "#FEE1ED", emblem: "#D43126" },
  { label: "Ấu Nhi", scarf: "#41AD49", emblem: "#FFF112" },
  { label: "Thiếu Nhi", scarf: "#0260A2", emblem: "#FFF112" },
  { label: "Nghĩa Sĩ", scarf: "#FFF112", emblem: "#DB0810" },
  { label: "Hiệp Sĩ", scarf: "#843905", emblem: "#FFF112" },
]

/** Huynh Trưởng wear the red scarf whichever ngành they lead. */
export const LEADER_SCARF: Scarf = {
  label: "Huynh Trưởng",
  scarf: "#DB0810",
  emblem: "#FFF112",
}

export const DIVISION_LABELS = DIVISION_SCARVES.map((entry) => entry.label)

/** `Nghĩa Sĩ` and `nghia si` are the same ngành to a volunteer typing it in. */
function compareKey(value: string) {
  return value
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .trim()
}

/**
 * Find the scarf for a ngành, or for anything that starts with one: both
 * `Nghĩa sĩ` and the classroom name `Nghĩa Sĩ 1A` resolve to the same entry,
 * and so does a shortened `Chiên 2A`, since no two ngành share a first word.
 */
export function scarfForDivision(value: string | null | undefined): Scarf | null {
  if (!value) return null
  const key = compareKey(value)
  if (!key) return null

  return (
    DIVISION_SCARVES.find((entry) => {
      const entryKey = compareKey(entry.label)
      return key === entryKey || key.startsWith(`${entryKey} `)
    }) ??
    DIVISION_SCARVES.find(
      (entry) => key.split(" ")[0] === compareKey(entry.label).split(" ")[0]
    ) ??
    null
  )
}

/**
 * A classroom has no ngành of its own, so read it from the name (`Nghĩa Sĩ
 * 1A`), falling back to what its Huynh Trưởng are assigned to.
 */
export function scarfForClassroom(classroom: Classroom): Scarf | null {
  const fromName = scarfForDivision(classroom.name)
  if (fromName) return fromName

  for (const teacher of classroom.teachers) {
    const fromTeacher = scarfForDivision(teacher.division)
    if (fromTeacher) return fromTeacher
  }
  return null
}
