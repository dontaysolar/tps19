export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500 mb-4"></div>
        <p className="text-gray-400">Loading dashboard...</p>
      </div>
    </div>
  )
}
