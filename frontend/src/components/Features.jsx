import { motion } from 'framer-motion'
import {
  FaMicrophone,
  FaMusic,
  FaRobot,
  FaVideo,
  FaCloud,
  FaBolt,
  FaFileAudio,
  FaChartLine
} from 'react-icons/fa'

const Features = () => {
  const features = [
    {
      icon: <FaMicrophone />,
      title: 'Separação Vocal Avançada',
      description: 'Separa vocais do instrumental usando Demucs com precisão de até 95%',
      color: 'from-pink-500 to-rose-500'
    },
    {
      icon: <FaMusic />,
      title: 'Transcrição Automática',
      description: 'Whisper AI transcreve letras automaticamente em mais de 90 idiomas',
      color: 'from-purple-500 to-indigo-500'
    },
    {
      icon: <FaRobot />,
      title: 'Detecção de Pitch com IA',
      description: 'Crepe detecta notas musicais com precisão profissional',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: <FaVideo />,
      title: 'Suporte YouTube',
      description: 'Copie e cole qualquer URL do YouTube para processar diretamente',
      color: 'from-red-500 to-orange-500'
    },
    {
      icon: <FaCloud />,
      title: 'Processamento Local',
      description: 'Todo o processamento acontece no seu PC com GPU - privacidade total',
      color: 'from-teal-500 to-green-500'
    },
    {
      icon: <FaBolt />,
      title: 'Processamento Rápido',
      description: 'GPU acelerada para processamento até 10x mais rápido',
      color: 'from-yellow-500 to-amber-500'
    },
    {
      icon: <FaFileAudio />,
      title: 'Múltiplos Formatos',
      description: 'Suporta MP3, WAV, FLAC, M4A, MP4, MOV e mais',
      color: 'from-violet-500 to-purple-500'
    },
    {
      icon: <FaChartLine />,
      title: 'Jobs Configuráveis',
      description: 'Escolha exatamente quais etapas processar - total controle',
      color: 'from-emerald-500 to-green-500'
    }
  ]

  return (
    <section id="features" className="py-20 relative">
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-dark-900 via-dark-800 to-dark-900" />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            Recursos do <span className="text-gradient">Melhor Criador de Karaokê</span>
          </h2>
          <p className="text-lg text-gray-300 max-w-3xl mx-auto">
            Crie arquivos UltraStar profissionais com tecnologias de IA de ponta
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="glass rounded-xl p-6 hover:bg-white/10 transition-all duration-300 group cursor-pointer"
            >
              {/* Icon */}
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-white text-2xl mb-4 group-hover:scale-110 transition-transform duration-300`}>
                {feature.icon}
              </div>

              {/* Content */}
              <h3 className="text-xl font-bold mb-2 group-hover:text-primary-400 transition-colors">
                {feature.title}
              </h3>
              <p className="text-gray-400 text-sm">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-12"
        >
          <a
            href="/process"
            className="inline-block bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 px-8 py-4 rounded-full font-bold text-lg transition-all duration-200 glow-primary hover:glow-primary-strong"
          >
            Começar Gratuitamente
          </a>
        </motion.div>
      </div>
    </section>
  )
}

export default Features
