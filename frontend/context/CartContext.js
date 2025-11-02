import { createContext, useContext, useEffect, useState } from 'react'

const CartContext = createContext()

export function useCart(){
  return useContext(CartContext)
}

export function CartProvider({ children }){
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    try{
      const raw = localStorage.getItem('md_cart')
      if(raw) setItems(JSON.parse(raw))
    }catch(e){
      setItems([])
    }
  }, [])

  useEffect(() => {
    try{
      localStorage.setItem('md_cart', JSON.stringify(items))
    }catch(e){}
  }, [items])

  function addItem(product, quantity = 1){
    // Bloquer l'ajout au panier pour les visiteurs non connectés
    if(typeof window !== 'undefined'){
      const token = localStorage.getItem('md_access_token')
      if(!token){
        // rediriger vers la page de connexion
        window.alert('Connectez-vous pour ajouter au panier')
        window.location.href = '/login.html'
        return
      }
    }

    setItems(prev => {
      const idx = prev.findIndex(i => i.product_id === product.id)
      if(idx !== -1){
        const copy = [...prev]
        copy[idx].quantity += quantity
        return copy
      }
      return [...prev, { product_id: product.id, name: product.name, price: product.price, image_url: product.image_url, quantity }]
    })
    setOpen(true)
  }

  function removeItem(product_id){
    setItems(prev => prev.filter(i => i.product_id !== product_id))
  }

  function clear(){
    setItems([])
  }

  function total(){
    return items.reduce((s, it) => s + (parseFloat(it.price || 0) * it.quantity), 0)
  }

  return (
    <CartContext.Provider value={{ items, addItem, removeItem, clear, total, open, setOpen }}>
      {children}
    </CartContext.Provider>
  )
}
