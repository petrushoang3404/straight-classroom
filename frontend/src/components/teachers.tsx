import { api } from "@/lib/api"
import type { Teacher, TeacherInput } from "@/lib/models"

import { ResourceDetail, ResourceList, type ResourceConfig } from "./resource-ui"
import { TeacherForm } from "./teacher-form"

const config: ResourceConfig<Teacher, TeacherInput> = {
  title: "Giáo viên",
  singular: "Giáo viên",
  description:
    "Quản lý danh sách giáo viên phụ trách và chuyên môn giảng dạy trong chương trình.",
  searchPlaceholder: "Tìm theo tên giáo viên",
  basePath: "/teachers",
  emptyText: "Chưa có giáo viên phù hợp.",
  list: api.teachers.list,
  get: api.teachers.get,
  create: api.teachers.create,
  update: api.teachers.update,
  form: {
    component: TeacherForm,
    createLabel: "Thêm giáo viên",
  },
  primary: (teacher) => teacher.name,
  secondary: (teacher) => teacher.division,
  badge: (teacher) => teacher.division,
  columns: [
    { label: "Phân công", value: (teacher) => teacher.division },
    { label: "Mã hồ sơ", value: (teacher) => `#${teacher.id}` },
  ],
  details: [
    { label: "Tên giáo viên", value: (teacher) => teacher.name },
    { label: "Chuyên môn / phân công", value: (teacher) => teacher.division },
    {
      label: "Lớp phụ trách",
      value: (teacher) =>
        teacher.classrooms.length > 0
          ? teacher.classrooms.map((classroom) => classroom.name).join(", ")
          : "Chưa phân công",
    },
    { label: "Mã giáo viên", value: (teacher) => `#${teacher.id}` },
  ],
}

export function TeachersList() {
  return <ResourceList config={config} />
}

export function TeacherDetail({ id }: { id: number }) {
  return <ResourceDetail config={config} id={id} />
}
