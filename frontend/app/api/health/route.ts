import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Check if the application is running
    const health = {
      status: 'healthy',
      service: 'PTE-QR Frontend',
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    }

    return NextResponse.json(health, { status: 200 })
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        service: 'PTE-QR Frontend',
        error: 'Internal server error',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}
