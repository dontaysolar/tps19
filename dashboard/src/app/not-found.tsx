import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-primary-500 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-100 mb-4">Page Not Found</h2>
        <p className="text-gray-400 mb-8">The page you're looking for doesn't exist.</p>
        <Link 
          href="/"
          className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Return to Dashboard
        </Link>
      </div>
    </div>
  )
}
