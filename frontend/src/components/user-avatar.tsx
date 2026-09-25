import { ShieldCheck, UserRound, UserRoundCheck } from "lucide-react"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import type { AuthRole } from "@/lib/auth-store"

const roleDetails = {
  admin: {
    label: "Quản trị viên",
    icon: ShieldCheck,
  },
  teacher: {
    label: "Giáo viên",
    icon: UserRoundCheck,
  },
} satisfies Record<AuthRole, { label: string; icon: typeof ShieldCheck }>

function getInitials(displayName: string) {
  const words = displayName.trim().split(/\s+/).filter(Boolean)

  if (words.length === 0) {
    return "ND"
  }

  const firstWord = words[0] ?? ""
  const lastWord = words.at(-1) ?? firstWord
  const initials = words.length > 1 ? [firstWord, lastWord] : [firstWord]
  return initials
    .map((word) => Array.from(word)[0] ?? "")
    .join("")
    .toLocaleUpperCase("vi")
    .slice(0, 2)
}

type UserAvatarProps = {
  displayName: string
  role: AuthRole
}

export function UserAvatar({ displayName, role }: UserAvatarProps) {
  const resolvedName = displayName.trim() || "Người dùng"
  const currentRole = roleDetails[role] ?? {
    label: "Vai trò không xác định",
    icon: UserRound,
  }
  const RoleIcon = currentRole.icon
  const accessibleLabel = `${resolvedName}, ${currentRole.label}`

  return (
    <div
      aria-label={accessibleLabel}
      className="flex shrink-0 items-center gap-2.5 rounded-lg px-1.5 py-1"
      title={accessibleLabel}
    >
      <Avatar aria-hidden="true" className="size-9 bg-primary/10 text-primary">
        <AvatarFallback>
          {getInitials(resolvedName)}
          <span className="absolute -right-0.5 -bottom-0.5 flex size-3.5 items-center justify-center rounded-full bg-primary text-primary-foreground ring-2 ring-background">
            <RoleIcon className="size-2" />
          </span>
        </AvatarFallback>
      </Avatar>
      <div className="hidden min-w-0 text-left sm:block">
        <p className="max-w-40 truncate text-sm font-medium leading-4">
          {resolvedName}
        </p>
        <p className="mt-0.5 text-[0.68rem] font-medium tracking-wide text-muted-foreground uppercase">
          {currentRole.label}
        </p>
      </div>
    </div>
  )
}
