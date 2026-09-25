import type { AxiosInstance } from "axios"
import MockAdapter from "axios-mock-adapter"

import type {
  Classroom,
  ClassroomInput,
  ClassroomSummary,
  Student,
  StudentInput,
  Teacher,
  TeacherInput,
  TeacherSummary,
} from "./models"

type ClassroomBase = Omit<Classroom, "teachers">
type TeacherBase = Pick<Teacher, "id" | "name" | "division"> &
  Partial<
    Pick<
      Teacher,
      | "saint_name"
      | "date_of_birth"
      | "place_of_birth"
      | "feast_day"
      | "phone_number"
      | "address"
    >
  >
type StudentBase = Pick<
  Student,
  "id" | "saint_name" | "first_name" | "last_name" | "division" | "classroom_id"
> &
  Partial<
    Pick<
      Student,
      | "date_of_birth"
      | "place_of_birth"
      | "date_of_baptism"
      | "place_of_baptism"
      | "date_of_first_communion"
      | "place_of_first_communion"
      | "date_of_confirmation"
      | "place_of_confirmation"
      | "father_name"
      | "father_phone_number"
      | "mother_name"
      | "mother_phone_number"
      | "address"
    >
  >

const classroomsBase: ClassroomBase[] = [
  { id: 1, name: "Khai Tâm A", capacity: 28, location: "Phòng Gioan" },
  { id: 2, name: "Rước Lễ 1", capacity: 32, location: "Phòng Luca" },
  { id: 3, name: "Thêm Sức 2", capacity: 30, location: "Phòng Marco" },
  { id: 4, name: "Bao Đồng", capacity: 24, location: "Hội trường nhỏ" },
]

const teachersBase: TeacherBase[] = [
  {
    id: 1,
    name: "Anna Nguyễn Minh",
    division: "Giáo lý căn bản",
    saint_name: "Anna",
    date_of_birth: "1991-03-12",
    place_of_birth: "TP. Hồ Chí Minh",
    feast_day: "26/07",
    phone_number: "090 123 45 67",
    address: "12 Nguyễn Văn Trỗi, Phường 7, Quận 3, TP. Hồ Chí Minh",
  },
  { id: 2, name: "Phêrô Trần Hoàng", division: "Kinh Thánh" },
  { id: 3, name: "Maria Lê Hạnh", division: "Phụng vụ" },
  { id: 4, name: "Giuse Phạm Quốc", division: "Sinh hoạt thiếu nhi" },
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
    date_of_birth: "2017-05-14",
    place_of_birth: "TP. Hồ Chí Minh",
    date_of_baptism: "2017-12-17",
    place_of_baptism: "Nhà thờ Chúa Thánh Thể",
    date_of_first_communion: "2024-04-21",
    place_of_first_communion: "Nhà thờ Chúa Thánh Thể",
    date_of_confirmation: null,
    place_of_confirmation: null,
    father_name: "Nguyễn Văn An",
    father_phone_number: "090 234 56 78",
    mother_name: "Trần Thị Bích",
    mother_phone_number: "091 345 67 89",
    address: "45 Nguyễn Đình Chiểu, Phường 5, Quận 3, TP. Hồ Chí Minh",
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
    ? { id: teacher.id, name: teacher.name, division: teacher.division }
    : { id: teacherId, name: "Không rõ", division: "—" }
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
    saint_name: null,
    date_of_birth: null,
    place_of_birth: null,
    feast_day: null,
    phone_number: null,
    address: null,
    ...teacher,
    classrooms: assignments
      .filter((link) => link.teacherId === teacher.id)
      .map((link) => classroomSummary(link.classroomId)),
  }))
}

function getStudents(): Student[] {
  return studentsBase.map((student) => ({
    date_of_birth: null,
    place_of_birth: null,
    date_of_baptism: null,
    place_of_baptism: null,
    date_of_first_communion: null,
    place_of_first_communion: null,
    date_of_confirmation: null,
    place_of_confirmation: null,
    father_name: null,
    father_phone_number: null,
    mother_name: null,
    mother_phone_number: null,
    address: null,
    ...student,
    classroom: classroomSummary(student.classroom_id),
  }))
}

function getClassroom(id: number): Classroom {
  const classroom = getClassrooms().find((item) => item.id === id)
  if (!classroom) throw new Error(`Mock classroom ${id} not found`)
  return classroom
}

function getTeacher(id: number): Teacher {
  const teacher = getTeachers().find((item) => item.id === id)
  if (!teacher) throw new Error(`Mock teacher ${id} not found`)
  return teacher
}

function getStudent(id: number): Student {
  const student = getStudents().find((item) => item.id === id)
  if (!student) throw new Error(`Mock student ${id} not found`)
  return student
}

function requestPayload<T>(data: unknown): T {
  if (typeof data === "object" && data !== null) {
    return data as T
  }

  if (typeof data !== "string" || !data) {
    return {} as T
  }

  try {
    return JSON.parse(data) as T
  } catch {
    return {} as T
  }
}

function isRequiredString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0 && value.length <= 255
}

function isValidClassroom(value: Partial<ClassroomBase>): value is ClassroomBase {
  return (
    isRequiredString(value.name) &&
    isRequiredString(value.location) &&
    typeof value.capacity === "number" &&
    Number.isInteger(value.capacity) &&
    value.capacity > 0
  )
}

function isValidTeacher(value: Partial<TeacherBase>): value is TeacherBase {
  return isRequiredString(value.name) && isRequiredString(value.division)
}

function isValidStudent(value: Partial<StudentBase>): value is StudentBase {
  return (
    isRequiredString(value.saint_name) &&
    isRequiredString(value.first_name) &&
    isRequiredString(value.last_name) &&
    isRequiredString(value.division) &&
    typeof value.classroom_id === "number" &&
    Number.isInteger(value.classroom_id) &&
    value.classroom_id > 0
  )
}

function nextId(rows: Array<{ id: number }>) {
  return Math.max(0, ...rows.map(({ id }) => id)) + 1
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
        role: username.toLowerCase().includes("teacher") ? "teacher" : "admin",
      },
    ]
  })

  mock.onPost("/auth/google").reply(200, {
    token: "mock-google-session-token",
    username: "google.user@straight-classroom.local",
    displayName: "Google User",
    provider: "google",
    role: "admin",
  })

  mock.onGet("/classrooms/").reply((config) => {
    return [200, listResponse(getClassrooms(), config.params)]
  })
  mock.onGet(/\/classrooms\/\d+$/).reply((config) => {
    return itemResponse(getClassrooms(), config.url)
  })
  mock.onPost("/classrooms/").reply((config) => {
    const payload = requestPayload<ClassroomInput>(config.data)
    if (!isValidClassroom(payload)) {
      return [422, { detail: "Invalid classroom data" }]
    }

    const classroom: ClassroomBase = {
      id: nextId(classroomsBase),
      name: payload.name,
      capacity: payload.capacity,
      location: payload.location,
    }
    classroomsBase.push(classroom)
    return [201, getClassroom(classroom.id)]
  })
  mock.onPatch(/\/classrooms\/\d+$/).reply((config) => {
    const classroomId = idFromUrl(config.url, -1)
    const classroomIndex = classroomsBase.findIndex(
      (classroom) => classroom.id === classroomId
    )
    if (classroomIndex === -1) {
      return [404, { detail: "Classroom not found" }]
    }

    const payload = requestPayload<Partial<ClassroomInput>>(config.data)
    if (Object.keys(payload).length === 0) {
      return [400, { detail: "At least one field must be provided" }]
    }

    const current = classroomsBase[classroomIndex]
    const updated: ClassroomBase = {
      ...current,
      ...(payload.name !== undefined ? { name: payload.name } : {}),
      ...(payload.capacity !== undefined ? { capacity: payload.capacity } : {}),
      ...(payload.location !== undefined ? { location: payload.location } : {}),
    }
    if (!isValidClassroom(updated)) {
      return [422, { detail: "Invalid classroom data" }]
    }

    classroomsBase[classroomIndex] = updated
    return [200, getClassroom(updated.id)]
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
  mock.onPost("/teachers/").reply((config) => {
    const payload = requestPayload<TeacherInput>(config.data)
    if (!isValidTeacher(payload)) {
      return [422, { detail: "Invalid teacher data" }]
    }

    const teacher: TeacherBase = {
      id: nextId(teachersBase),
      name: payload.name,
      division: payload.division,
    }
    teachersBase.push(teacher)
    return [201, getTeacher(teacher.id)]
  })
  mock.onPatch(/\/teachers\/\d+$/).reply((config) => {
    const teacherId = idFromUrl(config.url, -1)
    const teacherIndex = teachersBase.findIndex((teacher) => teacher.id === teacherId)
    if (teacherIndex === -1) {
      return [404, { detail: "Teacher not found" }]
    }

    const payload = requestPayload<Partial<TeacherInput>>(config.data)
    if (Object.keys(payload).length === 0) {
      return [400, { detail: "No updates provided" }]
    }

    const current = teachersBase[teacherIndex]
    const updated: TeacherBase = {
      ...current,
      ...(payload.name !== undefined ? { name: payload.name } : {}),
      ...(payload.division !== undefined ? { division: payload.division } : {}),
    }
    if (!isValidTeacher(updated)) {
      return [422, { detail: "Invalid teacher data" }]
    }

    teachersBase[teacherIndex] = updated
    return [200, getTeacher(updated.id)]
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
  mock.onPost("/students/").reply((config) => {
    const payload = requestPayload<StudentInput>(config.data)
    if (!isValidStudent(payload) || !classroomsBase.some((item) => item.id === payload.classroom_id)) {
      return [422, { detail: "Invalid student data" }]
    }

    const student: StudentBase = {
      id: nextId(studentsBase),
      saint_name: payload.saint_name,
      first_name: payload.first_name,
      last_name: payload.last_name,
      division: payload.division,
      classroom_id: payload.classroom_id,
    }
    studentsBase.push(student)
    return [201, getStudent(student.id)]
  })
  mock.onPatch(/\/students\/\d+$/).reply((config) => {
    const studentId = idFromUrl(config.url, -1)
    const studentIndex = studentsBase.findIndex((student) => student.id === studentId)
    if (studentIndex === -1) {
      return [404, { detail: "Student not found" }]
    }

    const payload = requestPayload<Partial<StudentInput>>(config.data)
    if (Object.keys(payload).length === 0) {
      return [400, { detail: "No updates provided" }]
    }

    const current = studentsBase[studentIndex]
    const updated: StudentBase = {
      ...current,
      ...(payload.saint_name !== undefined ? { saint_name: payload.saint_name } : {}),
      ...(payload.first_name !== undefined ? { first_name: payload.first_name } : {}),
      ...(payload.last_name !== undefined ? { last_name: payload.last_name } : {}),
      ...(payload.division !== undefined ? { division: payload.division } : {}),
      ...(payload.classroom_id !== undefined
        ? { classroom_id: payload.classroom_id }
        : {}),
    }
    if (
      !isValidStudent(updated) ||
      !classroomsBase.some((item) => item.id === updated.classroom_id)
    ) {
      return [422, { detail: "Invalid student data" }]
    }

    studentsBase[studentIndex] = updated
    return [200, getStudent(updated.id)]
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
  return `${teacher.name} ${teacher.division}`.toLowerCase().includes(term)
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
