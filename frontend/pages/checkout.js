import { useCart } from '../context/CartContext'
import { useState } from 'react'

export default function Checkout(){
  const { items, total, clear } = useCart()
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  async function payMock(){
    setLoading(true)
    // fake delay
    await new Promise(r => setTimeout(r, 1000))
    setLoading(false)
    setDone(true)
    clear()
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-2xl font-extrabold mb-6">Paiement</h1>
      {done ? (
        <div className="p-8 bg-green-50 rounded">Merci — votre paiement factice a été traité avec succès.</div>
      ) : (
        <>
          <div className="space-y-4">
            {items.map(it => (
              <div key={it.product_id} className="flex justify-between">
                <div>{it.name} × {it.quantity}</div>
                <div>€{(parseFloat(it.price||0)*it.quantity).toFixed(2)}</div>
              </div>
            ))}
          </div>
          <div className="mt-6 flex justify-between items-center">
            <div className="text-lg font-semibold">Total</div>
            <div className="text-2xl font-bold">€{total().toFixed(2)}</div>
          </div>
          <div className="mt-6 flex gap-4">
            <button onClick={payMock} disabled={loading || items.length===0} className="px-6 py-3 bg-brand text-white rounded">Payer (test)</button>
            <a href="/" className="px-6 py-3 border rounded">Continuer vos achats</a>
          </div>
        </>
      )}
    </div>
  )
}
