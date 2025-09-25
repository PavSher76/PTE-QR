import { NextRequest, NextResponse } from 'next/server'

const API_BASE_URL = process.env.API_BASE_URL || 'http://backend:8000'

// GET /api/settings - получить настройки системы
export async function GET(request: NextRequest) {
  try {
    const token = request.headers.get('authorization')?.replace('Bearer ', '')
    
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/settings/settings`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorData = await response.json()
      return NextResponse.json({ error: errorData.detail || 'Failed to fetch settings' }, { status: response.status })
    }

    const settings = await response.json()
    return NextResponse.json(settings)
  } catch (error) {
    console.error('Settings API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// PUT /api/settings - обновить настройки системы
export async function PUT(request: NextRequest) {
  try {
    const token = request.headers.get('authorization')?.replace('Bearer ', '')
    
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const settings = await request.json()

    const response = await fetch(`${API_BASE_URL}/api/v1/settings/settings`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    })

    if (!response.ok) {
      const errorData = await response.json()
      return NextResponse.json({ error: errorData.detail || 'Failed to update settings' }, { status: response.status })
    }

    const updatedSettings = await response.json()
    return NextResponse.json(updatedSettings)
  } catch (error) {
    console.error('Settings API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
