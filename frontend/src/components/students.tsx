import {
  Cake,
  Droplets,
  Home,
  MapPin,
  Phone,
  School,
  Sparkles,
  UsersRound,
  Wheat,
  type LucideIcon,
} from "lucide-react"
import { useNavigate } from "react-router"

import {
  DetailPageHeader,
  DetailSection,
  InfoGrid,
  InfoItem,
  RelatedResourceRow,
} from "@/components/detail-ui"
import { api } from "@/lib/api"
import { formatDate } from "@/lib/format"
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
}

export function StudentsList() {
  return <ResourceList config={config} />
}

export function StudentDetail({ id }: { id: number }) {
  return (
    <ResourceDetail config={config} id={id}>
      {(student, { onEdit }) => (
        <StudentDetailContent onEdit={onEdit} student={student} />
      )}
    </ResourceDetail>
  )
}

function StudentDetailContent({
  onEdit,
  student,
}: {
  onEdit: () => void
  student: Student
}) {
  const navigate = useNavigate()
  const sacraments = [
    {
      title: "Rửa tội",
      date: student.date_of_baptism,
      place: student.place_of_baptism,
      icon: Droplets,
    },
    {
      title: "Thánh Thể",
      date: student.date_of_first_communion,
      place: student.place_of_first_communion,
      icon: Wheat,
    },
    {
      title: "Thêm sức",
      date: student.date_of_confirmation,
      place: student.place_of_confirmation,
      icon: Sparkles,
    },
  ]

  return (
    <div className="grid gap-4">
      <DetailPageHeader
        badge={
          <span className="inline-flex items-center gap-1.5 rounded-md border bg-accent px-2.5 py-1 text-sm font-medium text-accent-foreground">
            <UsersRound className="size-3.5" />
            {student.division}
          </span>
        }
        description={
          <span className="inline-flex items-center gap-1.5">
            <School className="size-3.5" />
            {student.classroom.name} · {student.classroom.location}
          </span>
        }
        eyebrow={`Học sinh #${student.id}`}
        icon={UsersRound}
        onBack={() => navigate(config.basePath)}
        onEdit={onEdit}
        title={fullName(student)}
      />

      <div className="grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <div className="grid gap-4">
          <DetailSection
            description="Thông tin định danh cơ bản của học sinh."
            icon={UsersRound}
            title="Thông tin học sinh"
          >
            <InfoGrid>
              <InfoItem label="Tên thánh" value={student.saint_name} />
              <InfoItem label="Tên gọi" value={student.first_name} />
              <InfoItem label="Họ" value={student.last_name} />
              <InfoItem label="Ngành sinh hoạt" value={student.division} />
              <InfoItem
                icon={Cake}
                label="Ngày sinh"
                value={formatDate(student.date_of_birth)}
              />
              <InfoItem
                icon={MapPin}
                label="Nơi sinh"
                value={student.place_of_birth}
              />
            </InfoGrid>
          </DetailSection>

          <DetailSection
            description="Các mốc bí tích đã được ghi nhận trong hồ sơ."
            icon={Sparkles}
            title="Nhận bí tích"
          >
            <div className="grid gap-3 md:grid-cols-3">
              {sacraments.map((sacrament) => (
                <SacramentCard
                  date={sacrament.date}
                  icon={sacrament.icon}
                  key={sacrament.title}
                  place={sacrament.place}
                  title={sacrament.title}
                />
              ))}
            </div>
          </DetailSection>

          <DetailSection
            description="Thông tin liên hệ và người bảo trợ học sinh."
            icon={UsersRound}
            title="Gia đình và liên hệ"
          >
            <InfoGrid>
              <InfoItem label="Cha / người bảo trợ" value={student.father_name} />
              <InfoItem
                icon={Phone}
                label="Số điện thoại"
                value={
                  student.father_phone_number ? (
                    <a
                      className="text-primary underline-offset-4 hover:underline"
                      href={`tel:${student.father_phone_number}`}
                    >
                      {student.father_phone_number}
                    </a>
                  ) : null
                }
              />
              <InfoItem label="Mẹ / người bảo trợ" value={student.mother_name} />
              <InfoItem
                icon={Phone}
                label="Số điện thoại"
                value={
                  student.mother_phone_number ? (
                    <a
                      className="text-primary underline-offset-4 hover:underline"
                      href={`tel:${student.mother_phone_number}`}
                    >
                      {student.mother_phone_number}
                    </a>
                  ) : null
                }
              />
              <InfoItem
                className="sm:col-span-2"
                icon={Home}
                label="Địa chỉ"
                value={student.address}
              />
            </InfoGrid>
          </DetailSection>
        </div>

        <div className="grid gap-4">
          <DetailSection
            description="Lớp đang tiếp nhận học sinh."
            icon={School}
            title="Lớp học"
          >
            <RelatedResourceRow
              description={student.classroom.location}
              icon={School}
              onClick={() => navigate(`/classrooms/${student.classroom.id}`)}
              title={student.classroom.name}
            />
          </DetailSection>

          <DetailSection icon={UsersRound} title="Định danh hồ sơ">
            <InfoGrid className="sm:grid-cols-1">
              <InfoItem label="Mã học sinh" value={`#${student.id}`} />
              <InfoItem label="Mã lớp" value={`#${student.classroom.id}`} />
            </InfoGrid>
          </DetailSection>
        </div>
      </div>
    </div>
  )
}

function SacramentCard({
  date,
  icon: Icon,
  place,
  title,
}: {
  date: string | null
  icon: LucideIcon
  place: string | null
  title: string
}) {
  const hasRecord = Boolean(date || place)

  return (
    <div className="rounded-lg border bg-muted/20 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <Icon className="size-4" />
        </div>
        <span
          className={`rounded-md px-2 py-1 text-[0.68rem] font-medium ${
            hasRecord
              ? "bg-primary/10 text-primary"
              : "bg-muted text-muted-foreground"
          }`}
        >
          {hasRecord ? "Đã ghi nhận" : "Chưa cập nhật"}
        </span>
      </div>
      <h3 className="mt-3 text-sm font-semibold">{title}</h3>
      <div className="mt-2 grid gap-2 text-xs leading-5">
        <p className={date ? "text-foreground" : "text-muted-foreground"}>
          {formatDate(date) || "Chưa có ngày"}
        </p>
        <p className="text-muted-foreground">{place || "Chưa có địa điểm"}</p>
      </div>
    </div>
  )
}
