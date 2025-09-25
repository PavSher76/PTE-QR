import { NextResponse } from 'next/server'

const API_BASE_URL = process.env.API_BASE_URL || 'http://backend:8000'

export async function POST(request: Request) {
  try {
    const token = request.headers.get('Authorization')?.split(' ')[1]

    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get form data from request
    const formData = await request.formData()
    
    // Forward the request to the backend API
    const response = await fetch(`${API_BASE_URL}/api/v1/pdf/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    })

    if (response.ok) {
      const data = await response.json()
      return NextResponse.json(data)
    } else {
      const errorData = await response.json()
      return NextResponse.json(errorData, { status: response.status })
    }
  } catch (error) {
    console.error('PDF upload error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
