"use client";

import { useState, forwardRef } from "react";
import { Eye, EyeOff } from "lucide-react";

interface PasswordInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  hasError?: boolean;
}

export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ hasError, className, ...props }, ref) => {
    const [show, setShow] = useState(false);

    return (
      <div className="relative">
        <input
          ref={ref}
          type={show ? "text" : "password"}
          className={`w-full px-3 py-2 pr-10 rounded-lg border text-sm outline-none focus:ring-2 ${className ?? ""}`}
          style={{
            borderColor: hasError ? "#dc2626" : "var(--border)",
            backgroundColor: "var(--background)",
            color: "var(--foreground)",
          }}
          {...props}
        />
        <button
          type="button"
          onClick={() => setShow((s) => !s)}
          className="absolute right-2.5 top-1/2 -translate-y-1/2 opacity-50 hover:opacity-80 transition-opacity"
          style={{ color: "var(--foreground)" }}
          tabIndex={-1}
        >
          {show ? <EyeOff size={16} /> : <Eye size={16} />}
        </button>
      </div>
    );
  }
);

PasswordInput.displayName = "PasswordInput";
