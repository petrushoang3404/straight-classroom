import { useEffect, useMemo, useState } from "react"
import {
  GraduationCap,
  type LucideIcon,
  School,
  Settings,
  UserRoundCheck,
  UsersRound,
} from "lucide-react"

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
import { ClassroomDetail, ClassroomsList } from "@/routes/classrooms"
import { StudentDetail, StudentsList } from "@/routes/students"
import { TeacherDetail, TeachersList } from "@/routes/teachers"

type Route = {
  id: "classrooms" | "teachers" | "students"
  path: string
  title: string
  subtitle: string
  icon: LucideIcon
}

const routes: Route[] = [
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
  const [path, setPath] = useState(() => normalizePath(window.location.pathname))

  useEffect(() => {
    const handlePopState = () => setPath(normalizePath(window.location.pathname))
    window.addEventListener("popstate", handlePopState)
    return () => window.removeEventListener("popstate", handlePopState)
  }, [])

  const activeRoute = useMemo(
    () => routes.find((route) => path.startsWith(route.path)) ?? routes[0],
    [path]
  )

  const navigate = (nextPath: string) => {
    const normalizedPath = normalizePath(nextPath)
    window.history.pushState({}, "", normalizedPath)
    setPath(normalizedPath)
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
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton tooltip="Cài đặt">
                <Settings />
                <span>Cài đặt</span>
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
            {renderRoute(path, navigate)}
          </div>
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}

function renderRoute(path: string, navigate: (path: string) => void) {
  const [resource, id] = path.split("/").filter(Boolean)
  const numericId = Number(id)

  if (resource === "teachers") {
    return Number.isFinite(numericId) && numericId > 0 ? (
      <TeacherDetail id={numericId} navigate={navigate} />
    ) : (
      <TeachersList navigate={navigate} />
    )
  }

  if (resource === "students") {
    return Number.isFinite(numericId) && numericId > 0 ? (
      <StudentDetail id={numericId} navigate={navigate} />
    ) : (
      <StudentsList navigate={navigate} />
    )
  }

  if (resource === "classrooms") {
    return Number.isFinite(numericId) && numericId > 0 ? (
      <ClassroomDetail id={numericId} navigate={navigate} />
    ) : (
      <ClassroomsList navigate={navigate} />
    )
  }

  return <ClassroomsList navigate={navigate} />
}

function normalizePath(path: string) {
  if (path === "/") {
    return "/classrooms"
  }

  return path.endsWith("/") && path.length > 1 ? path.slice(0, -1) : path
}

export default App
