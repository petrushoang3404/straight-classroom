import { useEffect, useMemo, useState } from "react"
import {
  ArrowLeft,
  ChevronRight,
  Search,
  ShieldCheck,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import type { PaginatedResponse } from "@/lib/models"

export type ResourceConfig<T extends { id: number }> = {
  title: string
  singular: string
  description: string
  searchPlaceholder: string
  basePath: string
  emptyText: string
  list: (params: { limit?: number; offset?: number; search?: string }) => Promise<PaginatedResponse<T>>
  get: (id: number) => Promise<T>
  columns: Array<{
    label: string
    value: (item: T) => string
  }>
  details: Array<{
    label: string
    value: (item: T) => string
  }>
  primary: (item: T) => string
  secondary: (item: T) => string
  badge?: (item: T) => string
}

type ResourceProps<T extends { id: number }> = {
  config: ResourceConfig<T>
  navigate: (path: string) => void
}

export function ResourceList<T extends { id: number }>({
  config,
  navigate,
}: ResourceProps<T>) {
  const [items, setItems] = useState<T[]>([])
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setLoading(true)
      setError("")
      config
        .list({ limit: 50, search: search.trim() || undefined })
        .then((response) => {
          const normalizedSearch = search.trim().toLowerCase()
          const responseItems = Array.isArray(response.items)
            ? response.items
            : []
          const visibleItems = normalizedSearch
            ? responseItems.filter((item) =>
                `${config.primary(item)} ${config.secondary(item)}`
                  .toLowerCase()
                  .includes(normalizedSearch)
              )
            : responseItems

          setItems(visibleItems)
          setTotal(response.total ?? responseItems.length)
        })
        .catch(() => setError("Không thể tải dữ liệu. Vui lòng kiểm tra API."))
        .finally(() => setLoading(false))
    }, 180)

    return () => window.clearTimeout(timer)
  }, [config, search])

  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-col gap-4 border-b pb-5 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-primary">
            <ShieldCheck className="size-3.5" />
            Hồ sơ quản lý
          </div>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight">
            {config.title}
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
            {config.description}
          </p>
        </div>
        <div className="flex h-10 w-full items-center gap-2 rounded-md border bg-card px-3 shadow-xs md:w-80">
          <Search className="size-4 text-muted-foreground" />
          <Input
            className="h-9 border-0 bg-transparent px-0 shadow-none focus-visible:ring-0"
            placeholder={config.searchPlaceholder}
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className="rounded-md border bg-card px-2.5 py-1 font-medium">
          {total} hồ sơ
        </span>
        <span className="rounded-md border bg-card px-2.5 py-1 text-muted-foreground">
          Đang hiển thị {items.length}
        </span>
      </div>

      <div className="overflow-hidden rounded-lg border bg-card shadow-xs">
        <div className="grid min-h-11 grid-cols-[1fr_36px] items-center border-b bg-muted/65 px-4 text-xs font-semibold uppercase tracking-wide text-muted-foreground md:grid-cols-[1.5fr_1fr_1fr_44px]">
          <span>Tên</span>
          {config.columns.slice(0, 2).map((column) => (
            <span className="hidden md:block" key={column.label}>
              {column.label}
            </span>
          ))}
          <span />
        </div>

        {loading ? (
          <TableSkeleton />
        ) : error ? (
          <StateText text={error} />
        ) : items.length === 0 ? (
          <StateText text={config.emptyText} />
        ) : (
          items.map((item) => (
            <button
              className="grid w-full grid-cols-[1fr_36px] items-center border-b px-4 py-3.5 text-left transition-colors last:border-b-0 hover:bg-accent/60 md:grid-cols-[1.5fr_1fr_1fr_44px]"
              key={item.id}
              onClick={() => navigate(`${config.basePath}/${item.id}`)}
              type="button"
            >
              <span className="min-w-0">
                <span className="block truncate text-sm font-medium">
                  {config.primary(item)}
                </span>
                <span className="block truncate text-xs text-muted-foreground">
                  ID #{item.id} · {config.secondary(item)}
                </span>
              </span>
              {config.columns.slice(0, 2).map((column) => (
                <span
                  className="hidden truncate text-sm text-muted-foreground md:block"
                  key={column.label}
                >
                  {column.value(item)}
                </span>
              ))}
              <ChevronRight className="ml-auto size-4 text-muted-foreground" />
            </button>
          ))
        )}
      </div>
    </section>
  )
}

export function ResourceDetail<T extends { id: number }>({
  config,
  id,
  navigate,
}: ResourceProps<T> & { id: number }) {
  const [item, setItem] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    setLoading(true)
    setError("")
    config
      .get(id)
      .then(setItem)
      .catch(() => setError("Không tìm thấy hồ sơ hoặc API chưa sẵn sàng."))
      .finally(() => setLoading(false))
  }, [config, id])

  const badge = useMemo(() => (item ? config.badge?.(item) : undefined), [
    config,
    item,
  ])

  return (
    <section className="flex flex-col gap-5">
      <Button
        className="w-fit"
        onClick={() => navigate(config.basePath)}
        size="sm"
        variant="outline"
      >
        <ArrowLeft />
        Quay lại
      </Button>

      {loading ? (
        <DetailSkeleton />
      ) : error || !item ? (
        <StateText text={error || "Không có dữ liệu."} />
      ) : (
        <>
          <div className="rounded-lg border bg-card p-5 shadow-xs">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-primary">
                  {config.singular} #{item.id}
                </p>
                <h1 className="mt-2 text-2xl font-semibold tracking-tight">
                  {config.primary(item)}
                </h1>
                <p className="mt-1 text-sm text-muted-foreground">
                  {config.secondary(item)}
                </p>
              </div>
              {badge ? (
                <span className="w-fit rounded-md border bg-accent px-2.5 py-1 text-sm font-medium text-accent-foreground">
                  {badge}
                </span>
              ) : null}
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            {config.details.map((detail) => (
              <div className="rounded-lg border bg-card p-4 shadow-xs" key={detail.label}>
                <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  {detail.label}
                </div>
                <div className="mt-2 text-sm font-medium leading-6">
                  {detail.value(item)}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  )
}

function TableSkeleton() {
  return (
    <div className="divide-y">
      {[0, 1, 2, 3].map((row) => (
        <div
          className="grid grid-cols-[1fr_36px] gap-4 p-4 md:grid-cols-[1.5fr_1fr_1fr_44px]"
          key={row}
        >
          <Skeleton className="h-4" />
          <Skeleton className="hidden h-4 md:block" />
          <Skeleton className="hidden h-4 md:block" />
          <Skeleton className="h-4" />
        </div>
      ))}
    </div>
  )
}

function DetailSkeleton() {
  return (
    <div className="grid gap-4">
      <Skeleton className="h-28 rounded-lg" />
      <div className="grid gap-4 md:grid-cols-2">
        <Skeleton className="h-24 rounded-lg" />
        <Skeleton className="h-24 rounded-lg" />
      </div>
    </div>
  )
}

function StateText({ text }: { text: string }) {
  return (
    <div className="flex min-h-40 items-center justify-center p-6 text-center text-sm text-muted-foreground">
      {text}
    </div>
  )
}
