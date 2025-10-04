import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FaBars, FaTimes, FaMusic, FaGithub } from 'react-icons/fa'
import { motion, AnimatePresence } from 'framer-motion'

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false)

  const menuItems = [
    { name: 'Início', path: '/' },
    { name: 'Processar', path: '/process' },
    { name: 'Recursos', path: '#features' },
    { name: 'Como Usar', path: '#how-to' },
  ]

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 sm:h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <FaMusic className="text-3xl sm:text-4xl text-primary-500 group-hover:scale-110 transition-transform duration-300" />
              <div className="absolute inset-0 bg-primary-500 blur-xl opacity-30 group-hover:opacity-50 transition-opacity" />
            </div>
            <span className="text-xl sm:text-2xl font-bold text-gradient">
              UltraSinger
            </span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            {menuItems.map((item) => (
              <a
                key={item.name}
                href={item.path}
                className="text-gray-300 hover:text-primary-400 transition-colors duration-200 font-medium"
              >
                {item.name}
              </a>
            ))}
            <a
              href="https://github.com/flaviokosta79/UltraSinger"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 glass px-4 py-2 rounded-full hover:bg-white/10 transition-all duration-200"
            >
              <FaGithub className="text-xl" />
              <span>GitHub</span>
            </a>
            <Link
              to="/process"
              className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 px-6 py-2 rounded-full font-semibold transition-all duration-200 glow-primary hover:glow-primary-strong"
            >
              Começar Grátis
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-gray-300 hover:text-white transition-colors"
          >
            {isOpen ? <FaTimes className="text-2xl" /> : <FaBars className="text-2xl" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass border-t border-white/10 overflow-hidden"
          >
            <div className="container mx-auto px-4 py-4 space-y-4">
              {menuItems.map((item) => (
                <a
                  key={item.name}
                  href={item.path}
                  onClick={() => setIsOpen(false)}
                  className="block text-gray-300 hover:text-primary-400 transition-colors duration-200 font-medium py-2"
                >
                  {item.name}
                </a>
              ))}
              <a
                href="https://github.com/flaviokosta79/UltraSinger"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 glass px-4 py-2 rounded-full hover:bg-white/10 transition-all duration-200 w-full"
              >
                <FaGithub className="text-xl" />
                <span>GitHub</span>
              </a>
              <Link
                to="/process"
                onClick={() => setIsOpen(false)}
                className="block bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 px-6 py-3 rounded-full font-semibold transition-all duration-200 text-center glow-primary"
              >
                Começar Grátis
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}

export default Navbar
