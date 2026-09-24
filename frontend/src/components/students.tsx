import { api } from "@/lib/api"
import type { Student, StudentInput } from "@/lib/models"

import { ResourceDetail, ResourceList, type ResourceConfig } from "./resource-ui"
import { StudentForm } from "./student-form"

const fullName = (student: Student) =>
  `${student.saint_name} ${student.first_name} ${student.last_name}`

const config: ResourceConfig<Student, StudentInput> = {
  title: "Học sinh",
  singular: "Học sinh",
  description:
    "Quản lý hồ sơ học sinh theo tên thánh, tên gọi, ngành và lớp đang theo học.",
  searchPlaceholder: "Tìm theo tên học sinh",
  basePath: "/students",
  emptyText: "Chưa có học sinh phù hợp.",
  list: api.students.list,
  get: api.students.get,
  create: api.students.create,
  update: api.students.update,
  form: {
    component: StudentForm,
    createLabel: "Thêm học sinh",
  },
  primary: fullName,
  secondary: (student) => `${student.division} · ${student.classroom.name}`,
  badge: (student) => student.division,
  columns: [
    { label: "Ngành", value: (student) => student.division },
    { label: "Lớp", value: (student) => student.classroom.name },
  ],
  details: [
    { label: "Tên thánh", value: (student) => student.saint_name },
    { label: "Tên gọi", value: (student) => student.first_name },
    { label: "Họ", value: (student) => student.last_name },
    { label: "Ngành", value: (student) => student.division },
    {
      label: "Lớp học",
      value: (student) => `${student.classroom.name} (${student.classroom.location})`,
    },
    { label: "Mã học sinh", value: (student) => `#${student.id}` },
  ],
}

export function StudentsList() {
  return <ResourceList config={config} />
}

export function StudentDetail({ id }: { id: number }) {
  return <ResourceDetail config={config} id={id} />
}
