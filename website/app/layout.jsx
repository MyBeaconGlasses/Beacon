import {Inter} from 'next/font/google'
import './globals.css'
import Nav from '../components/Nav'

const inter = Inter({subsets: ['latin']})

export const metadata = {
  title: 'Beacon',
  description: 'The OS for Everything Around You',
}

export default function RootLayout({children}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#070707]`}>
        <div className="relative">
          <Nav />
        </div>
        {children}
      </body>
    </html>
  )
}
