import type { ReactNode } from "react"
import {
  AlertCircle,
  ArrowLeft,
  ChevronRight,
  Pencil,
  type LucideIcon,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

/**
 * Colours a detail page by what it is about -- the khăn quàng of a ngành, red
 * for a Huynh Trưởng. `background` is the scarf colour and `foreground` the
 * colour of the cross on it, which is what the icon is drawn in.
 */
export type DetailAccent = {
  background: string
  foreground: string
}

export function DetailPageHeader({
  accent,
  badge,
  description,
  eyebrow,
  icon: Icon,
  onBack,
  onEdit,
  title,
}: {
  accent?: DetailAccent | null
  badge?: ReactNode
  description?: ReactNode
  eyebrow: string
  icon: LucideIcon
  onBack: () => void
  onEdit: () => void
  title: string
}) {
  return (
    <header className="overflow-hidden rounded-lg border bg-card shadow-xs">
      {accent ? (
        <div
          aria-hidden="true"
          className="h-1.5"
          style={{ backgroundColor: accent.background }}
        />
      ) : null}
      <div className="flex items-center justify-between gap-3 border-b bg-muted/25 px-4 py-3">
        <Button onClick={onBack} size="sm" variant="outline">
          <ArrowLeft />
          Quay lại
        </Button>
        <Button onClick={onEdit} size="sm">
          <Pencil />
          Chỉnh sửa
        </Button>
      </div>
      <div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
        <div className="flex min-w-0 items-start gap-4">
          <div
            className={cn(
              "flex size-12 shrink-0 items-center justify-center rounded-lg",
              !accent && "bg-primary/10 text-primary"
            )}
            style={
              accent
                ? { backgroundColor: accent.background, color: accent.foreground }
                : undefined
            }
          >
            <Icon className="size-5" />
          </div>
          <div className="min-w-0">
            <p className="text-xs font-semibold tracking-wide text-primary uppercase">
              {eyebrow}
            </p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight">{title}</h1>
            {description ? (
              <div className="mt-1 text-sm leading-5 text-muted-foreground">
                {description}
              </div>
            ) : null}
          </div>
        </div>
        {badge ? <div className="w-fit shrink-0">{badge}</div> : null}
      </div>
    </header>
  )
}

export function DetailSection({
  action,
  children,
  description,
  icon: Icon,
  title,
}: {
  action?: ReactNode
  children: ReactNode
  description?: string
  icon?: LucideIcon
  title: string
}) {
  return (
    <section className="overflow-hidden rounded-lg border bg-card shadow-xs">
      <div className="flex flex-col gap-3 border-b px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 items-start gap-3">
          {Icon ? (
            <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
              <Icon className="size-4" />
            </div>
          ) : null}
          <div>
            <h2 className="font-semibold">{title}</h2>
            {description ? (
              <p className="mt-0.5 text-sm leading-5 text-muted-foreground">
                {description}
              </p>
            ) : null}
          </div>
        </div>
        {action ? <div className="shrink-0 pl-11 sm:pl-0">{action}</div> : null}
      </div>
      <div className="p-5">{children}</div>
    </section>
  )
}

export function InfoGrid({
  children,
  className = "",
}: {
  children: ReactNode
  className?: string
}) {
  return <div className={`grid gap-x-6 gap-y-5 sm:grid-cols-2 ${className}`}>{children}</div>
}

export function InfoItem({
  className,
  icon: Icon,
  label,
  value,
}: {
  className?: string
  icon?: LucideIcon
  label: string
  value: ReactNode
}) {
  const isEmpty = value === null || value === undefined || value === ""

  return (
    <div className={cn("min-w-0", className)}>
      <div className="flex items-center gap-1.5 text-xs font-medium tracking-wide text-muted-foreground uppercase">
        {Icon ? <Icon className="size-3.5" /> : null}
        {label}
      </div>
      <div
        className={`mt-1.5 text-sm leading-6 font-medium ${isEmpty ? "text-muted-foreground" : ""}`}
      >
        {isEmpty ? "Chưa cập nhật" : value}
      </div>
    </div>
  )
}

export function RelatedResourceRow({
  badge,
  description,
  icon: Icon,
  onClick,
  title,
}: {
  badge?: ReactNode
  description?: ReactNode
  icon: LucideIcon
  onClick?: () => void
  title: string
}) {
  const content = (
    <>
      <span
        className={cn(
          "flex size-9 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground",
          onClick &&
            "transition-colors group-hover:bg-background group-hover:text-primary"
        )}
      >
        <Icon className="size-4" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-medium">{title}</span>
        {description ? (
          <span className="mt-0.5 block truncate text-xs text-muted-foreground">
            {description}
          </span>
        ) : null}
      </span>
      {badge ? <span className="shrink-0">{badge}</span> : null}
      {onClick ? (
        <ChevronRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
      ) : null}
    </>
  )
  const className = cn(
    "group flex w-full items-center gap-3 border-b px-1 py-3 text-left last:border-b-0",
    onClick && "cursor-pointer transition-colors hover:bg-accent/45"
  )

  return onClick ? (
    <button className={className} onClick={onClick} type="button">
      {content}
    </button>
  ) : (
    <div className={className}>{content}</div>
  )
}

export function DetailEmptyState({
  action,
  description,
  icon: Icon,
  title,
}: {
  action?: ReactNode
  description: string
  icon: LucideIcon
  title: string
}) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center px-4 py-8 text-center">
      <div className="flex size-10 items-center justify-center rounded-lg bg-muted text-muted-foreground">
        <Icon className="size-4" />
      </div>
      <h3 className="mt-3 text-sm font-semibold">{title}</h3>
      <p className="mt-1 max-w-sm text-sm leading-5 text-muted-foreground">
        {description}
      </p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  )
}

export function DetailErrorState({
  description,
  onBack,
  title,
}: {
  description: string
  onBack: () => void
  title: string
}) {
  return (
    <div className="flex min-h-80 flex-col items-center justify-center rounded-lg border bg-card px-6 text-center shadow-xs">
      <div className="flex size-11 items-center justify-center rounded-lg bg-destructive/10 text-destructive">
        <AlertCircle className="size-5" />
      </div>
      <h1 className="mt-4 text-lg font-semibold">{title}</h1>
      <p className="mt-1 max-w-md text-sm leading-6 text-muted-foreground">
        {description}
      </p>
      <Button className="mt-5" onClick={onBack} variant="outline">
        <ArrowLeft />
        Quay lại danh sách
      </Button>
    </div>
  )
}

export function DetailPageSkeleton() {
  return (
    <div className="grid gap-4">
      <Skeleton className="h-52 rounded-lg" />
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <div className="grid gap-4">
          <Skeleton className="h-64 rounded-lg" />
          <Skeleton className="h-72 rounded-lg" />
        </div>
        <div className="grid content-start gap-4">
          <Skeleton className="h-44 rounded-lg" />
          <Skeleton className="h-56 rounded-lg" />
        </div>
      </div>
    </div>
  )
}
