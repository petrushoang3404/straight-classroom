import { useEffect, useState, type ChangeEvent, type FormEvent } from "react"
import { ClipboardCheck, Trash2 } from "lucide-react"

import {
  DetailEmptyState,
  DetailSection,
  RelatedResourceRow,
} from "@/components/detail-ui"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { FormField } from "@/components/ui/form-field"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "@/components/ui/toast"
import { api } from "@/lib/api"
import { getApiErrorMessage } from "@/lib/api-error"
import { formatDate } from "@/lib/format"
import type { AttendanceSession, FaceDetection, Student } from "@/lib/models"

const maxPhotoSize = 10 * 1024 * 1024

// Kept in step with PhotoUploadUrlRequest on the backend.
const photoTypes = ["image/jpeg", "image/png"]

const studentName = (student: Student) =>
  `${student.saint_name} ${student.first_name} ${student.last_name}`

// YYYY-MM-DD in the viewer's own timezone, which is what <input type="date"> wants.
const today = () => new Date().toLocaleDateString("sv-SE")

type Photo = {
  previewUrl: string
  objectKey: string
  detection: FaceDetection
}

export function ClassroomAttendance({
  classroomId,
  students,
}: {
  classroomId: number
  students: Student[]
}) {
  const [sessions, setSessions] = useState<AttendanceSession[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(false)
  const [busyId, setBusyId] = useState<number | null>(null)

  const [open, setOpen] = useState(false)
  const [date, setDate] = useState(today)
  const [present, setPresent] = useState<Set<number>>(new Set())
  const [photo, setPhoto] = useState<Photo | null>(null)
  const [photoError, setPhotoError] = useState("")
  const [detecting, setDetecting] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    let active = true
    setLoading(true)
    setLoadError(false)

    api.classrooms.attendance
      .list(classroomId, { limit: 50 })
      .then((response) => {
        if (active) setSessions(response.items)
      })
      .catch(() => {
        if (active) setLoadError(true)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [classroomId])

  const previewUrl = photo?.previewUrl
  useEffect(
    () => () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    },
    [previewUrl]
  )

  const reset = () => {
    setDate(today())
    setPresent(new Set())
    setPhoto(null)
    setPhotoError("")
  }

  const handleOpenChange = (nextOpen: boolean) => {
    if (saving || detecting) return
    setOpen(nextOpen)
    if (!nextOpen) reset()
  }

  const handlePhotoChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ""
    if (!file) return

    if (!photoTypes.includes(file.type)) {
      setPhotoError("Chỉ chấp nhận ảnh JPEG hoặc PNG.")
      return
    }
    if (file.size > maxPhotoSize) {
      setPhotoError("Ảnh vượt quá giới hạn 10 MB.")
      return
    }

    setPhotoError("")
    setDetecting(true)
    try {
      const { objectKey, detection } = await api.classrooms.attendance.detect(
        classroomId,
        file
      )
      setPhoto({ previewUrl: URL.createObjectURL(file), objectKey, detection })
    } catch (error) {
      setPhoto(null)
      setPhotoError(
        getApiErrorMessage(error, "Không đếm được khuôn mặt. Vui lòng thử lại.")
      )
    } finally {
      setDetecting(false)
    }
  }

  const togglePresent = (studentId: number) =>
    setPresent((current) => {
      const next = new Set(current)
      if (!next.delete(studentId)) next.add(studentId)
      return next
    })

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    try {
      const session = await api.classrooms.attendance.create(classroomId, {
        session_date: date,
        photo_object_key: photo?.objectKey ?? null,
        records: students.map((student) => ({
          student_id: student.id,
          present: present.has(student.id),
        })),
      })
      setSessions((current) => [session, ...current])
      toast.success(
        "Đã lưu điểm danh",
        `${session.present_count}/${session.total_count} học viên có mặt.`
      )
      setOpen(false)
      reset()
    } catch (error) {
      toast.error(
        "Không lưu được điểm danh",
        getApiErrorMessage(error, "Vui lòng thử lại sau ít phút.")
      )
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (session: AttendanceSession) => {
    const label = formatDate(session.session_date)
    if (!window.confirm(`Xóa buổi điểm danh ngày ${label}?`)) return

    setBusyId(session.id)
    try {
      await api.classrooms.attendance.remove(classroomId, session.id)
      setSessions((current) => current.filter((item) => item.id !== session.id))
      toast.success("Đã xóa điểm danh", `Buổi ngày ${label} đã được gỡ bỏ.`)
    } catch (error) {
      toast.error(
        "Không xóa được điểm danh",
        getApiErrorMessage(error, "Vui lòng thử lại sau ít phút.")
      )
    } finally {
      setBusyId(null)
    }
  }

  const nameById = new Map(students.map((student) => [student.id, studentName(student)]))
  const detected = photo?.detection.count

  const describe = (session: AttendanceSession) => {
    const absent = session.records
      .filter((record) => !record.present)
      .map((record) => nameById.get(record.student_id) ?? `#${record.student_id}`)
    return [
      `Có mặt ${session.present_count}/${session.total_count}`,
      session.detected_count !== null
        ? `ảnh: ${session.detected_count} khuôn mặt`
        : null,
      absent.length > 0 ? `vắng: ${absent.join(", ")}` : null,
    ]
      .filter(Boolean)
      .join(" · ")
  }

  return (
    <>
      <DetailSection
        action={
          <Button
            disabled={students.length === 0}
            onClick={() => setOpen(true)}
            size="sm"
          >
            <ClipboardCheck />
            Điểm danh
          </Button>
        }
        description="Chụp ảnh lớp để đếm số khuôn mặt, rồi đánh dấu học viên có mặt."
        icon={ClipboardCheck}
        title={`Điểm danh (${sessions.length})`}
      >
        {loading ? (
          <div className="grid gap-4">
            {[0, 1, 2].map((row) => (
              <Skeleton className="h-9 w-full" key={row} />
            ))}
          </div>
        ) : loadError ? (
          <DetailEmptyState
            description="Không thể tải lịch sử điểm danh của lớp lúc này."
            icon={ClipboardCheck}
            title="Chưa tải được lịch sử"
          />
        ) : sessions.length === 0 ? (
          <DetailEmptyState
            description="Các buổi điểm danh của lớp sẽ được lưu tại đây."
            icon={ClipboardCheck}
            title="Chưa có buổi điểm danh"
          />
        ) : (
          sessions.map((session) => (
            <RelatedResourceRow
              badge={
                <Button
                  aria-label={`Xóa buổi điểm danh ngày ${formatDate(session.session_date)}`}
                  disabled={busyId === session.id}
                  onClick={() => handleDelete(session)}
                  size="icon-sm"
                  variant="ghost"
                >
                  <Trash2 />
                </Button>
              }
              description={describe(session)}
              icon={ClipboardCheck}
              key={session.id}
              title={formatDate(session.session_date) ?? session.session_date}
            />
          ))
        )}
      </DetailSection>

      <Dialog onOpenChange={handleOpenChange} open={open}>
        <DialogContent>
          <form className="contents" onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>Điểm danh</DialogTitle>
              <DialogDescription>
                Ảnh lớp chỉ dùng để đếm khuôn mặt, không nhận diện từng người.
                Hãy đánh dấu học viên có mặt trong danh sách.
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4">
              <FormField htmlFor="attendance-date" label="Ngày" required>
                <Input
                  id="attendance-date"
                  max={today()}
                  onChange={(event) => setDate(event.target.value)}
                  required
                  type="date"
                  value={date}
                />
              </FormField>

              <FormField
                description={
                  detecting
                    ? "Đang đếm khuôn mặt..."
                    : "Không bắt buộc. JPEG hoặc PNG; tối đa 10 MB."
                }
                error={photoError}
                htmlFor="attendance-photo"
                label="Ảnh lớp học"
              >
                <Input
                  accept=".jpg,.jpeg,.png"
                  disabled={detecting}
                  id="attendance-photo"
                  onChange={handlePhotoChange}
                  type="file"
                />
              </FormField>

              {photo ? (
                <div className="grid gap-2">
                  <div className="relative overflow-hidden rounded-lg border">
                    <img
                      alt="Ảnh lớp học"
                      className="block w-full"
                      src={photo.previewUrl}
                    />
                    {photo.detection.faces.map((face, index) => (
                      <span
                        className="absolute rounded-sm border-2 border-primary"
                        key={index}
                        style={{
                          left: `${(face.x1 / photo.detection.width) * 100}%`,
                          top: `${(face.y1 / photo.detection.height) * 100}%`,
                          width: `${((face.x2 - face.x1) / photo.detection.width) * 100}%`,
                          height: `${((face.y2 - face.y1) / photo.detection.height) * 100}%`,
                        }}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Phát hiện {photo.detection.count} khuôn mặt
                  </p>
                </div>
              ) : null}

              <FormField
                htmlFor="attendance-roster"
                label={`Có mặt (${present.size}/${students.length})`}
                description={
                  detected !== undefined && detected !== present.size
                    ? `Số đã đánh dấu khác số khuôn mặt trong ảnh (${detected}). Hãy kiểm tra lại.`
                    : undefined
                }
              >
                <div
                  className="max-h-56 overflow-y-auto rounded-lg border"
                  id="attendance-roster"
                >
                  {students.map((student) => (
                    <label
                      className="flex cursor-pointer items-center gap-3 border-b px-3 py-2 text-sm last:border-b-0 hover:bg-accent/45"
                      key={student.id}
                    >
                      <input
                        checked={present.has(student.id)}
                        className="size-4"
                        onChange={() => togglePresent(student.id)}
                        type="checkbox"
                      />
                      {studentName(student)}
                    </label>
                  ))}
                </div>
              </FormField>
            </div>

            <DialogFooter>
              <Button
                disabled={saving || detecting}
                onClick={() => handleOpenChange(false)}
                type="button"
                variant="outline"
              >
                Hủy
              </Button>
              <Button disabled={saving || detecting} type="submit">
                {saving ? "Đang lưu..." : "Lưu điểm danh"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  )
}
