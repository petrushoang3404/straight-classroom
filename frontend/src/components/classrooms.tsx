import { useEffect, useState } from "react"
import {
  BookOpen,
  MapPin,
  School,
  UserRoundCheck,
  UsersRound,
  type LucideIcon,
} from "lucide-react"
import { useNavigate } from "react-router"

import { ClassroomMaterials } from "@/components/classroom-materials"
import {
  DetailEmptyState,
  DetailPageHeader,
  DetailSection,
  RelatedResourceRow,
} from "@/components/detail-ui"
import { Skeleton } from "@/components/ui/skeleton"
import { api } from "@/lib/api"
import { useAuthStore } from "@/lib/auth-store"
import type { Classroom, ClassroomInput, Student } from "@/lib/models"

import { ClassroomForm } from "./classroom-form"
import { ResourceDetail, ResourceList, type ResourceConfig } from "./resource-ui"

const config: ResourceConfig<Classroom, ClassroomInput> = {
  title: "Lớp học",
  singular: "Lớp học",
  description:
    "Theo dõi phòng học, sức chứa và địa điểm để việc phân bổ lớp diễn ra rõ ràng.",
  searchPlaceholder: "Tìm theo tên lớp hoặc địa điểm",
  basePath: "/classrooms",
  emptyText: "Chưa có lớp học phù hợp.",
  list: api.classrooms.list,
  get: api.classrooms.get,
  create: api.classrooms.create,
  update: api.classrooms.update,
  form: {
    component: ClassroomForm,
    createLabel: "Thêm lớp học",
  },
  primary: (classroom) => classroom.name,
  secondary: (classroom) => classroom.location,
  badge: (classroom) => `${classroom.capacity} chỗ`,
  columns: [
    { label: "Địa điểm", value: (classroom) => classroom.location },
    { label: "Sức chứa", value: (classroom) => `${classroom.capacity}` },
  ],
}

export function ClassroomsList() {
  return <ResourceList config={config} />
}

export function ClassroomDetail({ id }: { id: number }) {
  return (
    <ResourceDetail config={config} id={id}>
      {(classroom, { onEdit }) => (
        <ClassroomDetailContent classroom={classroom} onEdit={onEdit} />
      )}
    </ResourceDetail>
  )
}

function ClassroomDetailContent({
  classroom,
  onEdit,
}: {
  classroom: Classroom
  onEdit: () => void
}) {
  const navigate = useNavigate()
  const role = useAuthStore((state) => state.session?.role)
  const canOpenTeacherProfile = role === "admin"
  const [materialTotal, setMaterialTotal] = useState(0)
  const [students, setStudents] = useState<Student[]>([])
  const [studentTotal, setStudentTotal] = useState(0)
  const [studentsLoading, setStudentsLoading] = useState(true)
  const [studentsError, setStudentsError] = useState(false)

  useEffect(() => {
    let active = true
    setStudentsLoading(true)
    setStudentsError(false)

    api.classrooms
      .students(classroom.id, { limit: 50 })
      .then((response) => {
        if (!active) return
        setStudents(response.items)
        setStudentTotal(response.total)
      })
      .catch(() => {
        if (active) setStudentsError(true)
      })
      .finally(() => {
        if (active) setStudentsLoading(false)
      })

    return () => {
      active = false
    }
  }, [classroom.id])

  const occupancy = classroom.capacity > 0
    ? Math.min(100, Math.round((studentTotal / classroom.capacity) * 100))
    : 0
  const isOverCapacity = studentTotal > classroom.capacity

  return (
    <div className="grid gap-4">
      <DetailPageHeader
        badge={
          <span className="inline-flex items-center gap-1.5 rounded-md border bg-accent px-2.5 py-1 text-sm font-medium text-accent-foreground">
            <UsersRound className="size-3.5" />
            {classroom.capacity} chỗ
          </span>
        }
        description={
          <span className="inline-flex items-center gap-1.5">
            <MapPin className="size-3.5" />
            {classroom.location}
          </span>
        }
        eyebrow={`Lớp học #${classroom.id}`}
        icon={School}
        onBack={() => navigate(config.basePath)}
        onEdit={onEdit}
        title={classroom.name}
      />

      <div className="grid gap-3 sm:grid-cols-3">
        <SummaryMetric
          description={
            isOverCapacity
              ? `${studentTotal - classroom.capacity} học viên vượt sức chứa`
              : `${occupancy}% sức chứa đã sử dụng`
          }
          icon={UsersRound}
          label="Học viên"
          progress={occupancy}
          tone={isOverCapacity ? "destructive" : "default"}
          value={`${studentTotal}/${classroom.capacity}`}
        />
        <SummaryMetric
          description="Đang phụ trách lớp"
          icon={UserRoundCheck}
          label="Giáo viên"
          value={`${classroom.teachers.length}`}
        />
        <SummaryMetric
          description={
            materialTotal === 0
              ? "Chưa có tài liệu đã tải lên"
              : "Tài liệu dùng chung cho lớp"
          }
          icon={BookOpen}
          label="Tài liệu"
          value={`${materialTotal}`}
        />
      </div>

      <div className="grid items-start gap-4 lg:grid-cols-[minmax(0,1.45fr)_minmax(18rem,0.75fr)]">
        <DetailSection
          description="Danh sách học sinh đang theo học tại lớp."
          icon={UsersRound}
          title={`Học sinh (${studentTotal})`}
        >
          {studentsLoading ? (
            <RelatedListSkeleton />
          ) : studentsError ? (
            <DetailEmptyState
              description="Không thể tải danh sách học sinh của lớp lúc này."
              icon={UsersRound}
              title="Chưa tải được danh sách"
            />
          ) : students.length === 0 ? (
            <DetailEmptyState
              description="Lớp học chưa có học sinh được phân bổ."
              icon={UsersRound}
              title="Chưa có học sinh"
            />
          ) : (
            <div>
              {students.map((student) => (
                <RelatedResourceRow
                  badge={
                    <span className="rounded-md bg-muted px-2 py-1 text-xs font-medium text-muted-foreground">
                      {student.division}
                    </span>
                  }
                  description={`Mã học sinh #${student.id}`}
                  icon={UsersRound}
                  key={student.id}
                  onClick={() => navigate(`/students/${student.id}`)}
                  title={`${student.saint_name} ${student.first_name} ${student.last_name}`}
                />
              ))}
              {studentTotal > students.length ? (
                <p className="mt-3 border-t pt-3 text-xs text-muted-foreground">
                  Đang hiển thị {students.length} trong tổng số {studentTotal} học sinh.
                </p>
              ) : null}
            </div>
          )}
        </DetailSection>

        <div className="grid gap-4">
          <DetailSection
            description="Giáo viên được phân công phụ trách lớp."
            icon={UserRoundCheck}
            title={`Giáo viên (${classroom.teachers.length})`}
          >
            {classroom.teachers.length === 0 ? (
              <DetailEmptyState
                description="Lớp học chưa có giáo viên được phân công."
                icon={UserRoundCheck}
                title="Chưa phân công giáo viên"
              />
            ) : (
              classroom.teachers.map((teacher) => (
                <RelatedResourceRow
                  description={teacher.division}
                  icon={UserRoundCheck}
                  key={teacher.id}
                  onClick={
                    canOpenTeacherProfile
                      ? () => navigate(`/teachers/${teacher.id}`)
                      : undefined
                  }
                  title={teacher.name}
                />
              ))
            )}
          </DetailSection>

        </div>
      </div>

      <ClassroomMaterials
        classroomId={classroom.id}
        classroomName={classroom.name}
        onTotalChange={setMaterialTotal}
      />
    </div>
  )
}

function SummaryMetric({
  description,
  icon: Icon,
  label,
  progress,
  tone = "default",
  value,
}: {
  description: string
  icon: LucideIcon
  label: string
  progress?: number
  tone?: "default" | "destructive"
  value: string
}) {
  return (
    <div className="rounded-lg border bg-card p-4 shadow-xs">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-xs font-medium tracking-wide text-muted-foreground uppercase">
          <Icon className="size-3.5" />
          {label}
        </div>
        <span className="text-xl font-semibold tabular-nums">{value}</span>
      </div>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">{description}</p>
      {progress !== undefined ? (
        <div
          aria-label={`${progress}% sức chứa`}
          aria-valuemax={100}
          aria-valuemin={0}
          aria-valuenow={progress}
          className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted"
          role="progressbar"
        >
          <div
            className={`h-full rounded-full ${tone === "destructive" ? "bg-destructive" : "bg-primary"}`}
            style={{ width: `${progress}%` }}
          />
        </div>
      ) : null}
    </div>
  )
}

function RelatedListSkeleton() {
  return (
    <div className="grid gap-4">
      {[0, 1, 2, 3].map((row) => (
        <div className="flex items-center gap-3" key={row}>
          <Skeleton className="size-9 rounded-lg" />
          <div className="flex-1">
            <Skeleton className="h-4 w-2/5" />
            <Skeleton className="mt-2 h-3 w-3/5" />
          </div>
        </div>
      ))}
    </div>
  )
}
