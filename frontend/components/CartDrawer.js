import { useCart } from '../context/CartContext'

export default function CartDrawer(){
  const { items, removeItem, clear, total, open, setOpen } = useCart()

  return (
    <div className={`fixed top-0 right-0 h-full w-full sm:w-96 bg-white shadow-xl transform transition-transform ${open ? 'translate-x-0' : 'translate-x-full'} z-50`}>
      <div className="p-6 flex justify-between items-center border-b">
        <h2 className="text-lg font-semibold">Votre panier</h2>
        <button onClick={() => setOpen(false)} className="text-gray-500">Fermer</button>
      </div>
      <div className="p-6 overflow-auto" style={{maxHeight: '70vh'}}>
        {items.length === 0 && <div className="text-gray-500">Votre panier est vide.</div>}
        <div className="space-y-4">
          {items.map(it => (
            <div key={it.product_id} className="flex items-center gap-4">
              <img src={it.image_url || '/placeholder.png'} className="w-16 h-16 object-cover rounded" />
              <div className="flex-1">
                <div className="font-semibold">{it.name}</div>
                <div className="text-sm text-gray-500">{it.quantity} × €{it.price}</div>
              </div>
              <div className="text-right">
                <div className="font-semibold">€{(parseFloat(it.price||0)*it.quantity).toFixed(2)}</div>
                <button onClick={() => removeItem(it.product_id)} className="text-sm text-red-500 mt-1">Supprimer</button>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="p-6 border-t">
        <div className="flex justify-between items-center mb-4">
          <div className="text-sm text-gray-600">Total</div>
          <div className="text-xl font-bold">€{total().toFixed(2)}</div>
        </div>
        <div className="flex gap-3">
          <a href="/checkout" className="flex-1 text-center px-4 py-3 bg-brand text-white rounded">Passer au paiement</a>
          <button onClick={() => clear()} className="px-4 py-3 border rounded">Vider</button>
        </div>
      </div>
    </div>
  )
}
