import { useState, type ChangeEvent, type DragEvent, type FormEvent } from "react"
import { FileText, FolderOpen, UploadCloud, X } from "lucide-react"

import {
  DetailEmptyState,
  DetailSection,
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
import {
  FormField,
  fieldAccessibility,
} from "@/components/ui/form-field"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "@/components/ui/toast"

const maxFileSize = 50 * 1024 * 1024

const fileHint = "PDF, JPEG hoặc PNG; tối đa 50 MB."

function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${Math.round(size / 1024)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

export function ClassroomMaterials({
  classroomId,
  classroomName,
}: {
  classroomId: number
  classroomName: string
}) {
  const [open, setOpen] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [fileError, setFileError] = useState("")
  const [description, setDescription] = useState("")

  const selectFile = (nextFile: File | undefined) => {
    if (!nextFile) return

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
    setOpen(nextOpen)
    if (!nextOpen) reset()
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!file) {
      setFileError("Vui lòng chọn tài liệu cần tải lên.")
      return
    }

    toast.info(
      "Tài liệu chưa được tải lên",
      `Dịch vụ lưu trữ chưa sẵn sàng. Tệp “${file.name}” chưa được lưu cho lớp #${classroomId}.`
    )
    handleOpenChange(false)
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
        title="Tài liệu lớp học"
      >
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
              <Button onClick={() => setOpen(false)} type="button" variant="outline">
                Hủy
              </Button>
              <Button type="submit">
                <UploadCloud />
                Tải lên
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  )
}
