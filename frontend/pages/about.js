import Footer from '../components/Footer'

export default function About(){
  return (
    <div className="max-w-4xl mx-auto px-6 py-20">
      <h1 className="text-4xl font-extrabold mb-6">À propos — Maison d'essence</h1>
      <p className="text-lg text-gray-700 leading-relaxed">Nous sommes une maison de parfums indépendante dédiée à la création de fragrances narratives, fabriquées avec soin et responsabilité. Chaque parfum de notre collection est conçu pour évoquer une mémoire et célébrer l'art des senteurs.</p>
      <section className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h3 className="text-xl font-semibold">Notre mission</h3>
          <p className="mt-2 text-gray-600">Proposer des parfums de qualité, durables et accessibles, tout en soutenant des producteurs responsables.</p>
        </div>
        <div>
          <h3 className="text-xl font-semibold">Artisanat</h3>
          <p className="mt-2 text-gray-600">Nous travaillons avec des nez et des fournisseurs soigneusement sélectionnés. Nos compositions privilégient la qualité des matières premières.</p>
        </div>
      </section>
      <section className="mt-12">
        <h3 className="text-xl font-semibold">Contact</h3>
        <p className="mt-2 text-gray-600">contact@maison-dessence.test</p>
      </section>
      <Footer />
    </div>
  )
}
