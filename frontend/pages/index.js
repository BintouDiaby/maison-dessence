import Hero from '../components/Hero'
import Footer from '../components/Footer'
import ProductCard from '../components/ProductCard'
import axios from 'axios'

export default function Home({products}){
  return (
    <>
      <Hero />
      <section className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-extrabold mb-6">Nos coups de cœur</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(p => (
            <ProductCard key={p.id} p={p} />
          ))}
        </div>
      </section>
      <Footer />
    </>
  )
}

export async function getServerSideProps(){
  try{
    const res = await axios.get(process.env.BACKEND_URL ? `${process.env.BACKEND_URL}/api/products/` : 'http://127.0.0.1:8000/api/products/')
    return { props: { products: res.data || [] } }
  }catch(e){
    return { props: { products: [] } }
  }
}
