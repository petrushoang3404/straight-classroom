import { api } from "@/lib/api"
import type { Classroom } from "@/lib/models"

import { ResourceDetail, ResourceList, type ResourceConfig } from "./resource-ui"

const config: ResourceConfig<Classroom> = {
  title: "Lớp học",
  singular: "Lớp học",
  description:
    "Theo dõi phòng học, sức chứa và địa điểm để việc phân bổ lớp diễn ra rõ ràng.",
  searchPlaceholder: "Tìm theo tên lớp hoặc địa điểm",
  basePath: "/classrooms",
  emptyText: "Chưa có lớp học phù hợp.",
  list: api.classrooms.list,
  get: api.classrooms.get,
  primary: (classroom) => classroom.name,
  secondary: (classroom) => classroom.location,
  badge: (classroom) => `${classroom.capacity} chỗ`,
  columns: [
    { label: "Địa điểm", value: (classroom) => classroom.location },
    { label: "Sức chứa", value: (classroom) => `${classroom.capacity}` },
  ],
  details: [
    { label: "Tên lớp", value: (classroom) => classroom.name },
    { label: "Địa điểm", value: (classroom) => classroom.location },
    { label: "Sức chứa", value: (classroom) => `${classroom.capacity} học viên` },
    {
      label: "Giáo viên phụ trách",
      value: (classroom) =>
        classroom.teachers.length > 0
          ? classroom.teachers.map((teacher) => teacher.name).join(", ")
          : "Chưa phân công",
    },
    { label: "Mã lớp", value: (classroom) => `#${classroom.id}` },
  ],
}

export function ClassroomsList() {
  return <ResourceList config={config} />
}

export function ClassroomDetail({ id }: { id: number }) {
  return <ResourceDetail config={config} id={id} />
}
