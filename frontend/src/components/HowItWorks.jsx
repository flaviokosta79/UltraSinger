import { motion } from 'framer-motion'
import { FaUpload, FaCog, FaDownload, FaCheck } from 'react-icons/fa'

const HowItWorks = () => {
  const steps = [
    {
      icon: <FaUpload />,
      title: 'Envie sua Música',
      description: 'Faça upload de um arquivo de áudio/vídeo ou cole um link do YouTube',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: <FaCog />,
      title: 'Configure os Jobs',
      description: 'Escolha quais processos executar: separação vocal, transcrição, pitch detection, etc.',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: <FaCheck />,
      title: 'Processamento IA',
      description: 'A IA processa automaticamente usando Whisper, Demucs e Crepe no seu GPU',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: <FaDownload />,
      title: 'Baixe o Resultado',
      description: 'Receba arquivo UltraStar completo com letras sincronizadas e notas musicais',
      color: 'from-orange-500 to-red-500'
    }
  ]

  return (
    <section id="how-to" className="py-20 relative">
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-dark-800 to-dark-900" />
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
            Como <span className="text-gradient">Funciona</span>
          </h2>
          <p className="text-lg text-gray-300 max-w-3xl mx-auto">
            4 passos simples para criar seu karaokê profissional
          </p>
        </motion.div>

        {/* Steps */}
        <div className="max-w-6xl mx-auto">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              className="relative"
            >
              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute left-1/2 top-32 w-0.5 h-32 bg-gradient-to-b from-primary-500 to-transparent -translate-x-1/2" />
              )}

              <div className={`flex flex-col md:flex-row items-center gap-8 mb-16 ${
                index % 2 === 1 ? 'md:flex-row-reverse' : ''
              }`}>
                {/* Icon Circle */}
                <div className="flex-shrink-0 relative">
                  <div className={`w-24 h-24 rounded-full bg-gradient-to-br ${step.color} flex items-center justify-center text-white text-3xl glow-primary`}>
                    {step.icon}
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white font-bold text-sm">
                    {index + 1}
                  </div>
                </div>

                {/* Content */}
                <div className={`flex-1 glass rounded-xl p-6 ${
                  index % 2 === 1 ? 'md:text-right' : ''
                }`}>
                  <h3 className="text-2xl font-bold mb-2">{step.title}</h3>
                  <p className="text-gray-400">{step.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default HowItWorks
