export default function Hero(){
  return (
    <section className="relative bg-[url('https://images.unsplash.com/photo-1520986606214-8b456906c813?q=80&w=1600&auto=format&fit=crop')] bg-cover bg-center h-[70vh] flex items-center">
      <div className="absolute inset-0 hero-overlay"></div>
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center text-white">
        <h1 className="text-5xl md:text-6xl font-extrabold leading-tight">Maison d'essence</h1>
        <p className="mt-6 text-lg md:text-xl text-gray-100/90 max-w-2xl mx-auto">Découvrez des parfums uniques, faits pour raconter votre histoire. Sélection artisanale, senteurs durables.</p>
        <div className="mt-8 flex justify-center gap-4">
          <a href="/products" className="inline-block bg-white text-brand px-6 py-3 rounded shadow font-semibold">Voir la collection</a>
          <a href="/about" className="inline-block border border-white text-white px-6 py-3 rounded">En savoir plus</a>
        </div>
      </div>
    </section>
  )
}
