import { type FormEvent, useState } from "react"
import {
  Eye,
  EyeOff,
  GraduationCap,
  KeyRound,
  Loader2,
  LockKeyhole,
  ShieldCheck,
  UserRound,
} from "lucide-react"
import { useLocation, useNavigate } from "react-router"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from "@/components/ui/toast"
import { api } from "@/lib/api"
import { useAuthStore } from "@/lib/auth-store"

export function LoginPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState<"password" | "google" | null>(null)

  const redirectTo =
    typeof location.state === "object" &&
    location.state !== null &&
    "redirectTo" in location.state &&
    typeof location.state.redirectTo === "string"
      ? location.state.redirectTo
      : "/classrooms"

  const submitPasswordLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!username.trim() || !password.trim()) {
      toast.error(
        "Thiếu thông tin đăng nhập",
        "Vui lòng nhập username và password."
      )
      return
    }

    try {
      setLoading("password")
      const session = await api.auth.login({
        username: username.trim(),
        password,
      })

      login(session)
      navigate(redirectTo, { replace: true })
      toast.success("Đăng nhập thành công", `Chào mừng ${session.displayName}.`)
    } catch {
      toast.error(
        "Không thể đăng nhập",
        "Vui lòng kiểm tra lại tài khoản hoặc kết nối hệ thống."
      )
    } finally {
      setLoading(null)
    }
  }

  const continueWithGoogle = async () => {
    try {
      setLoading("google")
      const session = await api.auth.google()

      login(session)
      navigate(redirectTo, { replace: true })
      toast.success("Google OAuth thành công", `Chào mừng ${session.displayName}.`)
    } catch {
      toast.error(
        "Không thể dùng Google",
        "Google OAuth chưa sẵn sàng hoặc kết nối đang gặp lỗi."
      )
    } finally {
      setLoading(null)
    }
  }

  const isSubmitting = loading !== null

  return (
    <main className="min-h-screen bg-background px-4 py-6 text-foreground md:px-6">
      <div className="mx-auto grid min-h-[calc(100vh-3rem)] w-full max-w-6xl overflow-hidden rounded-lg border bg-card shadow-sm md:grid-cols-[0.95fr_1.05fr]">
        <section className="flex flex-col justify-between border-b bg-muted/35 p-6 md:border-b-0 md:border-r md:p-8">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-md bg-primary text-primary-foreground">
                <GraduationCap className="size-5" />
              </div>
              <div className="min-w-0">
                <p className="truncate text-base font-semibold">
                  Straight Classroom
                </p>
                <p className="truncate text-sm text-muted-foreground">
                  Giáo lý và sinh hoạt lớp
                </p>
              </div>
            </div>

            <div className="mt-16 max-w-md">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-primary">
                <ShieldCheck className="size-3.5" />
                Cổng quản trị
              </div>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight">
                Đăng nhập hệ thống lớp học
              </h1>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">
                Không gian quản lý hồ sơ lớp, giáo viên và học sinh cho cộng đoàn
                nhà thờ.
              </p>
            </div>
          </div>

          <div className="mt-12 grid gap-3 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <LockKeyhole className="size-4 text-primary" />
              <span>Phiên đăng nhập được lưu trên thiết bị này.</span>
            </div>
            <div className="flex items-center gap-2">
              <KeyRound className="size-4 text-primary" />
              <span>Hỗ trợ username/password và Google OAuth.</span>
            </div>
          </div>
        </section>

        <section className="flex items-center justify-center p-6 md:p-10">
          <div className="w-full max-w-[25rem]">
            <div className="mb-7">
              <h2 className="text-xl font-semibold tracking-tight">Đăng nhập</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Sử dụng tài khoản được cấp bởi ban điều hành.
              </p>
            </div>

            <form className="grid gap-4" onSubmit={submitPasswordLogin}>
              <div className="grid gap-2">
                <label className="text-sm font-medium" htmlFor="username">
                  Username
                </label>
                <div className="relative">
                  <UserRound className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    autoComplete="username"
                    className="h-10 pl-9"
                    disabled={isSubmitting}
                    id="username"
                    onChange={(event) => setUsername(event.target.value)}
                    placeholder="ten.dang.nhap"
                    value={username}
                  />
                </div>
              </div>

              <div className="grid gap-2">
                <label className="text-sm font-medium" htmlFor="password">
                  Password
                </label>
                <div className="relative">
                  <LockKeyhole className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    autoComplete="current-password"
                    className="h-10 pl-9 pr-10"
                    disabled={isSubmitting}
                    id="password"
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Nhập password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                  />
                  <button
                    aria-label={showPassword ? "Ẩn password" : "Hiện password"}
                    className="absolute right-1.5 top-1/2 flex size-7 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                    disabled={isSubmitting}
                    onClick={() => setShowPassword((current) => !current)}
                    type="button"
                  >
                    {showPassword ? (
                      <EyeOff className="size-4" />
                    ) : (
                      <Eye className="size-4" />
                    )}
                  </button>
                </div>
              </div>

              <Button className="mt-1 h-10" disabled={isSubmitting} type="submit">
                {loading === "password" ? (
                  <Loader2 className="animate-spin" />
                ) : (
                  <KeyRound />
                )}
                Đăng nhập
              </Button>
            </form>

            <div className="my-6 grid grid-cols-[1fr_auto_1fr] items-center gap-3 text-xs uppercase tracking-wide text-muted-foreground">
              <span className="h-px bg-border" />
              <span>Hoặc</span>
              <span className="h-px bg-border" />
            </div>

            <Button
              className="h-10 w-full"
              disabled={isSubmitting}
              onClick={continueWithGoogle}
              type="button"
              variant="outline"
            >
              {loading === "google" ? (
                <Loader2 className="animate-spin" />
              ) : (
                <span className="flex size-4 items-center justify-center rounded-sm border text-[0.7rem] font-semibold">
                  G
                </span>
              )}
              Tiếp tục với Google
            </Button>
          </div>
        </section>
      </div>
    </main>
  )
}
