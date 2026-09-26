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
  division: string
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
  division: string
  classrooms: ClassroomSummary[]
  saint_name: string | null
  date_of_birth: string | null
  place_of_birth: string | null
  feast_day: string | null
  phone_number: string | null
  address: string | null
}

export type Student = {
  id: number
  saint_name: string
  first_name: string
  last_name: string
  division: string
  classroom_id: number
  classroom: ClassroomSummary
  date_of_birth: string | null
  place_of_birth: string | null
  date_of_baptism: string | null
  place_of_baptism: string | null
  date_of_first_communion: string | null
  place_of_first_communion: string | null
  date_of_confirmation: string | null
  place_of_confirmation: string | null
  father_name: string | null
  father_phone_number: string | null
  mother_name: string | null
  mother_phone_number: string | null
  address: string | null
}

export type ClassroomInput = Pick<Classroom, "name" | "capacity" | "location">

export type TeacherInput = Pick<Teacher, "name" | "division">

export type StudentInput = Pick<
  Student,
  "saint_name" | "first_name" | "last_name" | "division" | "classroom_id"
>

export type Material = {
  id: number
  classroom_id: number
  description: string | null
  filename: string
  content_type: string
  size_bytes: number
  created_at: string
}
