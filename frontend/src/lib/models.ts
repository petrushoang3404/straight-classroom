export type PaginatedResponse<T> = {
  items: T[]
  limit: number
  offset: number
  total: number
}

export type ClassroomSummary = {
  id: number
  name: string
  location: string
}

export type TeacherSummary = {
  id: number
  name: string
  subject: string
}

export type Classroom = {
  id: number
  name: string
  capacity: number
  location: string
  teachers: TeacherSummary[]
}

export type Teacher = {
  id: number
  name: string
  subject: string
  classrooms: ClassroomSummary[]
}

export type Student = {
  id: number
  saint_name: string
  first_name: string
  last_name: string
  division: string
  classroom_id: number
  classroom: ClassroomSummary
}
