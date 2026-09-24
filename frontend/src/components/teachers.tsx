import {
  BookUser,
  CalendarDays,
  Cake,
  MapPin,
  Phone,
  School,
  UserRoundCheck,
} from "lucide-react"
import { useNavigate } from "react-router"

import {
  DetailEmptyState,
  DetailPageHeader,
  DetailSection,
  InfoGrid,
  InfoItem,
  RelatedResourceRow,
} from "@/components/detail-ui"
import { api } from "@/lib/api"
import { formatDate } from "@/lib/format"
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
}

export function TeachersList() {
  return <ResourceList config={config} />
}

export function TeacherDetail({ id }: { id: number }) {
  return (
    <ResourceDetail config={config} id={id}>
      {(teacher, { onEdit }) => (
        <TeacherDetailContent onEdit={onEdit} teacher={teacher} />
      )}
    </ResourceDetail>
  )
}

function TeacherDetailContent({
  onEdit,
  teacher,
}: {
  onEdit: () => void
  teacher: Teacher
}) {
  const navigate = useNavigate()
  const phoneNumber = teacher.phone_number?.trim() || null

  return (
    <div className="grid gap-4">
      <DetailPageHeader
        badge={
          <span className="inline-flex items-center gap-1.5 rounded-md border bg-accent px-2.5 py-1 text-sm font-medium text-accent-foreground">
            <BookUser className="size-3.5" />
            {teacher.division}
          </span>
        }
        description="Hồ sơ giáo viên và các lớp đang phụ trách."
        eyebrow={`Giáo viên #${teacher.id}`}
        icon={UserRoundCheck}
        onBack={() => navigate(config.basePath)}
        onEdit={onEdit}
        title={teacher.name}
      />

      <div className="grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <div className="grid gap-4">
          <DetailSection
            description="Thông tin chính và thông tin phục vụ việc lập danh sách."
            icon={BookUser}
            title="Thông tin giáo viên"
          >
            <InfoGrid>
              <InfoItem label="Tên thánh" value={teacher.saint_name} />
              <InfoItem label="Tên giáo viên" value={teacher.name} />
              <InfoItem label="Chuyên môn / phân công" value={teacher.division} />
              <InfoItem
                icon={Cake}
                label="Ngày sinh"
                value={formatDate(teacher.date_of_birth)}
              />
              <InfoItem
                icon={MapPin}
                label="Nơi sinh"
                value={teacher.place_of_birth}
              />
              <InfoItem
                icon={CalendarDays}
                label="Ngày lễ"
                value={teacher.feast_day}
              />
            </InfoGrid>
          </DetailSection>

          <DetailSection
            description="Các lớp đã được phân công cho giáo viên này."
            icon={School}
            title={`Lớp phụ trách (${teacher.classrooms.length})`}
          >
            {teacher.classrooms.length === 0 ? (
              <DetailEmptyState
                description="Giáo viên chưa được phân công lớp nào."
                icon={School}
                title="Chưa có lớp phụ trách"
              />
            ) : (
              teacher.classrooms.map((classroom) => (
                <RelatedResourceRow
                  description={classroom.location}
                  icon={School}
                  key={classroom.id}
                  onClick={() => navigate(`/classrooms/${classroom.id}`)}
                  title={classroom.name}
                />
              ))
            )}
          </DetailSection>
        </div>

        <div className="grid gap-4">
          <DetailSection
            description="Thông tin liên hệ dùng cho việc phối hợp trong chương trình."
            icon={Phone}
            title="Liên hệ"
          >
            <InfoGrid className="sm:grid-cols-1">
              <InfoItem
                icon={Phone}
                label="Số điện thoại"
                value={
                  phoneNumber ? (
                    <a
                      className="text-primary underline-offset-4 hover:underline"
                      href={`tel:${phoneNumber}`}
                    >
                      {phoneNumber}
                    </a>
                  ) : null
                }
              />
              <InfoItem
                icon={MapPin}
                label="Địa chỉ"
                value={teacher.address}
              />
            </InfoGrid>
          </DetailSection>

          <DetailSection icon={UserRoundCheck} title="Định danh hồ sơ">
            <InfoGrid className="sm:grid-cols-1">
              <InfoItem label="Mã giáo viên" value={`#${teacher.id}`} />
              <InfoItem
                label="Số lớp phụ trách"
                value={`${teacher.classrooms.length} lớp`}
              />
            </InfoGrid>
          </DetailSection>
        </div>
      </div>
    </div>
  )
}
