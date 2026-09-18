import { useMemo } from "react"
import {
  GraduationCap,
  LogOut,
  type LucideIcon,
  School,
  Settings,
  UserRoundCheck,
  UsersRound,
} from "lucide-react"
import {
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarSeparator,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { toast } from "@/components/ui/toast"
import { ClassroomDetail, ClassroomsList } from "@/routes/classrooms"
import { LoginPage } from "@/routes/login"
import { StudentDetail, StudentsList } from "@/routes/students"
import { TeacherDetail, TeachersList } from "@/routes/teachers"
import { useAuthStore } from "@/lib/auth-store"

type NavRoute = {
  id: "classrooms" | "teachers" | "students"
  path: string
  title: string
  subtitle: string
  icon: LucideIcon
}

const routes: NavRoute[] = [
  {
    id: "classrooms",
    path: "/classrooms",
    title: "Lớp học",
    subtitle: "Phòng học và sức chứa",
    icon: School,
  },
  {
    id: "teachers",
    path: "/teachers",
    title: "Giáo viên",
    subtitle: "Phụ trách và chuyên môn",
    icon: UserRoundCheck,
  },
  {
    id: "students",
    path: "/students",
    title: "Học sinh",
    subtitle: "Hồ sơ và lớp học",
    icon: UsersRound,
  },
]

function App() {
  return (
    <Routes>
      <Route element={<PublicRoute />} path="/login" />
      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route element={<Navigate replace to="/classrooms" />} index />
          <Route element={<ClassroomsList />} path="classrooms" />
          <Route element={<ClassroomDetailRoute />} path="classrooms/:id" />
          <Route element={<TeachersList />} path="teachers" />
          <Route element={<TeacherDetailRoute />} path="teachers/:id" />
          <Route element={<StudentsList />} path="students" />
          <Route element={<StudentDetailRoute />} path="students/:id" />
          <Route element={<Navigate replace to="/classrooms" />} path="*" />
        </Route>
      </Route>
    </Routes>
  )
}

function PublicRoute() {
  const session = useAuthStore((state) => state.session)

  return session ? <Navigate replace to="/classrooms" /> : <LoginPage />
}

function RequireAuth() {
  const session = useAuthStore((state) => state.session)
  const location = useLocation()

  if (!session) {
    return (
      <Navigate
        replace
        state={{ redirectTo: `${location.pathname}${location.search}` }}
        to="/login"
      />
    )
  }

  return <Outlet />
}

function AppLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const session = useAuthStore((state) => state.session)
  const logout = useAuthStore((state) => state.logout)

  const activeRoute = useMemo(
    () =>
      routes.find((route) => location.pathname.startsWith(route.path)) ??
      routes[0],
    [location.pathname]
  )

  const handleLogout = () => {
    logout()
    navigate("/login", { replace: true })
    toast.info("Đã đăng xuất", "Phiên làm việc trên thiết bị này đã kết thúc.")
  }

  if (!session) {
    return null
  }

  return (
    <SidebarProvider>
      <Sidebar collapsible="icon">
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg" tooltip="Straight Classroom">
                <div className="flex size-8 items-center justify-center rounded-md bg-sidebar-primary text-sidebar-primary-foreground">
                  <GraduationCap className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">
                    Straight Classroom
                  </span>
                  <span className="truncate text-xs text-sidebar-foreground/70">
                    Giáo lý và sinh hoạt lớp
                  </span>
                </div>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

        <SidebarSeparator />

        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Quản lý</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {routes.map((route) => (
                  <SidebarMenuItem key={route.id}>
                    <SidebarMenuButton
                      isActive={activeRoute.id === route.id}
                      onClick={() => navigate(route.path)}
                      tooltip={route.title}
                    >
                      <route.icon />
                      <span>{route.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter>
          <div className="grid gap-1 px-2 py-1 text-xs group-data-[collapsible=icon]:hidden">
            <span className="truncate font-medium">{session.displayName}</span>
            <span className="truncate text-sidebar-foreground/65">
              {session.username}
            </span>
          </div>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton tooltip="Cài đặt">
                <Settings />
                <span>Cài đặt</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <SidebarMenuButton onClick={handleLogout} tooltip="Đăng xuất">
                <LogOut />
                <span>Đăng xuất</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>

      <SidebarInset>
        <header className="flex h-14 shrink-0 items-center gap-3 border-b bg-background/95 px-4">
          <SidebarTrigger />
          <div className="min-w-0">
            <h1 className="truncate text-base font-semibold">
              {activeRoute.title}
            </h1>
            <p className="truncate text-sm text-muted-foreground">
              {activeRoute.subtitle}
            </p>
          </div>
        </header>

        <main className="flex flex-1 flex-col p-4 md:p-6">
          <div className="mx-auto w-full max-w-6xl">
            <Outlet />
          </div>
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}

function ClassroomDetailRoute() {
  const id = usePositiveId()
  return id ? <ClassroomDetail id={id} /> : <Navigate replace to="/classrooms" />
}

function TeacherDetailRoute() {
  const id = usePositiveId()
  return id ? <TeacherDetail id={id} /> : <Navigate replace to="/teachers" />
}

function StudentDetailRoute() {
  const id = usePositiveId()
  return id ? <StudentDetail id={id} /> : <Navigate replace to="/students" />
}

function usePositiveId() {
  const { id } = useParams()
  const numericId = Number(id)

  return Number.isFinite(numericId) && numericId > 0 ? numericId : null
}

export default App
