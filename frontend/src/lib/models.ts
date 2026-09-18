export type PaginatedResponse<T> = {
  items: T[]
  limit: number
  offset: number
  total: number
}

export type Classroom = {
  id: number
  name: string
  capacity: number
  location: string
}

export type Teacher = {
  id: number
  name: string
  subject: string
}

export type Student = {
  id: number
  saint_name: string
  first_name: string
  last_name: string
  division: string
  classroom_id: number
}
