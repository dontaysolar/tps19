import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const apiUrl = process.env.ORGANISM_API_URL || 'http://localhost:5000'
  const path = request.nextUrl.searchParams.get('path') || 'vitals'
  
  try {
    const response = await fetch(`${apiUrl}/api/${path}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('API Proxy Error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch from organism API' },
      { status: 500 }
    )
  }
}
