import axios from 'axios'
import Footer from '../../components/Footer'
import ProductCard from '../../components/ProductCard'
import AddToCartBtn from '../../components/AddToCartBtn'

export default function ProductDetail({product, similar}){
  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2">
          <img src={product.image_url || '/placeholder.png'} alt={product.name} className="w-full h-96 object-cover rounded-md shadow" />
          <h1 className="text-3xl font-extrabold mt-6">{product.name}</h1>
          <p className="mt-4 text-gray-700">{product.description}</p>
          <div className="mt-6 flex items-center justify-between">
            <div className="text-2xl font-bold">€{product.price}</div>
            <AddToCartBtn product={product} />
          </div>
        </div>
        <aside>
          <h3 className="text-xl font-semibold">Produits similaires</h3>
          <div className="mt-4 space-y-4">
            {similar.map(s => <ProductCard key={s.id} p={s} />)}
          </div>
        </aside>
      </div>
      <Footer />
    </div>
  )
}

export async function getServerSideProps(ctx){
  const { id } = ctx.params
  try{
    const base = process.env.BACKEND_URL ? `${process.env.BACKEND_URL}/api` : 'http://127.0.0.1:8000/api'
    const [pRes, sRes] = await Promise.all([
      axios.get(`${base}/products/${id}/`),
      axios.get(`${base}/recommender/products/${id}/?k=3`)
    ])
    return { props: { product: pRes.data, similar: sRes.data } }
  }catch(e){
    return { props: { product: {}, similar: [] } }
  }
}
