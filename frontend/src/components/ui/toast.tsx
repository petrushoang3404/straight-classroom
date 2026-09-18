import * as React from "react"
import { Toast as ToastPrimitive } from "@base-ui/react/toast"
import { CheckCircle2, Info, TriangleAlert, X, XCircle } from "lucide-react"

import { cn } from "@/lib/utils"

type ToastType = "success" | "error" | "info" | "warning"

type ToastData = {
  type?: ToastType
}

type ToastOptions = {
  title: React.ReactNode
  description?: React.ReactNode
  type?: ToastType
  timeout?: number
}

const manager = ToastPrimitive.createToastManager<ToastData>()

const iconMap = {
  success: CheckCircle2,
  error: XCircle,
  info: Info,
  warning: TriangleAlert,
} satisfies Record<ToastType, React.ComponentType<{ className?: string }>>

const typeClasses = {
  success: "border-primary/25 bg-card text-card-foreground",
  error: "border-destructive/35 bg-card text-card-foreground",
  info: "border-border bg-card text-card-foreground",
  warning: "border-amber-500/35 bg-card text-card-foreground",
} satisfies Record<ToastType, string>

const iconClasses = {
  success: "text-primary",
  error: "text-destructive",
  info: "text-muted-foreground",
  warning: "text-amber-600",
} satisfies Record<ToastType, string>

export const toast = {
  show({ title, description, type = "info", timeout }: ToastOptions) {
    return manager.add({
      title,
      description,
      timeout,
      type,
      data: { type },
      priority: type === "error" ? "high" : "low",
    })
  },
  success(title: React.ReactNode, description?: React.ReactNode) {
    return toast.show({ title, description, type: "success" })
  },
  error(title: React.ReactNode, description?: React.ReactNode) {
    return toast.show({ title, description, type: "error" })
  },
  info(title: React.ReactNode, description?: React.ReactNode) {
    return toast.show({ title, description, type: "info" })
  },
  warning(title: React.ReactNode, description?: React.ReactNode) {
    return toast.show({ title, description, type: "warning" })
  },
  close(id?: string) {
    manager.close(id)
  },
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  return (
    <ToastPrimitive.Provider limit={4} timeout={4600} toastManager={manager}>
      {children}
      <Toaster />
    </ToastPrimitive.Provider>
  )
}

function Toaster() {
  const { toasts } = ToastPrimitive.useToastManager<ToastData>()

  return (
    <ToastPrimitive.Portal>
      <ToastPrimitive.Viewport className="fixed bottom-4 right-4 z-50 w-[calc(100vw-2rem)] outline-none sm:bottom-6 sm:right-6 sm:w-[24rem]">
        {toasts.map((item) => {
          const type = item.data?.type ?? (item.type as ToastType | undefined) ?? "info"
          const Icon = iconMap[type]

          return (
            <ToastPrimitive.Root
              className={cn(
                "[--gap:0.75rem] [--peek:0.75rem] [--scale:calc(max(0,1-(var(--toast-index)*0.05)))] [--shrink:calc(1-var(--scale))] [--height:var(--toast-frontmost-height,var(--toast-height))] [--offset-y:calc(var(--toast-offset-y)*-1+calc(var(--toast-index)*var(--gap)*-1)+var(--toast-swipe-movement-y))]",
                "absolute bottom-0 right-0 z-[calc(1000-var(--toast-index))] w-full origin-bottom select-none rounded-lg border shadow-lg shadow-foreground/10",
                "[transform:translateX(var(--toast-swipe-movement-x))_translateY(calc(var(--toast-swipe-movement-y)-(var(--toast-index)*var(--peek))-(var(--shrink)*var(--height))))_scale(var(--scale))]",
                "[transition:transform_0.45s_cubic-bezier(0.22,1,0.36,1),opacity_0.25s,height_0.15s]",
                "data-expanded:[transform:translateX(var(--toast-swipe-movement-x))_translateY(calc(var(--offset-y)))] data-expanded:h-[var(--toast-height)]",
                "data-limited:opacity-0 data-starting-style:[transform:translateY(140%)] data-ending-style:opacity-0",
                "[&[data-ending-style]:not([data-limited]):not([data-swipe-direction])]:[transform:translateY(140%)]",
                typeClasses[type]
              )}
              key={item.id}
              toast={item}
            >
              <ToastPrimitive.Content className="flex items-start gap-3 overflow-hidden p-4 transition-opacity duration-200 data-behind:opacity-0 data-expanded:opacity-100">
                <Icon className={cn("mt-0.5 size-4 shrink-0", iconClasses[type])} />
                <div className="min-w-0 flex-1">
                  <ToastPrimitive.Title className="text-sm font-semibold leading-5" />
                  <ToastPrimitive.Description className="mt-1 text-sm leading-5 text-muted-foreground" />
                </div>
                <ToastPrimitive.Close
                  aria-label="Đóng thông báo"
                  className="flex size-7 shrink-0 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                  <X className="size-4" />
                </ToastPrimitive.Close>
              </ToastPrimitive.Content>
            </ToastPrimitive.Root>
          )
        })}
      </ToastPrimitive.Viewport>
    </ToastPrimitive.Portal>
  )
}
