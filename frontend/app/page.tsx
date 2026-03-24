import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold" style={{ color: "var(--primary)" }}>
          FinanApp
        </h1>
        <p className="text-lg" style={{ color: "var(--muted-foreground)" }}>
          Gestión de finanzas personales
        </p>
        <div className="flex gap-4 justify-center pt-4">
          <Link
            href="/sign-in"
            className="px-6 py-2 rounded-lg font-medium"
            style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          >
            Iniciar sesión
          </Link>
          <Link
            href="/sign-up"
            className="px-6 py-2 rounded-lg font-medium border"
            style={{ borderColor: "var(--primary)", color: "var(--primary)" }}
          >
            Registrarse
          </Link>
        </div>
      </div>
    </div>
  );
}
