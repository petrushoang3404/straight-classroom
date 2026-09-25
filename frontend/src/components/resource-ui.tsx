import {
  useEffect,
  useState,
  type ComponentType,
  type ReactNode,
} from "react"
import {
  ChevronRight,
  Plus,
  Search,
  ShieldCheck,
} from "lucide-react"
import type { FieldValues } from "react-hook-form"
import { useNavigate } from "react-router"

import {
  DetailErrorState,
  DetailPageSkeleton,
} from "@/components/detail-ui"
import type { ResourceFormProps } from "@/components/resource-form-dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "@/components/ui/toast"
import type { PaginatedResponse } from "@/lib/models"

export type ResourceConfig<T extends { id: number }, TValues extends FieldValues> = {
  title: string
  singular: string
  description: string
  searchPlaceholder: string
  basePath: string
  emptyText: string
  list: (params: { limit?: number; offset?: number; search?: string }) => Promise<PaginatedResponse<T>>
  get: (id: number) => Promise<T>
  create: (values: TValues) => Promise<T>
  update: (id: number, values: TValues) => Promise<T>
  form: {
    component: ComponentType<ResourceFormProps<T, TValues>>
    createLabel: string
  }
  columns: Array<{
    label: string
    value: (item: T) => string
  }>
  primary: (item: T) => string
  secondary: (item: T) => string
  badge?: (item: T) => string
}

type ResourceEditor<T> =
  | { mode: "create" }
  | {
      mode: "update"
      item: T
    }

export function ResourceList<
  T extends { id: number },
  TValues extends FieldValues,
>({ config }: { config: ResourceConfig<T, TValues> }) {
  const navigate = useNavigate()
  const [items, setItems] = useState<T[]>([])
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [editor, setEditor] = useState<ResourceEditor<T> | null>(null)
  const FormComponent = config.form.component

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
        .catch(() => {
          setError("Không thể tải dữ liệu. Vui lòng kiểm tra API.")
          toast.error(
            "Không thể tải dữ liệu",
            `Danh sách ${config.title.toLowerCase()} chưa sẵn sàng.`
          )
        })
        .finally(() => setLoading(false))
    }, 180)

    return () => window.clearTimeout(timer)
  }, [config, search])

  const handleFormSuccess = (savedItem: T) => {
    if (editor?.mode === "update") {
      setItems((current) =>
        current.map((item) => (item.id === savedItem.id ? savedItem : item))
      )
    } else {
      setItems((current) => [savedItem, ...current])
      setTotal((current) => current + 1)
    }
    setEditor(null)
  }

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
        <div className="flex w-full flex-col gap-2 sm:flex-row md:w-auto">
          <div className="flex h-10 w-full items-center gap-2 rounded-lg border bg-card px-3 shadow-xs sm:w-72">
            <Search className="size-4 text-muted-foreground" />
            <Input
              className="h-9 border-0 bg-transparent px-0 shadow-none focus-visible:ring-0"
              placeholder={config.searchPlaceholder}
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
          <Button
            className="h-10 w-full sm:w-auto"
            onClick={() => setEditor({ mode: "create" })}
            type="button"
          >
            <Plus />
            {config.form.createLabel}
          </Button>
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

      {editor ? (
        <FormComponent
          initialItem={editor.mode === "update" ? editor.item : null}
          onOpenChange={(open) => {
            if (!open) setEditor(null)
          }}
          onSuccess={handleFormSuccess}
          open
          save={(values) =>
            editor.mode === "update"
              ? config.update(editor.item.id, values)
              : config.create(values)
          }
        />
      ) : null}
    </section>
  )
}

export function ResourceDetail<
  T extends { id: number },
  TValues extends FieldValues,
>({
  children,
  config,
  id,
}: {
  children: (item: T, actions: { onEdit: () => void }) => ReactNode
  config: ResourceConfig<T, TValues>
  id: number
}) {
  const navigate = useNavigate()
  const [item, setItem] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [editor, setEditor] = useState<ResourceEditor<T> | null>(null)
  const FormComponent = config.form.component

  useEffect(() => {
    let active = true

    setLoading(true)
    setError("")
    setItem(null)
    config
      .get(id)
      .then((response) => {
        if (active) setItem(response)
      })
      .catch(() => {
        if (!active) return
        setError("Không tìm thấy hồ sơ hoặc API chưa sẵn sàng.")
        toast.error(
          "Không thể mở hồ sơ",
          `${config.singular} #${id} không tồn tại hoặc API chưa sẵn sàng.`
        )
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [config, id])

  if (loading) {
    return <DetailPageSkeleton />
  }

  if (error || !item) {
    return (
      <DetailErrorState
        description={error || "Không có dữ liệu để hiển thị."}
        onBack={() => navigate(config.basePath)}
        title="Không thể mở hồ sơ"
      />
    )
  }

  return (
    <>
      {children(item, {
        onEdit: () => setEditor({ mode: "update", item }),
      })}

      {editor ? (
        <FormComponent
          initialItem={editor.mode === "update" ? editor.item : null}
          onOpenChange={(open) => {
            if (!open) setEditor(null)
          }}
          onSuccess={(savedItem) => {
            setItem(savedItem)
            setEditor(null)
          }}
          open
          save={(values) =>
            editor.mode === "update"
              ? config.update(editor.item.id, values)
              : config.create(values)
          }
        />
      ) : null}
    </>
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

function StateText({ text }: { text: string }) {
  return (
    <div className="flex min-h-40 items-center justify-center p-6 text-center text-sm text-muted-foreground">
      {text}
    </div>
  )
}
