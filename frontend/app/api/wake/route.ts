import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_GRAPHQL_URL ?? "http://localhost:8000/graphql";
const HEALTH_URL = new URL("/api/health", BACKEND_URL);

// The free backend instance can take up to a minute to wake up.
export const maxDuration = 60;

export async function GET() {
  try {
    const response = await fetch(HEALTH_URL, {
      cache: "no-store",
      signal: AbortSignal.timeout(55_000),
    });
    return NextResponse.json({ ok: response.ok }, { status: response.ok ? 200 : 503 });
  } catch {
    return NextResponse.json({ ok: false }, { status: 503 });
  }
}
