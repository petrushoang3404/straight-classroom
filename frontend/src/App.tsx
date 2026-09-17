import {
  BookOpen,
  CalendarDays,
  GraduationCap,
  LayoutDashboard,
  Settings,
  Users,
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

const menuItems = [
  { title: "Dashboard", icon: LayoutDashboard, active: true },
  { title: "Lớp học", icon: GraduationCap },
  { title: "Giáo viên", icon: Users },
  { title: "Tài liệu", icon: BookOpen },
  { title: "Lịch học", icon: CalendarDays },
]

function App() {
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
                    Learning workspace
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
                {menuItems.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      isActive={item.active}
                      tooltip={item.title}
                    >
                      <item.icon />
                      <span>{item.title}</span>
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
        <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger />
          <div>
            <h1 className="text-base font-semibold">Classroom Overview</h1>
            <p className="text-sm text-muted-foreground">
              Demo sidebar shadcn trong App.tsx
            </p>
          </div>
        </header>

        <main className="flex flex-1 flex-col gap-4 p-4">
          <section className="grid gap-4 md:grid-cols-3">
            {[
              ["12", "Lớp đang mở"],
              ["248", "Học viên"],
              ["18", "Giáo viên"],
            ].map(([value, label]) => (
              <div
                key={label}
                className="rounded-lg border bg-card p-4 text-card-foreground"
              >
                <div className="text-2xl font-semibold">{value}</div>
                <div className="text-sm text-muted-foreground">{label}</div>
              </div>
            ))}
          </section>

          <section className="min-h-80 rounded-lg border bg-card p-4 text-card-foreground">
            <h2 className="text-lg font-semibold">Hoạt động gần đây</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Nhấn nút sidebar hoặc dùng Ctrl+B / Cmd+B để thử collapse.
            </p>
          </section>
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default App
