import axios from "axios"

import type { AuthSession } from "./auth-store"
import type { Classroom, PaginatedResponse, Student, Teacher } from "./models"
import { setupMockApi } from "./mock-api"

export const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api",
  headers: {
    "Content-Type": "application/json",
  },
})

if (import.meta.env.DEV && import.meta.env.VITE_USE_MOCKS !== "false") {
  setupMockApi(client)
}

type ListParams = {
  limit?: number
  offset?: number
  search?: string
}

const listParams = (params: ListParams, searchKey?: string) => ({
  limit: params.limit ?? 20,
  offset: params.offset ?? 0,
  ...(searchKey && params.search ? { [searchKey]: params.search } : {}),
})

function normalizeList<T>(
  data: PaginatedResponse<T> | T[] | undefined,
  fallback: ListParams
): PaginatedResponse<T> {
  if (Array.isArray(data)) {
    return {
      items: data,
      limit: fallback.limit ?? data.length,
      offset: fallback.offset ?? 0,
      total: data.length,
    }
  }

  return {
    items: Array.isArray(data?.items) ? data.items : [],
    limit: data?.limit ?? fallback.limit ?? 20,
    offset: data?.offset ?? fallback.offset ?? 0,
    total: data?.total ?? data?.items?.length ?? 0,
  }
}

export const api = {
  auth: {
    login: async (credentials: { username: string; password: string }) => {
      const response = await client.post<AuthSession>("/auth/login", credentials)
      return response.data
    },
    google: async () => {
      const response = await client.post<AuthSession>("/auth/google")
      return response.data
    },
  },
  classrooms: {
    list: async (params: ListParams = {}) => {
      const response = await client.get<PaginatedResponse<Classroom> | Classroom[]>(
        "/classrooms/",
        { params: listParams(params) }
      )
      return normalizeList(response.data, params)
    },
    get: async (id: number) => {
      const response = await client.get<Classroom>(`/classrooms/${id}`)
      return response.data
    },
  },
  teachers: {
    list: async (params: ListParams = {}) => {
      const response = await client.get<PaginatedResponse<Teacher> | Teacher[]>(
        "/teachers/",
        { params: listParams(params, "teacher_name") }
      )
      return normalizeList(response.data, params)
    },
    get: async (id: number) => {
      const response = await client.get<Teacher>(`/teachers/${id}`)
      return response.data
    },
  },
  students: {
    list: async (params: ListParams = {}) => {
      const response = await client.get<PaginatedResponse<Student> | Student[]>(
        "/students/",
        { params: listParams(params, "student_name") }
      )
      return normalizeList(response.data, params)
    },
    get: async (id: number) => {
      const response = await client.get<Student>(`/students/${id}`)
      return response.data
    },
  },
}
