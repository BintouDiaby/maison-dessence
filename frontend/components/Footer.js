export default function Footer(){
  return (
    <footer className="bg-gray-50 border-t mt-12">
      <div className="max-w-7xl mx-auto px-6 py-10 text-sm text-gray-600 flex justify-between">
        <div>© {new Date().getFullYear()} Maison d'essence</div>
        <div>Designed with care · <a href="/about" className="underline">About</a></div>
      </div>
    </footer>
  )
}
