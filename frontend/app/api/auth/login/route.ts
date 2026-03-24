import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const LOGIN_MUTATION = `
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      accessToken
      refreshToken
      user {
        id
        email
        name
      }
    }
  }
`;

const BACKEND_URL = process.env.BACKEND_GRAPHQL_URL ?? "http://localhost:8000/graphql";

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();

  const response = await fetch(BACKEND_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: LOGIN_MUTATION,
      variables: { input: { email, password } },
    }),
  });

  const json = await response.json();

  if (json.errors) {
    return NextResponse.json({ error: json.errors[0].message }, { status: 401 });
  }

  const { accessToken, refreshToken, user } = json.data.login;

  const cookieStore = await cookies();
  const isProduction = process.env.NODE_ENV === "production";

  cookieStore.set("access_token", accessToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: isProduction,
    maxAge: 60 * 60 * 24,
    path: "/",
  });

  cookieStore.set("refresh_token", refreshToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: isProduction,
    maxAge: 60 * 60 * 24 * 7,
    path: "/",
  });

  return NextResponse.json({ user });
}
