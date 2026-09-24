import { useForm } from "react-hook-form"

import {
  ResourceFormDialog,
  type ResourceFormProps,
} from "@/components/resource-form-dialog"
import {
  FormField,
  FormSection,
  fieldAccessibility,
} from "@/components/ui/form-field"
import { Input } from "@/components/ui/input"
import { toast } from "@/components/ui/toast"
import { getApiErrorMessage } from "@/lib/api-error"
import type { Teacher, TeacherInput } from "@/lib/models"

const requiredText = (value: string) =>
  value.trim().length > 0 || "Vui lòng nhập thông tin này."

export function TeacherForm({
  initialItem,
  onOpenChange,
  onSuccess,
  open,
  save,
}: ResourceFormProps<Teacher, TeacherInput>) {
  const isEditing = initialItem !== null
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<TeacherInput>({
    defaultValues: {
      name: initialItem?.name ?? "",
      division: initialItem?.division ?? "",
    },
    mode: "onBlur",
    reValidateMode: "onChange",
  })

  const submit = handleSubmit(async (values) => {
    const payload: TeacherInput = {
      name: values.name.trim(),
      division: values.division.trim(),
    }

    try {
      const teacher = await save(payload)

      toast.success(
        isEditing ? "Đã cập nhật giáo viên" : "Đã thêm giáo viên",
        `${teacher.name} đã được ${isEditing ? "cập nhật" : "lưu"} thành công.`
      )
      onSuccess(teacher)
    } catch (error) {
      toast.error(
        "Không thể lưu giáo viên",
        getApiErrorMessage(
          error,
          "Vui lòng kiểm tra thông tin hoặc kết nối hệ thống."
        )
      )
    }
  })

  return (
    <ResourceFormDialog
      description="Ghi nhận thông tin giáo viên để phụ trách lớp và phân công giảng dạy."
      isSubmitting={isSubmitting}
      onOpenChange={onOpenChange}
      onSubmit={submit}
      open={open}
      submitLabel={isEditing ? "Lưu thay đổi" : "Thêm giáo viên"}
      title={isEditing ? "Cập nhật giáo viên" : "Thêm giáo viên"}
    >
      <FormSection
        description="Thông tin cốt lõi dùng để nhận diện giáo viên trong danh sách quản lý."
        title="Thông tin giáo viên"
      >
        <FormField
          description="Nhập tên thánh và tên gọi theo cách ghi chính thức."
          error={errors.name?.message}
          htmlFor="teacher-name"
          label="Tên giáo viên"
          required
        >
          <Input
            {...register("name", {
              maxLength: {
                value: 255,
                message: "Tên giáo viên không được vượt quá 255 ký tự.",
              },
              required: "Vui lòng nhập tên giáo viên.",
              validate: requiredText,
            })}
            {...fieldAccessibility(
              "teacher-name",
              errors.name?.message,
              "Nhập tên thánh và tên gọi theo cách ghi chính thức."
            )}
            autoComplete="name"
            autoFocus
            id="teacher-name"
            placeholder="Ví dụ: Thánh Anna Nguyễn Minh"
            required
          />
        </FormField>

        <FormField
          description="Có thể nhập chuyên môn, lĩnh vực phụ trách hoặc nhóm sinh hoạt."
          error={errors.division?.message}
          htmlFor="teacher-division"
          label="Chuyên môn / phân công"
          required
        >
          <Input
            {...register("division", {
              maxLength: {
                value: 255,
                message: "Thông tin phân công không được vượt quá 255 ký tự.",
              },
              required: "Vui lòng nhập chuyên môn hoặc phân công.",
              validate: requiredText,
            })}
            {...fieldAccessibility(
              "teacher-division",
              errors.division?.message,
              "Có thể nhập chuyên môn, lĩnh vực phụ trách hoặc nhóm sinh hoạt."
            )}
            id="teacher-division"
            placeholder="Ví dụ: Giáo lý căn bản"
            required
          />
        </FormField>
      </FormSection>
    </ResourceFormDialog>
  )
}
