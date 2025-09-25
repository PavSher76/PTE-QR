import { NextRequest, NextResponse } from 'next/server'

const API_BASE_URL = process.env.API_BASE_URL || 'http://backend:8000'

export async function GET(request: NextRequest) {
  try {
    const token = request.headers.get('Authorization')

    if (!token) {
      return NextResponse.json({ detail: 'Not authenticated' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const filename = searchParams.get('filename')

    if (!filename) {
      return NextResponse.json({ detail: 'Filename parameter is required' }, { status: 400 })
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/pdf/download/${filename}`, {
      method: 'GET',
      headers: {
        'Authorization': token,
      },
    })

    if (response.ok) {
      const blob = await response.blob()
      return new NextResponse(blob, {
        status: 200,
        headers: {
          'Content-Type': 'application/pdf',
          'Content-Disposition': `attachment; filename="${filename}"`,
        },
      })
    } else {
      const errorData = await response.json()
      return NextResponse.json(errorData, { status: response.status })
    }
  } catch (error) {
    console.error('Error proxying PDF download:', error)
    return NextResponse.json({ detail: 'Internal server error' }, { status: 500 })
  }
}
