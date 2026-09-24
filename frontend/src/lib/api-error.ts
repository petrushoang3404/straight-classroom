import axios from "axios"

type ApiErrorPayload = {
  detail?: string | Array<{ msg?: string }>
}

export function getApiErrorMessage(error: unknown, fallback: string) {
  if (!axios.isAxiosError<ApiErrorPayload>(error)) {
    return fallback
  }

  const detail = error.response?.data?.detail

  if (typeof detail === "string" && detail.trim()) {
    return detail
  }

  if (Array.isArray(detail)) {
    const messages = detail.flatMap(({ msg }) =>
      typeof msg === "string" && msg.trim() ? [msg] : []
    )
    if (messages.length > 0) {
      return messages.join("; ")
    }
  }

  return fallback
}
