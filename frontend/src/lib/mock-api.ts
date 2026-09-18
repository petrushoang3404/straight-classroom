import type { AxiosInstance } from "axios"
import MockAdapter from "axios-mock-adapter"

import type { Classroom, Student, Teacher } from "./models"

const classrooms: Classroom[] = [
  { id: 1, name: "Khai Tâm A", capacity: 28, location: "Phòng Gioan" },
  { id: 2, name: "Rước Lễ 1", capacity: 32, location: "Phòng Luca" },
  { id: 3, name: "Thêm Sức 2", capacity: 30, location: "Phòng Marco" },
  { id: 4, name: "Bao Đồng", capacity: 24, location: "Hội trường nhỏ" },
]

const teachers: Teacher[] = [
  { id: 1, name: "Anna Nguyễn Minh", subject: "Giáo lý căn bản" },
  { id: 2, name: "Phêrô Trần Hoàng", subject: "Kinh Thánh" },
  { id: 3, name: "Maria Lê Hạnh", subject: "Phụng vụ" },
  { id: 4, name: "Giuse Phạm Quốc", subject: "Sinh hoạt thiếu nhi" },
]

const students: Student[] = [
  {
    id: 1,
    saint_name: "Maria",
    first_name: "An",
    last_name: "Nguyễn",
    division: "Ấu nhi",
    classroom_id: 1,
  },
  {
    id: 2,
    saint_name: "Giuse",
    first_name: "Bảo",
    last_name: "Trần",
    division: "Thiếu nhi",
    classroom_id: 2,
  },
  {
    id: 3,
    saint_name: "Têrêsa",
    first_name: "Chi",
    last_name: "Lê",
    division: "Nghĩa sĩ",
    classroom_id: 3,
  },
  {
    id: 4,
    saint_name: "Phêrô",
    first_name: "Đức",
    last_name: "Phạm",
    division: "Hiệp sĩ",
    classroom_id: 4,
  },
]

export function setupMockApi(client: AxiosInstance) {
  const mock = new MockAdapter(client, { delayResponse: 250 })

  mock.onGet("/classrooms/").reply((config) => {
    return [200, listResponse(classrooms, config.params)]
  })
  mock.onGet(/\/classrooms\/\d+$/).reply((config) => {
    return itemResponse(classrooms, config.url)
  })

  mock.onGet("/teachers/").reply((config) => {
    return [200, listResponse(teachers, config.params, "teacher_name", teacherSearch)]
  })
  mock.onGet(/\/teachers\/\d+$/).reply((config) => {
    return itemResponse(teachers, config.url)
  })

  mock.onGet("/students/").reply((config) => {
    return [200, listResponse(students, config.params, "student_name", studentSearch)]
  })
  mock.onGet(/\/students\/\d+$/).reply((config) => {
    return itemResponse(students, config.url)
  })
}

function listResponse<T>(
  rows: T[],
  params: Record<string, unknown> = {},
  searchKey?: string,
  search?: (item: T, term: string) => boolean
) {
  const limit = Number(params.limit ?? 20)
  const offset = Number(params.offset ?? 0)
  const term = searchKey ? String(params[searchKey] ?? "").toLowerCase() : ""
  const filteredRows = term && search ? rows.filter((item) => search(item, term)) : rows
  const items = filteredRows.slice(offset, offset + limit)

  return {
    items,
    limit,
    offset,
    total: filteredRows.length,
  }
}

function itemResponse<T extends { id: number }>(rows: T[], url = "") {
  const id = Number(url.split("/").filter(Boolean).at(-1))
  const item = rows.find((row) => row.id === id)

  return item
    ? ([200, item] as [number, T])
    : ([404, { detail: "Not found" }] as [number, { detail: string }])
}

function teacherSearch(teacher: Teacher, term: string) {
  return `${teacher.name} ${teacher.subject}`.toLowerCase().includes(term)
}

function studentSearch(student: Student, term: string) {
  return `${student.saint_name} ${student.first_name} ${student.last_name} ${student.division}`
    .toLowerCase()
    .includes(term)
}
