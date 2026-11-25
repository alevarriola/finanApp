import { NextRequest, NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  const token = request.cookies.get("access_token")?.value;

  if (!token) {
    const signInUrl = new URL("/sign-in", request.url);
    return NextResponse.redirect(signInUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/wallets/:path*",
    "/transactions/:path*",
    "/sharing/:path*",
    "/settings/:path*",
    "/chat/:path*",
  ],
};
