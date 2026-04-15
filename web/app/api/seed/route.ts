import { NextResponse } from "next/server";
import { MOCK_7DAYS } from "@/lib/mock-data";

export async function POST() {
  try {
    const res = await fetch("http://localhost:8700/seed-demo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ days: MOCK_7DAYS }),
    });
    if (!res.ok) {
      const text = await res.text();
      return NextResponse.json(
        { error: `Backend error: ${text}` },
        { status: res.status },
      );
    }
    const data = await res.json();
    return NextResponse.json(data);
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 },
    );
  }
}
