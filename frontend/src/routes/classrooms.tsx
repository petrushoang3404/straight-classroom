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
    { label: "Mã lớp", value: (classroom) => `#${classroom.id}` },
  ],
}

export function ClassroomsList({ navigate }: { navigate: (path: string) => void }) {
  return <ResourceList config={config} navigate={navigate} />
}

export function ClassroomDetail({
  id,
  navigate,
}: {
  id: number
  navigate: (path: string) => void
}) {
  return <ResourceDetail config={config} id={id} navigate={navigate} />
}
