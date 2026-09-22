import type { AxiosInstance } from "axios"
import MockAdapter from "axios-mock-adapter"

import type {
  Classroom,
  ClassroomSummary,
  Student,
  Teacher,
  TeacherSummary,
} from "./models"

type ClassroomBase = Omit<Classroom, "teachers">
type TeacherBase = Omit<Teacher, "classrooms">
type StudentBase = Omit<Student, "classroom">

const classroomsBase: ClassroomBase[] = [
  { id: 1, name: "Khai Tâm A", capacity: 28, location: "Phòng Gioan" },
  { id: 2, name: "Rước Lễ 1", capacity: 32, location: "Phòng Luca" },
  { id: 3, name: "Thêm Sức 2", capacity: 30, location: "Phòng Marco" },
  { id: 4, name: "Bao Đồng", capacity: 24, location: "Hội trường nhỏ" },
]

const teachersBase: TeacherBase[] = [
  { id: 1, name: "Anna Nguyễn Minh", subject: "Giáo lý căn bản" },
  { id: 2, name: "Phêrô Trần Hoàng", subject: "Kinh Thánh" },
  { id: 3, name: "Maria Lê Hạnh", subject: "Phụng vụ" },
  { id: 4, name: "Giuse Phạm Quốc", subject: "Sinh hoạt thiếu nhi" },
]

// Many-to-many classroom <-> teacher assignments, mutated by the assign/unassign mocks.
const assignments: { classroomId: number; teacherId: number }[] = [
  { classroomId: 1, teacherId: 1 },
  { classroomId: 2, teacherId: 2 },
  { classroomId: 3, teacherId: 3 },
  { classroomId: 4, teacherId: 4 },
  { classroomId: 4, teacherId: 1 },
]

const studentsBase: StudentBase[] = [
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

function classroomSummary(classroomId: number): ClassroomSummary {
  const classroom = classroomsBase.find((item) => item.id === classroomId)
  return classroom
    ? { id: classroom.id, name: classroom.name, location: classroom.location }
    : { id: classroomId, name: "Không rõ", location: "—" }
}

function teacherSummary(teacherId: number): TeacherSummary {
  const teacher = teachersBase.find((item) => item.id === teacherId)
  return teacher
    ? { id: teacher.id, name: teacher.name, subject: teacher.subject }
    : { id: teacherId, name: "Không rõ", subject: "—" }
}

function getClassrooms(): Classroom[] {
  return classroomsBase.map((classroom) => ({
    ...classroom,
    teachers: assignments
      .filter((link) => link.classroomId === classroom.id)
      .map((link) => teacherSummary(link.teacherId)),
  }))
}

function getTeachers(): Teacher[] {
  return teachersBase.map((teacher) => ({
    ...teacher,
    classrooms: assignments
      .filter((link) => link.teacherId === teacher.id)
      .map((link) => classroomSummary(link.classroomId)),
  }))
}

function getStudents(): Student[] {
  return studentsBase.map((student) => ({
    ...student,
    classroom: classroomSummary(student.classroom_id),
  }))
}

export function setupMockApi(client: AxiosInstance) {
  const mock = new MockAdapter(client, { delayResponse: 250 })

  mock.onPost("/auth/login").reply((config) => {
    const credentials = JSON.parse(config.data || "{}") as {
      username?: string
      password?: string
    }
    const username = credentials.username?.trim()
    const password = credentials.password?.trim()

    if (!username || !password) {
      return [400, { detail: "Username and password are required" }]
    }

    return [
      200,
      {
        token: "mock-session-token",
        username,
        displayName: displayNameFromUsername(username),
        provider: "password",
      },
    ]
  })

  mock.onPost("/auth/google").reply(200, {
    token: "mock-google-session-token",
    username: "google.user@straight-classroom.local",
    displayName: "Google User",
    provider: "google",
  })

  mock.onGet("/classrooms/").reply((config) => {
    return [200, listResponse(getClassrooms(), config.params)]
  })
  mock.onGet(/\/classrooms\/\d+$/).reply((config) => {
    return itemResponse(getClassrooms(), config.url)
  })
  mock.onGet(/\/classrooms\/\d+\/students$/).reply((config) => {
    const classroomId = idFromUrl(config.url, -2)
    const rows = getStudents().filter(
      (student) => student.classroom_id === classroomId
    )
    return [200, listResponse(rows, config.params)]
  })
  mock.onGet(/\/classrooms\/\d+\/teachers$/).reply((config) => {
    const classroomId = idFromUrl(config.url, -2)
    const classroom = getClassrooms().find((item) => item.id === classroomId)
    return classroom
      ? [200, classroom.teachers]
      : [404, { detail: "Classroom not found" }]
  })
  mock.onPost(/\/classrooms\/\d+\/teachers$/).reply((config) => {
    const classroomId = idFromUrl(config.url, -2)
    const { teacher_id: teacherId } = JSON.parse(config.data || "{}") as {
      teacher_id?: number
    }
    if (!classroomsBase.some((item) => item.id === classroomId)) {
      return [404, { detail: "Classroom not found" }]
    }
    if (!teacherId || !teachersBase.some((item) => item.id === teacherId)) {
      return [404, { detail: "Teacher not found" }]
    }
    if (
      assignments.some(
        (link) => link.classroomId === classroomId && link.teacherId === teacherId
      )
    ) {
      return [409, { detail: "Teacher is already assigned to this classroom" }]
    }
    assignments.push({ classroomId, teacherId })
    const classroom = getClassrooms().find((item) => item.id === classroomId)
    return [201, classroom]
  })
  mock.onDelete(/\/classrooms\/\d+\/teachers\/\d+$/).reply((config) => {
    const classroomId = idFromUrl(config.url, -2)
    const teacherId = idFromUrl(config.url, -1)
    const index = assignments.findIndex(
      (link) => link.classroomId === classroomId && link.teacherId === teacherId
    )
    if (index === -1) {
      return [404, { detail: "Teacher is not assigned to this classroom" }]
    }
    assignments.splice(index, 1)
    return [204]
  })

  mock.onGet("/teachers/").reply((config) => {
    return [
      200,
      listResponse(getTeachers(), config.params, "teacher_name", teacherSearch),
    ]
  })
  mock.onGet(/\/teachers\/\d+$/).reply((config) => {
    return itemResponse(getTeachers(), config.url)
  })
  mock.onGet(/\/teachers\/\d+\/classrooms$/).reply((config) => {
    const teacherId = idFromUrl(config.url, -2)
    const teacher = getTeachers().find((item) => item.id === teacherId)
    return teacher
      ? [200, teacher.classrooms]
      : [404, { detail: "Teacher not found" }]
  })

  mock.onGet("/students/").reply((config) => {
    const params = config.params ?? {}
    const classroomId = params.classroom_id ? Number(params.classroom_id) : undefined
    const rows = classroomId
      ? getStudents().filter((student) => student.classroom_id === classroomId)
      : getStudents()
    return [200, listResponse(rows, params, "student_name", studentSearch)]
  })
  mock.onGet(/\/students\/\d+$/).reply((config) => {
    return itemResponse(getStudents(), config.url)
  })
}

function idFromUrl(url = "", fromEnd: number): number {
  const segments = url.split("/").filter(Boolean)
  return Number(segments.at(fromEnd))
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

function displayNameFromUsername(username: string) {
  return username
    .split(/[.@_-]/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ")
}
