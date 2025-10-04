import { motion } from 'framer-motion'
import { FaPlay, FaYoutube, FaUpload } from 'react-icons/fa'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const Hero = () => {
  const [activeTab, setActiveTab] = useState('local')
  const [file, setFile] = useState(null)
  const [url, setUrl] = useState('')
  const navigate = useNavigate()

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      setFile(droppedFile)
    }
  }

  const handleSubmit = () => {
    if (activeTab === 'local' && file) {
      navigate('/process', { state: { file } })
    } else if (activeTab === 'url' && url) {
      navigate('/process', { state: { url } })
    }
  }

  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20 pb-10 overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary-600/10 rounded-full blur-3xl animate-pulse-slow animation-delay-1000" />

        {/* Wave SVG */}
        <svg
          className="absolute bottom-0 left-0 w-full h-64 opacity-10"
          viewBox="0 0 1440 320"
          preserveAspectRatio="none"
        >
          <path
            fill="currentColor"
            className="text-primary-500 wave"
            d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,149.3C960,160,1056,160,1152,138.7C1248,117,1344,75,1392,53.3L1440,32L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
          />
        </svg>
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-5xl mx-auto">
          {/* Title Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-6">
              Criador de Karaokê <br />
              <span className="text-gradient">com Inteligência Artificial</span>
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto">
              Transforme qualquer música em arquivos UltraStar automaticamente com a poderosa tecnologia de IA
            </p>
          </motion.div>

          {/* Upload Card */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass rounded-2xl p-6 sm:p-8 glow-primary"
          >
            {/* Tabs */}
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setActiveTab('local')}
                className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-semibold transition-all duration-200 ${
                  activeTab === 'local'
                    ? 'bg-primary-500 text-white'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                }`}
              >
                <FaUpload />
                Arquivo Local
              </button>
              <button
                onClick={() => setActiveTab('url')}
                className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-semibold transition-all duration-200 ${
                  activeTab === 'url'
                    ? 'bg-primary-500 text-white'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                }`}
              >
                <FaYoutube />
                Link do YouTube
              </button>
            </div>

            {/* Upload Area */}
            {activeTab === 'local' ? (
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className="border-2 border-dashed border-primary-500/30 rounded-xl p-12 text-center hover:border-primary-500/50 transition-colors cursor-pointer bg-white/5"
              >
                <input
                  type="file"
                  id="file-upload"
                  accept="audio/*,video/*,.mp3,.mp4,.wav,.flac,.m4a"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <FaUpload className="text-5xl text-primary-500 mx-auto mb-4" />
                  <p className="text-xl font-semibold mb-2">
                    {file ? file.name : 'Escolher arquivo'}
                  </p>
                  <p className="text-gray-400">
                    ou solte aqui
                  </p>
                  <p className="text-sm text-gray-500 mt-4">
                    Duração máxima: 60 min | Tamanho máximo: 1GB
                  </p>
                </label>
              </div>
            ) : (
              <div className="space-y-4">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Cole o link do YouTube aqui..."
                  className="w-full px-6 py-4 rounded-xl glass border border-white/10 focus:border-primary-500 focus:outline-none text-white placeholder-gray-400 transition-colors"
                />
                <p className="text-sm text-gray-500 text-center">
                  Exemplo: https://www.youtube.com/watch?v=...
                </p>
              </div>
            )}

            {/* Process Button */}
            <button
              onClick={handleSubmit}
              disabled={!file && !url}
              className="w-full mt-6 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed px-8 py-4 rounded-xl font-bold text-lg transition-all duration-200 flex items-center justify-center gap-3 glow-primary hover:glow-primary-strong"
            >
              <FaPlay />
              Processar Agora
            </button>

            <p className="text-center text-sm text-gray-500 mt-4">
              Ao enviar um arquivo, você concorda com nossos{' '}
              <a href="#" className="text-primary-400 hover:text-primary-300">
                Termos de Serviço
              </a>
            </p>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8"
          >
            {[
              { label: 'Minutos Processados', value: '4,000,000+' },
              { label: 'Usuários Ativos', value: '500,000+' },
              { label: 'Precisão IA', value: '95%' },
              { label: 'Velocidade', value: '2x' },
            ].map((stat, index) => (
              <div
                key={index}
                className="glass rounded-xl p-4 text-center hover:bg-white/10 transition-colors"
              >
                <div className="text-2xl sm:text-3xl font-bold text-primary-400 mb-1">
                  {stat.value}
                </div>
                <div className="text-xs sm:text-sm text-gray-400">
                  {stat.label}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  )
}

export default Hero
