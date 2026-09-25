import { useEffect, useState } from "react"
import { Loader2, RotateCcw } from "lucide-react"
import { useForm } from "react-hook-form"

import {
  ResourceFormDialog,
  type ResourceFormProps,
} from "@/components/resource-form-dialog"
import { Button } from "@/components/ui/button"
import {
  FormField,
  FormSection,
  fieldAccessibility,
} from "@/components/ui/form-field"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { toast } from "@/components/ui/toast"
import { api } from "@/lib/api"
import { getApiErrorMessage } from "@/lib/api-error"
import type { ClassroomSummary, Student, StudentInput } from "@/lib/models"

const standardDivisions = ["Ấu nhi", "Thiếu nhi", "Nghĩa sĩ", "Hiệp sĩ"]
const requiredText = (value: string) =>
  value.trim().length > 0 || "Vui lòng nhập thông tin này."

export function StudentForm({
  initialItem,
  onOpenChange,
  onSuccess,
  open,
  save,
}: ResourceFormProps<Student, StudentInput>) {
  const isEditing = initialItem !== null
  const [classroomOptions, setClassroomOptions] = useState<ClassroomSummary[]>(() =>
    initialItem ? [initialItem.classroom] : []
  )
  const [classroomOptionsError, setClassroomOptionsError] = useState("")
  const [classroomOptionsLoading, setClassroomOptionsLoading] = useState(true)
  const [classroomOptionsRequest, setClassroomOptionsRequest] = useState(0)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<StudentInput>({
    defaultValues: {
      saint_name: initialItem?.saint_name ?? "",
      first_name: initialItem?.first_name ?? "",
      last_name: initialItem?.last_name ?? "",
      division: initialItem?.division ?? "",
      classroom_id: initialItem?.classroom_id,
    },
    mode: "onBlur",
    reValidateMode: "onChange",
  })

  useEffect(() => {
    let active = true
    setClassroomOptionsLoading(true)
    setClassroomOptionsError("")

    api.classrooms
      .list({ limit: 100 })
      .then((response) => {
        if (!active) return

        const options: ClassroomSummary[] = [...response.items]
        if (
          initialItem?.classroom &&
          !options.some((classroom) => classroom.id === initialItem.classroom.id)
        ) {
          options.unshift(initialItem.classroom)
        }
        setClassroomOptions(options)
      })
      .catch(() => {
        if (active) {
          setClassroomOptionsError(
            "Không thể tải danh sách lớp. Vui lòng thử lại."
          )
        }
      })
      .finally(() => {
        if (active) setClassroomOptionsLoading(false)
      })

    return () => {
      active = false
    }
  }, [classroomOptionsRequest, initialItem])

  const divisionOptions =
    initialItem && !standardDivisions.includes(initialItem.division)
      ? [initialItem.division, ...standardDivisions]
      : standardDivisions
  const classroomDescription = classroomOptionsLoading
    ? "Đang tải danh sách lớp học..."
    : "Chọn lớp đang sinh hoạt và sẽ tiếp nhận học viên."

  const submit = handleSubmit(async (values) => {
    const payload: StudentInput = {
      saint_name: values.saint_name.trim(),
      first_name: values.first_name.trim(),
      last_name: values.last_name.trim(),
      division: values.division,
      classroom_id: values.classroom_id,
    }

    try {
      const student = await save(payload)
      const studentName = `${student.saint_name} ${student.first_name} ${student.last_name}`

      toast.success(
        isEditing ? "Đã cập nhật học sinh" : "Đã thêm học sinh",
        `${studentName} đã được ${isEditing ? "cập nhật" : "lưu"} thành công.`
      )
      onSuccess(student)
    } catch (error) {
      toast.error(
        "Không thể lưu học sinh",
        getApiErrorMessage(
          error,
          "Vui lòng kiểm tra thông tin hoặc kết nối hệ thống."
        )
      )
    }
  })

  return (
    <ResourceFormDialog
      description="Cập nhật đầy đủ định danh và lớp sinh hoạt của học viên."
      isSubmitting={isSubmitting}
      onOpenChange={onOpenChange}
      onSubmit={submit}
      open={open}
      submitLabel={isEditing ? "Lưu thay đổi" : "Thêm học sinh"}
      title={isEditing ? "Cập nhật học sinh" : "Thêm học sinh"}
    >
      <div className="grid gap-6">
        <FormSection
          description="Ghi tên thánh theo thông báo chính thức; tên gọi và họ theo giấy tờ hiện hành."
          title="Định danh học sinh"
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              error={errors.saint_name?.message}
              htmlFor="student-saint-name"
              label="Tên thánh"
              required
            >
              <Input
                {...register("saint_name", {
                  maxLength: {
                    value: 255,
                    message: "Tên thánh không được vượt quá 255 ký tự.",
                  },
                  required: "Vui lòng nhập tên thánh.",
                  validate: requiredText,
                })}
                {...fieldAccessibility("student-saint-name", errors.saint_name?.message)}
                autoFocus
                id="student-saint-name"
                placeholder="Ví dụ: Maria"
                required
              />
            </FormField>

            <FormField
              error={errors.first_name?.message}
              htmlFor="student-first-name"
              label="Tên gọi"
              required
            >
              <Input
                {...register("first_name", {
                  maxLength: {
                    value: 255,
                    message: "Tên gọi không được vượt quá 255 ký tự.",
                  },
                  required: "Vui lòng nhập tên gọi.",
                  validate: requiredText,
                })}
                {...fieldAccessibility("student-first-name", errors.first_name?.message)}
                autoComplete="given-name"
                id="student-first-name"
                placeholder="Ví dụ: An"
                required
              />
            </FormField>
          </div>

          <FormField
            error={errors.last_name?.message}
            htmlFor="student-last-name"
            label="Họ"
            required
          >
            <Input
              {...register("last_name", {
                maxLength: {
                  value: 255,
                  message: "Họ không được vượt quá 255 ký tự.",
                },
                required: "Vui lòng nhập họ.",
                validate: requiredText,
              })}
              {...fieldAccessibility("student-last-name", errors.last_name?.message)}
              autoComplete="family-name"
              id="student-last-name"
              placeholder="Ví dụ: Nguyễn"
              required
            />
          </FormField>
        </FormSection>

        <FormSection
          description="Xác định nhóm sinh hoạt và lớp đang theo học của học sinh."
          title="Phân bổ sinh hoạt"
        >
          <FormField
            description="Chọn ngành theo danh sách đang áp dụng tại cộng đoàn."
            error={errors.division?.message}
            htmlFor="student-division"
            label="Ngành sinh hoạt"
            required
          >
            <Select
              {...register("division", {
                required: "Vui lòng chọn ngành sinh hoạt.",
                validate: requiredText,
              })}
              {...fieldAccessibility(
                "student-division",
                errors.division?.message,
                "Chọn ngành theo danh sách đang áp dụng tại cộng đoàn."
              )}
              defaultValue={initialItem?.division ?? ""}
              id="student-division"
              required
            >
              <option disabled value="">
                Chọn ngành sinh hoạt
              </option>
              {divisionOptions.map((division) => (
                <option key={division} value={division}>
                  {division}
                </option>
              ))}
            </Select>
          </FormField>

          <FormField
            description={classroomDescription}
            error={errors.classroom_id?.message ?? classroomOptionsError}
            htmlFor="student-classroom"
            label="Lớp học"
            required
          >
            <Select
              {...register("classroom_id", {
                required: "Vui lòng chọn lớp học.",
                setValueAs: (value) => Number(value),
                validate: (value) =>
                  (Number.isInteger(value) && value > 0) ||
                  "Vui lòng chọn lớp học.",
              })}
              {...fieldAccessibility(
                "student-classroom",
                errors.classroom_id?.message ?? classroomOptionsError,
                classroomDescription
              )}
              aria-busy={classroomOptionsLoading}
              defaultValue={initialItem?.classroom_id ?? ""}
              disabled={classroomOptionsLoading || Boolean(classroomOptionsError)}
              id="student-classroom"
              required
            >
              <option disabled value="">
                {classroomOptionsLoading
                  ? "Đang tải lớp học..."
                  : classroomOptionsError
                    ? "Chưa tải được lớp học"
                    : "Chọn lớp học"}
              </option>
              {classroomOptions.map((classroom) => (
                <option key={classroom.id} value={classroom.id}>
                  {classroom.name} — {classroom.location}
                </option>
              ))}
            </Select>
          </FormField>

          {classroomOptionsError ? (
            <Button
              className="w-fit"
              disabled={classroomOptionsLoading}
              onClick={() => setClassroomOptionsRequest((current) => current + 1)}
              size="sm"
              type="button"
              variant="outline"
            >
              {classroomOptionsLoading ? (
                <Loader2 className="animate-spin" />
              ) : (
                <RotateCcw />
              )}
              Tải lại danh sách
            </Button>
          ) : null}
        </FormSection>
      </div>
    </ResourceFormDialog>
  )
}
