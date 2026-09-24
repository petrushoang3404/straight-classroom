import { ArrowLeft, BookOpen, Church } from "lucide-react"
import { useLocation, useNavigate } from "react-router"

import { Button } from "@/components/ui/button"
import { useAuthStore } from "@/lib/auth-store"

export function NotFoundPage({ embedded = false }: { embedded?: boolean }) {
  const navigate = useNavigate()
  const location = useLocation()
  const hasSession = useAuthStore((state) => state.session !== null)
  const destination = hasSession ? "/classrooms" : "/login"

  return (
    <div
      className={
        embedded
          ? "flex min-h-[32rem] items-center justify-center overflow-hidden bg-background px-2 py-6"
          : "relative flex min-h-svh items-center justify-center overflow-hidden bg-background px-4 py-8 sm:px-6"
      }
    >
      {!embedded ? (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,color-mix(in_oklch,var(--primary),transparent_92%),transparent_42%)]"
        />
      ) : null}

      <section className="relative w-full max-w-2xl">
        {!embedded ? (
          <div className="mb-5 flex items-center justify-center gap-3 sm:justify-start">
            <div className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Church className="size-4" />
            </div>
            <div>
              <p className="text-sm font-semibold">Straight Classroom</p>
              <p className="text-xs text-muted-foreground">
                Quản lý lớp học và sinh hoạt cộng đoàn
              </p>
            </div>
          </div>
        ) : null}

        <div className="overflow-hidden rounded-lg border bg-card shadow-sm">
          <div className="flex items-center justify-between border-b bg-muted/25 px-5 py-3 text-xs font-medium tracking-wide text-muted-foreground uppercase">
            <span>Lỗi điều hướng</span>
            <span>404</span>
          </div>

          <div className="px-5 py-10 text-center sm:px-10 sm:py-12">
            <div className="mx-auto flex size-14 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Church className="size-6" />
            </div>
            <p className="mt-6 text-xs font-semibold tracking-[0.16em] text-primary uppercase">
              Không tìm thấy trang
            </p>
            <h1 className="mx-auto mt-2 max-w-lg text-2xl font-semibold tracking-tight sm:text-3xl">
              Ước dẫn chưa dẫn được đến trang này
            </h1>
            <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-muted-foreground">
              Đường dẫn không tồn tại hoặc nội dung đã được chuyển đi. Hãy quay
              lại khu vực quản lý để tiếp tục công việc.
            </p>

            <div className="mt-7 flex justify-center">
              <Button
                className="min-w-44"
                onClick={() => navigate(destination, { replace: true })}
              >
                <ArrowLeft />
                {hasSession ? "Về trang quản lý" : "Đến trang đăng nhập"}
              </Button>
            </div>

            <div className="mx-auto mt-8 max-w-lg rounded-lg border bg-muted/25 px-4 py-3 text-left">
              <div className="flex items-start gap-3">
                <BookOpen className="mt-0.5 size-4 shrink-0 text-primary" />
                <div className="min-w-0">
                  <p className="text-xs font-medium">Đường dẫn không tìm thấy</p>
                  <code className="mt-1 block break-all text-xs leading-5 text-muted-foreground">
                    {location.pathname}
                  </code>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
