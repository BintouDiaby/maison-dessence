import '../styles/globals.css'
import Navbar from '../components/Navbar'
import { CartProvider } from '../context/CartContext'

export default function App({ Component, pageProps }) {
  return (
    <CartProvider>
      <Navbar />
      <main className="min-h-screen bg-white">
        <Component {...pageProps} />
      </main>
    </CartProvider>
  )
}
