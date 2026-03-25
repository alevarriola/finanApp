import { NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function POST() {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;
  if (!token) {
    return NextResponse.redirect(new URL("/sign-in", process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000"));
  }

  await fetch(
    process.env.BACKEND_GRAPHQL_URL ?? "http://localhost:8000/graphql",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        query: "mutation { sendVerificationEmail }",
      }),
    }
  );

  return NextResponse.redirect(
    new URL("/dashboard", process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000")
  );
}
