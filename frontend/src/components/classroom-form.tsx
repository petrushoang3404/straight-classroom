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
import type { Classroom, ClassroomInput } from "@/lib/models"

const requiredText = (value: string) =>
  value.trim().length > 0 || "Vui lòng nhập thông tin này."

export function ClassroomForm({
  initialItem,
  onOpenChange,
  onSuccess,
  open,
  save,
}: ResourceFormProps<Classroom, ClassroomInput>) {
  const isEditing = initialItem !== null
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ClassroomInput>({
    defaultValues: {
      name: initialItem?.name ?? "",
      capacity: initialItem?.capacity,
      location: initialItem?.location ?? "",
    },
    mode: "onBlur",
    reValidateMode: "onChange",
  })

  const submit = handleSubmit(async (values) => {
    const payload: ClassroomInput = {
      name: values.name.trim(),
      location: values.location.trim(),
      capacity: values.capacity,
    }

    try {
      const classroom = await save(payload)

      toast.success(
        isEditing ? "Đã cập nhật lớp học" : "Đã tạo lớp học",
        `${classroom.name} đã được ${isEditing ? "cập nhật" : "thêm"} thành công.`
      )
      onSuccess(classroom)
    } catch (error) {
      toast.error(
        "Không thể lưu lớp học",
        getApiErrorMessage(
          error,
          "Vui lòng kiểm tra thông tin hoặc kết nối hệ thống."
        )
      )
    }
  })

  return (
    <ResourceFormDialog
      description="Cập nhật thông tin phòng học để việc phân bổ học viên và giáo viên được rõ ràng."
      isSubmitting={isSubmitting}
      onOpenChange={onOpenChange}
      onSubmit={submit}
      open={open}
      submitLabel={isEditing ? "Lưu thay đổi" : "Tạo lớp học"}
      title={isEditing ? "Cập nhật lớp học" : "Thêm lớp học"}
    >
      <FormSection description="Thông tin dùng để nhận diện và bố trí lớp học." title="Thông tin lớp học">
        <FormField
          error={errors.name?.message}
          htmlFor="classroom-name"
          label="Tên lớp học"
          required
        >
          <Input
            {...register("name", {
              maxLength: {
                value: 255,
                message: "Tên lớp học không được vượt quá 255 ký tự.",
              },
              required: "Vui lòng nhập tên lớp học.",
              validate: requiredText,
            })}
            {...fieldAccessibility("classroom-name", errors.name?.message)}
            autoFocus
            id="classroom-name"
            placeholder="Ví dụ: Khai Tâm A"
            required
          />
        </FormField>

        <div className="grid gap-4 sm:grid-cols-[1fr_10rem]">
          <FormField
            description="Phòng hoặc khu vực tổ chức sinh hoạt."
            error={errors.location?.message}
            htmlFor="classroom-location"
            label="Địa điểm"
            required
          >
            <Input
              {...register("location", {
                maxLength: {
                  value: 255,
                  message: "Địa điểm không được vượt quá 255 ký tự.",
                },
                required: "Vui lòng nhập địa điểm.",
                validate: requiredText,
              })}
              {...fieldAccessibility(
                "classroom-location",
                errors.location?.message,
                "Phòng hoặc khu vực tổ chức sinh hoạt."
              )}
              id="classroom-location"
              placeholder="Ví dụ: Phòng Gioan"
              required
            />
          </FormField>

          <FormField
            description="Số học viên tối đa."
            error={errors.capacity?.message}
            htmlFor="classroom-capacity"
            label="Sức chứa"
            required
          >
            <Input
              {...register("capacity", {
                required: "Vui lòng nhập sức chứa.",
                validate: (value) =>
                  (Number.isInteger(value) && value > 0) ||
                  "Sức chứa phải là số nguyên lớn hơn 0.",
                valueAsNumber: true,
              })}
              {...fieldAccessibility(
                "classroom-capacity",
                errors.capacity?.message,
                "Số học viên tối đa."
              )}
              id="classroom-capacity"
              inputMode="numeric"
              min={1}
              placeholder="28"
              required
              step={1}
              type="number"
            />
          </FormField>
        </div>
      </FormSection>
    </ResourceFormDialog>
  )
}
