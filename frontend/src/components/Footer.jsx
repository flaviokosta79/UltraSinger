import { FaGithub, FaMusic, FaHeart, FaTwitter, FaDiscord } from 'react-icons/fa'

const Footer = () => {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    'Produto': [
      { name: 'Início', href: '/' },
      { name: 'Processar', href: '/process' },
      { name: 'Recursos', href: '#features' },
      { name: 'Como Usar', href: '#how-to' },
    ],
    'Recursos': [
      { name: 'Documentação', href: 'https://github.com/flaviokosta79/UltraSinger/blob/main/README.md' },
      { name: 'GitHub', href: 'https://github.com/flaviokosta79/UltraSinger' },
      { name: 'Guias', href: 'https://github.com/flaviokosta79/UltraSinger/tree/main' },
      { name: 'API', href: '#' },
    ],
    'Legal': [
      { name: 'Termos de Uso', href: '#' },
      { name: 'Privacidade', href: '#' },
      { name: 'Licença', href: 'https://github.com/flaviokosta79/UltraSinger/blob/main/LICENSE' },
      { name: 'Cookies', href: '#' },
    ],
  }

  return (
    <footer className="glass border-t border-white/10 mt-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Top Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-12">
          {/* Logo & Description */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <FaMusic className="text-3xl text-primary-500" />
              <span className="text-2xl font-bold text-gradient">
                UltraSinger
              </span>
            </div>
            <p className="text-gray-400 mb-6 max-w-md">
              Crie arquivos UltraStar de karaokê automaticamente com IA.
              Separe vocais, transcreva letras e detecte notas musicais com precisão profissional.
            </p>
            {/* Social Links */}
            <div className="flex space-x-4">
              <a
                href="https://github.com/flaviokosta79/UltraSinger"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-full glass flex items-center justify-center hover:bg-white/10 transition-colors"
              >
                <FaGithub className="text-xl" />
              </a>
              <a
                href="#"
                className="w-10 h-10 rounded-full glass flex items-center justify-center hover:bg-white/10 transition-colors"
              >
                <FaTwitter className="text-xl" />
              </a>
              <a
                href="#"
                className="w-10 h-10 rounded-full glass flex items-center justify-center hover:bg-white/10 transition-colors"
              >
                <FaDiscord className="text-xl" />
              </a>
            </div>
          </div>

          {/* Links Columns */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="font-bold text-white mb-4">{category}</h3>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-gray-400 hover:text-primary-400 transition-colors text-sm"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Section */}
        <div className="pt-8 border-t border-white/10">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-gray-400 text-sm">
              © {currentYear} UltraSinger. Todos os direitos reservados.
            </p>
            <p className="text-gray-400 text-sm flex items-center">
              Feito com <FaHeart className="text-red-500 mx-1" /> por{' '}
              <a
                href="https://github.com/flaviokosta79"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-400 hover:text-primary-300 ml-1"
              >
                Flavio Kosta
              </a>
            </p>
            <div className="flex items-center space-x-4 text-sm">
              <a href="#" className="text-gray-400 hover:text-primary-400 transition-colors">
                Status
              </a>
              <a href="#" className="text-gray-400 hover:text-primary-400 transition-colors">
                Changelog
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
