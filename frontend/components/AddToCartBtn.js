import { useCart } from '../context/CartContext'

export default function AddToCartBtn({ product }){
  const { addItem } = useCart()
  return (
    <button onClick={() => addItem(product, 1)} className="px-4 py-2 bg-brand text-white rounded">Ajouter au panier</button>
  )
}
