import { useCallback, useEffect, useState, type ChangeEvent, type DragEvent, type FormEvent } from "react"
import {
  Download,
  FileText,
  FolderOpen,
  Image as ImageIcon,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react"

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
import { FormField, fieldAccessibility } from "@/components/ui/form-field"
import { Skeleton } from "@/components/ui/skeleton"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "@/components/ui/toast"
import { api } from "@/lib/api"
import { getApiErrorMessage } from "@/lib/api-error"
import { formatDateTime, formatFileSize } from "@/lib/format"
import type { Material } from "@/lib/models"

const maxFileSize = 50 * 1024 * 1024

// Kept in step with ALLOWED_CONTENT_TYPES on the backend. Checking here too
// catches drag-and-drop, which ignores the input's `accept` list.
const allowedTypes = ["application/pdf", "image/jpeg", "image/png"]

const fileHint = "PDF, JPEG hoặc PNG; tối đa 50 MB."

function materialIcon(contentType: string) {
  return contentType.startsWith("image/") ? ImageIcon : FileText
}

export function ClassroomMaterials({
  classroomId,
  classroomName,
  onTotalChange,
}: {
  classroomId: number
  classroomName: string
  onTotalChange?: (total: number) => void
}) {
  const [materials, setMaterials] = useState<Material[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(false)
  const [busyId, setBusyId] = useState<number | null>(null)

  const [open, setOpen] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [fileError, setFileError] = useState("")
  const [description, setDescription] = useState("")
  const [uploading, setUploading] = useState(false)

  // Kept in a callback so the upload and delete handlers can report the new
  // count to the parent without re-running the fetch effect.
  const publishTotal = useCallback(
    (total: number) => onTotalChange?.(total),
    [onTotalChange]
  )

  useEffect(() => {
    let active = true
    setLoading(true)
    setLoadError(false)

    api.classrooms.materials
      .list(classroomId, { limit: 50 })
      .then((response) => {
        if (!active) return
        setMaterials(response.items)
        publishTotal(response.total)
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
  }, [classroomId, publishTotal])

  const selectFile = (nextFile: File | undefined) => {
    if (!nextFile) return

    if (!allowedTypes.includes(nextFile.type)) {
      setFile(null)
      setFileError("Chỉ chấp nhận tệp PDF, JPEG hoặc PNG.")
      return
    }

    if (nextFile.size > maxFileSize) {
      setFile(null)
      setFileError("Tệp vượt quá giới hạn 50 MB.")
      return
    }

    setFile(nextFile)
    setFileError("")
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    selectFile(event.target.files?.[0])
    event.target.value = ""
  }

  const handleDrop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault()
    selectFile(event.dataTransfer.files[0])
  }

  const reset = () => {
    setFile(null)
    setFileError("")
    setDescription("")
  }

  const handleOpenChange = (nextOpen: boolean) => {
    if (uploading) return
    setOpen(nextOpen)
    if (!nextOpen) reset()
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!file) {
      setFileError("Vui lòng chọn tài liệu cần tải lên.")
      return
    }

    setUploading(true)
    try {
      const material = await api.classrooms.materials.upload(
        classroomId,
        file,
        description
      )
      setMaterials((current) => {
        const next = [material, ...current]
        publishTotal(next.length)
        return next
      })
      toast.success("Đã tải tài liệu lên", `“${material.filename}” đã được lưu.`)
      setOpen(false)
      reset()
    } catch (error) {
      toast.error(
        "Không tải được tài liệu",
        getApiErrorMessage(error, "Vui lòng thử lại sau ít phút.")
      )
    } finally {
      setUploading(false)
    }
  }

  const handleDownload = async (material: Material) => {
    setBusyId(material.id)
    try {
      const url = await api.classrooms.materials.downloadUrl(
        classroomId,
        material.id
      )
      // The presigned URL carries Content-Disposition: attachment, so the
      // browser saves the file and stays on the page.
      window.location.assign(url)
    } catch (error) {
      toast.error(
        "Không tải được tài liệu",
        getApiErrorMessage(error, "Liên kết tải xuống không khả dụng.")
      )
    } finally {
      setBusyId(null)
    }
  }

  const handleDelete = async (material: Material) => {
    if (!window.confirm(`Xóa tài liệu “${material.filename}”?`)) return

    setBusyId(material.id)
    try {
      await api.classrooms.materials.remove(classroomId, material.id)
      setMaterials((current) => {
        const next = current.filter((item) => item.id !== material.id)
        publishTotal(next.length)
        return next
      })
      toast.success("Đã xóa tài liệu", `“${material.filename}” đã được gỡ bỏ.`)
    } catch (error) {
      toast.error(
        "Không xóa được tài liệu",
        getApiErrorMessage(error, "Vui lòng thử lại sau ít phút.")
      )
    } finally {
      setBusyId(null)
    }
  }

  return (
    <>
      <DetailSection
        action={
          <Button onClick={() => setOpen(true)} size="sm">
            <UploadCloud />
            Tải tài liệu
          </Button>
        }
        description="Tài liệu giảng dạy dùng chung cho lớp học."
        icon={FolderOpen}
        title={`Tài liệu lớp học (${materials.length})`}
      >
        {loading ? (
          <MaterialListSkeleton />
        ) : loadError ? (
          <DetailEmptyState
            description="Không thể tải danh sách tài liệu của lớp lúc này."
            icon={FolderOpen}
            title="Chưa tải được danh sách"
          />
        ) : materials.length === 0 ? (
          <DetailEmptyState
            action={
              <Button onClick={() => setOpen(true)} variant="outline">
                <UploadCloud />
                Chọn tài liệu đầu tiên
              </Button>
            }
            description="Tài liệu giảng dạy, tài liệu học viên và tài liệu tham khảo sẽ được lưu tại đây để giáo viên trao đổi."
            icon={FileText}
            title="Chưa có tài liệu"
          />
        ) : (
          <div>
            {materials.map((material) => (
              <RelatedResourceRow
                badge={
                  <span className="flex items-center gap-1">
                    <Button
                      aria-label={`Tải xuống ${material.filename}`}
                      disabled={busyId === material.id}
                      onClick={() => handleDownload(material)}
                      size="icon-sm"
                      variant="ghost"
                    >
                      <Download />
                    </Button>
                    <Button
                      aria-label={`Xóa ${material.filename}`}
                      disabled={busyId === material.id}
                      onClick={() => handleDelete(material)}
                      size="icon-sm"
                      variant="ghost"
                    >
                      <Trash2 />
                    </Button>
                  </span>
                }
                description={
                  [
                    formatFileSize(material.size_bytes),
                    formatDateTime(material.created_at),
                    material.description,
                  ]
                    .filter(Boolean)
                    .join(" · ")
                }
                icon={materialIcon(material.content_type)}
                key={material.id}
                title={material.filename}
              />
            ))}
          </div>
        )}
      </DetailSection>

      <Dialog onOpenChange={handleOpenChange} open={open}>
        <DialogContent>
          <form className="contents" onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>Tải tài liệu lên lớp</DialogTitle>
              <DialogDescription>
                Chuẩn bị tài liệu cho {classroomName}. Thông tin được trình bày rõ ràng để giáo viên dễ tra cứu.
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4">
              <FormField
                description={fileHint}
                error={fileError}
                htmlFor="classroom-material-file"
                label="Tệp tài liệu"
                required
              >
                <label
                  className="flex min-h-28 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed bg-muted/20 px-5 py-5 text-center transition-colors hover:border-primary/40 hover:bg-accent/35"
                  htmlFor="classroom-material-file"
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={handleDrop}
                >
                  <input
                    accept=".pdf,.jpg,.jpeg,.png"
                    {...fieldAccessibility(
                      "classroom-material-file",
                      fileError,
                      fileHint
                    )}
                    className="sr-only"
                    id="classroom-material-file"
                    onChange={handleFileChange}
                    type="file"
                  />
                  {file ? (
                    <>
                      <span className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <FileText className="size-4" />
                      </span>
                      <span className="mt-2 max-w-full truncate text-sm font-medium">
                        {file.name}
                      </span>
                      <span className="mt-0.5 text-xs text-muted-foreground">
                        {formatFileSize(file.size)}
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <UploadCloud className="size-4" />
                      </span>
                      <span className="mt-2 text-sm font-medium">
                        Chọn tệp hoặc kéo thả vào đây
                      </span>
                      <span className="mt-0.5 text-xs text-muted-foreground">
                        Tối đa 50 MB
                      </span>
                    </>
                  )}
                </label>
              </FormField>

              {file ? (
                <Button
                  className="w-fit"
                  onClick={() => {
                    setFile(null)
                    setFileError("")
                  }}
                  size="xs"
                  type="button"
                  variant="ghost"
                >
                  <X />
                  Xóa tệp đã chọn
                </Button>
              ) : null}

              <FormField
                description="Không bắt buộc. Giúp giáo viên và người quản lý nhận diện tài liệu."
                htmlFor="classroom-material-description"
                label="Mô tả"
              >
                <Textarea
                  {...fieldAccessibility(
                    "classroom-material-description",
                    undefined,
                    "Không bắt buộc. Giúp giáo viên và người quản lý nhận diện tài liệu."
                  )}
                  id="classroom-material-description"
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder="Mục đích, thời lượng hoặc hướng dẫn sử dụng"
                  value={description}
                />
              </FormField>
            </div>

            <DialogFooter>
              <Button
                disabled={uploading}
                onClick={() => handleOpenChange(false)}
                type="button"
                variant="outline"
              >
                Hủy
              </Button>
              <Button disabled={uploading} type="submit">
                <UploadCloud />
                {uploading ? "Đang tải lên..." : "Tải lên"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  )
}

function MaterialListSkeleton() {
  return (
    <div className="grid gap-4">
      {[0, 1, 2].map((row) => (
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
