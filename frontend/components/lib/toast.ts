import { toast } from "sonner";

export function showSuccess(message: string) {
  toast.success(message);
}

export function showError(error: unknown) {
  const message =
    error instanceof Error ? error.message : "Unexpected error occurred";
  toast.error(message);
}

export function showInfo(message: string) {
  toast.info(message);
}
