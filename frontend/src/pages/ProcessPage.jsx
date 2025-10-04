import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  FaMicrophone,
  FaMusic,
  FaRobot,
  FaChartLine,
  FaFileAudio,
  FaCut,
  FaCheck,
  FaTimes
} from 'react-icons/fa'

const ProcessPage = () => {
  const location = useLocation()
  const { file, url } = location.state || {}

  const [selectedJobs, setSelectedJobs] = useState({
    vocal_separation: true,
    transcription: true,
    pitch_detection: true,
    midi: false,
    plot: false,
    hyphenation: true,
    karaoke: true
  })

  const jobs = [
    {
      id: 'vocal_separation',
      icon: <FaMicrophone />,
      title: 'Separação Vocal',
      description: 'Separa vocais do instrumental com Demucs',
      recommended: true
    },
    {
      id: 'transcription',
      icon: <FaMusic />,
      title: 'Transcrição',
      description: 'Transcreve letras automaticamente com Whisper',
      recommended: true
    },
    {
      id: 'pitch_detection',
      icon: <FaRobot />,
      title: 'Detecção de Pitch',
      description: 'Detecta notas musicais com Crepe',
      recommended: true
    },
    {
      id: 'midi',
      icon: <FaFileAudio />,
      title: 'Arquivo MIDI',
      description: 'Gera arquivo MIDI com as notas',
      recommended: false
    },
    {
      id: 'plot',
      icon: <FaChartLine />,
      title: 'Gráficos',
      description: 'Cria visualizações de pitch e timing',
      recommended: false
    },
    {
      id: 'hyphenation',
      icon: <FaCut />,
      title: 'Hifenização',
      description: 'Divide palavras em sílabas',
      recommended: true
    },
    {
      id: 'karaoke',
      icon: <FaMusic />,
      title: 'Arquivo Karaokê',
      description: 'Cria arquivo UltraStar.txt',
      recommended: true
    }
  ]

  const toggleJob = (jobId) => {
    setSelectedJobs(prev => ({
      ...prev,
      [jobId]: !prev[jobId]
    }))
  }

  const handleProcess = () => {
    // TODO: Integrate with backend API
    console.log('Processing with jobs:', selectedJobs)
    console.log('File:', file)
    console.log('URL:', url)
  }

  return (
    <div className="min-h-screen pt-24 pb-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl sm:text-5xl font-bold mb-4">
              Configure o <span className="text-gradient">Processamento</span>
            </h1>
            <p className="text-lg text-gray-300">
              Escolha quais jobs deseja executar
            </p>
          </motion.div>

          {/* File Info */}
          {(file || url) && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="glass rounded-xl p-6 mb-8"
            >
              <h3 className="text-xl font-bold mb-2">Arquivo Selecionado:</h3>
              <p className="text-gray-300">
                {file ? file.name : url}
              </p>
            </motion.div>
          )}

          {/* Jobs Grid */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8"
          >
            {jobs.map((job, index) => (
              <motion.button
                key={job.id}
                onClick={() => toggleJob(job.id)}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`glass rounded-xl p-6 text-left transition-all duration-200 relative ${
                  selectedJobs[job.id]
                    ? 'bg-primary-500/20 border-2 border-primary-500'
                    : 'border-2 border-transparent hover:bg-white/10'
                }`}
              >
                {/* Recommended Badge */}
                {job.recommended && (
                  <div className="absolute top-2 right-2 bg-primary-500 text-white text-xs px-2 py-1 rounded-full font-semibold">
                    Recomendado
                  </div>
                )}

                {/* Check Icon */}
                <div className={`absolute top-6 right-6 w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                  selectedJobs[job.id]
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-700 text-gray-400'
                }`}>
                  {selectedJobs[job.id] ? <FaCheck /> : <FaTimes />}
                </div>

                {/* Icon */}
                <div className="text-3xl text-primary-400 mb-4">
                  {job.icon}
                </div>

                {/* Content */}
                <h3 className="text-lg font-bold mb-2">{job.title}</h3>
                <p className="text-sm text-gray-400">{job.description}</p>
              </motion.button>
            ))}
          </motion.div>

          {/* Process Button */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="text-center"
          >
            <button
              onClick={handleProcess}
              disabled={!file && !url}
              className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed px-12 py-4 rounded-xl font-bold text-lg transition-all duration-200 glow-primary hover:glow-primary-strong"
            >
              Iniciar Processamento
            </button>
            <p className="text-sm text-gray-500 mt-4">
              O processamento será executado localmente no seu PC
            </p>
          </motion.div>

          {/* Info Card */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="glass rounded-xl p-6 mt-8"
          >
            <h3 className="text-xl font-bold mb-4">📋 Informações</h3>
            <ul className="space-y-2 text-gray-300">
              <li>• Jobs recomendados garantem melhor qualidade</li>
              <li>• Processamento local garante privacidade total</li>
              <li>• GPU acelerada para resultados mais rápidos</li>
              <li>• Tempo estimado: 5-10 minutos para uma música de 3-4 min</li>
            </ul>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default ProcessPage
