import axios from "axios"

import type { AuthSession } from "./auth-store"
import { useAuthStore } from "./auth-store"
import type {
  Classroom,
  ClassroomInput,
  ClassroomSummary,
  PaginatedResponse,
  Student,
  StudentInput,
  Teacher,
  TeacherInput,
  TeacherSummary,
} from "./models"
import { setupMockApi } from "./mock-api"

export const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api",
  headers: {
    "Content-Type": "application/json",
  },
})

// Attach the logged-in session's token to every request.
client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().session?.token
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`)
  }
  return config
})

// A 401 means the token is missing/expired/invalid -- drop the stale session
// and send the user back to the login page, except when the 401 came from
// the login call itself (that's just "wrong password", handled by the form).
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const isAuthRequest = error.config?.url?.startsWith("/auth/")
    if (error.response?.status === 401 && !isAuthRequest) {
      useAuthStore.getState().logout()
      if (window.location.pathname !== "/login") {
        window.location.assign("/login")
      }
    }
    return Promise.reject(error)
  }
)

if (import.meta.env.DEV && import.meta.env.VITE_USE_MOCKS !== "false") {
  setupMockApi(client)
}

type ListParams = {
  limit?: number
  offset?: number
  search?: string
}

type StudentListParams = ListParams & {
  classroomId?: number
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
    create: async (payload: ClassroomInput) => {
      const response = await client.post<Classroom>("/classrooms/", payload)
      return response.data
    },
    update: async (id: number, payload: ClassroomInput) => {
      const response = await client.patch<Classroom>(`/classrooms/${id}`, payload)
      return response.data
    },
    students: async (id: number, params: ListParams = {}) => {
      const response = await client.get<PaginatedResponse<Student> | Student[]>(
        `/classrooms/${id}/students`,
        { params: listParams(params) }
      )
      return normalizeList(response.data, params)
    },
    teachers: async (id: number) => {
      const response = await client.get<TeacherSummary[]>(
        `/classrooms/${id}/teachers`
      )
      return response.data
    },
    assignTeacher: async (id: number, teacherId: number) => {
      const response = await client.post<Classroom>(`/classrooms/${id}/teachers`, {
        teacher_id: teacherId,
      })
      return response.data
    },
    unassignTeacher: async (id: number, teacherId: number) => {
      await client.delete(`/classrooms/${id}/teachers/${teacherId}`)
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
    create: async (payload: TeacherInput) => {
      const response = await client.post<Teacher>("/teachers/", payload)
      return response.data
    },
    update: async (id: number, payload: TeacherInput) => {
      const response = await client.patch<Teacher>(`/teachers/${id}`, payload)
      return response.data
    },
    classrooms: async (id: number) => {
      const response = await client.get<ClassroomSummary[]>(
        `/teachers/${id}/classrooms`
      )
      return response.data
    },
  },
  students: {
    list: async ({ classroomId, ...params }: StudentListParams = {}) => {
      const response = await client.get<PaginatedResponse<Student> | Student[]>(
        "/students/",
        {
          params: {
            ...listParams(params, "student_name"),
            ...(classroomId ? { classroom_id: classroomId } : {}),
          },
        }
      )
      return normalizeList(response.data, params)
    },
    get: async (id: number) => {
      const response = await client.get<Student>(`/students/${id}`)
      return response.data
    },
    create: async (payload: StudentInput) => {
      const response = await client.post<Student>("/students/", payload)
      return response.data
    },
    update: async (id: number, payload: StudentInput) => {
      const response = await client.patch<Student>(`/students/${id}`, payload)
      return response.data
    },
  },
}
