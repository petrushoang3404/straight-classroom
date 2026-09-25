import type { FormEventHandler, ReactNode } from "react"
import type { FieldValues } from "react-hook-form"
import { Loader2, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

export type ResourceFormProps<TItem, TValues extends FieldValues> = {
  initialItem: TItem | null
  onOpenChange: (open: boolean) => void
  onSuccess: (item: TItem) => void
  open: boolean
  save: (values: TValues) => Promise<TItem>
}

type ResourceFormDialogProps = {
  cancelLabel?: string
  children: ReactNode
  description: string
  isSubmitting: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: FormEventHandler<HTMLFormElement>
  open: boolean
  submitLabel: string
  title: string
}

function ResourceFormDialog({
  cancelLabel = "Hủy",
  children,
  description,
  isSubmitting,
  onOpenChange,
  onSubmit,
  open,
  submitLabel,
  title,
}: ResourceFormDialogProps) {
  const handleOpenChange = (nextOpen: boolean) => {
    if (!isSubmitting) {
      onOpenChange(nextOpen)
    }
  }

  return (
    <Dialog onOpenChange={handleOpenChange} open={open}>
      <DialogContent className="gap-0 p-0" showCloseButton={false}>
        <form
          className="flex min-h-0 flex-1 flex-col overflow-hidden"
          noValidate
          onSubmit={onSubmit}
        >
          <DialogHeader className="shrink-0 border-b px-6 py-5 pr-14">
            <DialogTitle>{title}</DialogTitle>
            <DialogDescription>{description}</DialogDescription>
          </DialogHeader>

          <Button
            aria-label="Đóng biểu mẫu"
            className="absolute top-4 right-4"
            disabled={isSubmitting}
            onClick={() => onOpenChange(false)}
            size="icon"
            type="button"
            variant="ghost"
          >
            <X />
            <span className="sr-only">Đóng</span>
          </Button>

          <div className="min-h-0 flex-1 overflow-y-auto px-6 py-5">{children}</div>

          <DialogFooter className="mt-0 shrink-0 border-t bg-muted/25 px-6 py-4 sm:flex-row sm:justify-end">
            <Button
              disabled={isSubmitting}
              onClick={() => onOpenChange(false)}
              type="button"
              variant="outline"
            >
              {cancelLabel}
            </Button>
            <Button disabled={isSubmitting} type="submit">
              {isSubmitting ? <Loader2 className="animate-spin" /> : null}
              {submitLabel}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export { ResourceFormDialog }
