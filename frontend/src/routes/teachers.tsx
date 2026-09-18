import { api } from "@/lib/api"
import type { Teacher } from "@/lib/models"

import { ResourceDetail, ResourceList, type ResourceConfig } from "./resource-ui"

const config: ResourceConfig<Teacher> = {
  title: "Giáo viên",
  singular: "Giáo viên",
  description:
    "Quản lý danh sách giáo viên phụ trách và chuyên môn giảng dạy trong chương trình.",
  searchPlaceholder: "Tìm theo tên giáo viên",
  basePath: "/teachers",
  emptyText: "Chưa có giáo viên phù hợp.",
  list: api.teachers.list,
  get: api.teachers.get,
  primary: (teacher) => teacher.name,
  secondary: (teacher) => teacher.subject,
  badge: (teacher) => teacher.subject,
  columns: [
    { label: "Chuyên môn", value: (teacher) => teacher.subject },
    { label: "Mã hồ sơ", value: (teacher) => `#${teacher.id}` },
  ],
  details: [
    { label: "Tên giáo viên", value: (teacher) => teacher.name },
    { label: "Chuyên môn", value: (teacher) => teacher.subject },
    { label: "Mã giáo viên", value: (teacher) => `#${teacher.id}` },
  ],
}

export function TeachersList({ navigate }: { navigate: (path: string) => void }) {
  return <ResourceList config={config} navigate={navigate} />
}

export function TeacherDetail({
  id,
  navigate,
}: {
  id: number
  navigate: (path: string) => void
}) {
  return <ResourceDetail config={config} id={id} navigate={navigate} />
}
