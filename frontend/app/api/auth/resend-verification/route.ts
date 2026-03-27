import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function POST(request: NextRequest) {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;
  if (!token) {
    return NextResponse.redirect(new URL("/sign-in", request.url));
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

  return NextResponse.redirect(new URL("/dashboard", request.url));
}
