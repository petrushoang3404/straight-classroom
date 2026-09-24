import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

type FormFieldProps = {
  children: ReactNode
  description?: string
  error?: string
  htmlFor: string
  label: string
  required?: boolean
}

function FormField({
  children,
  description,
  error,
  htmlFor,
  label,
  required = false,
}: FormFieldProps) {
  const descriptionId = description ? `${htmlFor}-description` : undefined
  const errorId = error ? `${htmlFor}-error` : undefined

  return (
    <div className="grid gap-2">
      <label className="flex items-center gap-1 text-sm font-medium" htmlFor={htmlFor}>
        {label}
        {required ? (
          <span aria-hidden="true" className="text-destructive">
            *
          </span>
        ) : null}
      </label>
      {children}
      {description ? (
        <p className="text-xs leading-5 text-muted-foreground" id={descriptionId}>
          {description}
        </p>
      ) : null}
      <p
        className={cn("text-xs leading-5 text-destructive", !error && "hidden")}
        id={errorId}
        role="alert"
      >
        {error || "Invalid value"}
      </p>
    </div>
  )
}

type FormSectionProps = {
  children: ReactNode
  description?: string
  title: string
}

function FormSection({ children, description, title }: FormSectionProps) {
  return (
    <section className="grid gap-4">
      <div>
        <h2 className="text-sm font-semibold">{title}</h2>
        {description ? (
          <p className="mt-1 text-sm leading-5 text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {children}
    </section>
  )
}

function fieldAccessibility(id: string, error?: string, description?: string) {
  return {
    "aria-describedby": [
      description ? `${id}-description` : null,
      error ? `${id}-error` : null,
    ]
      .filter(Boolean)
      .join(" ") || undefined,
    "aria-invalid": error ? (true as const) : undefined,
  }
}

export { FormField, FormSection, fieldAccessibility }
