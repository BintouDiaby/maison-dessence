import Link from 'next/link'
import { useCart } from '../context/CartContext'

export default function ProductCard({p}){
  const { addItem } = useCart()
  return (
    <div className="border rounded-lg overflow-hidden shadow-sm hover:shadow-lg transition">
      <div className="h-48 bg-gray-100 flex items-center justify-center">
        <img src={p.image_url || '/placeholder.png'} alt={p.name} className="object-cover h-full w-full" />
      </div>
      <div className="p-4">
        <h3 className="text-lg font-semibold">{p.name}</h3>
        <p className="text-sm text-gray-500 mt-2">{p.family} · {p.concentration || ''}</p>
        <div className="mt-4 flex items-center justify-between">
          <div className="text-lg font-bold">€{p.price}</div>
          <div className="flex items-center gap-3">
            <button onClick={() => addItem(p, 1)} className="text-sm bg-gray-100 px-3 py-1 rounded">Ajouter</button>
            <Link href={`/products/${p.id}`} className="text-sm text-brand underline">Voir</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
