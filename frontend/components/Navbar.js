import Link from 'next/link'
import { useCart } from '../context/CartContext'
import CartDrawer from './CartDrawer'

export default function Navbar(){
  const { items, setOpen } = useCart()
  const count = items.reduce((s, it) => s + it.quantity, 0)

  return (
    <>
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-6">
              <Link href="/" className="text-2xl font-bold text-brand">Maison d'essence</Link>
              <Link href="/products" className="text-sm text-gray-600 hover:text-gray-900">Produits</Link>
              <Link href="/about" className="text-sm text-gray-600 hover:text-gray-900">À propos</Link>
            </div>
            <div className="flex items-center gap-4">
              <a className="text-sm text-gray-600 hover:text-gray-900">Connexion</a>
              <button onClick={() => setOpen(true)} className="relative px-4 py-2 bg-brand text-white rounded-md">
                Panier
                {count > 0 && <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">{count}</span>}
              </button>
            </div>
          </div>
        </div>
      </nav>
      <CartDrawer />
    </>
  )
}
