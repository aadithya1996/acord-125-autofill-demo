import { NextResponse } from "next/server"

export async function POST(request: Request) {
  try {
    const body = await request.json()

    // Forward to Python backend
    const res = await fetch("http://localhost:8000/generate-acord", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })

    if (!res.ok) {
      const text = await res.text()
      return NextResponse.json({ error: text }, { status: res.status })
    }

    const blob = await res.blob()
    return new NextResponse(blob, {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": 'attachment; filename="ACORD_125_Filled.pdf"',
      },
    })
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to generate PDF. Ensure the Python backend is running on port 8000." },
      { status: 500 }
    )
  }
}
