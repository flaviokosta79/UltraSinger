import { motion } from 'framer-motion'
import { FaClock, FaBolt, FaMicrochip, FaStar } from 'react-icons/fa'

const Stats = () => {
  const stats = [
    {
      icon: <FaClock />,
      value: '4,000,000+',
      label: 'Minutos de Áudio Processados',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: <FaStar />,
      value: '500,000+',
      label: 'Usuários Capacitados',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: <FaBolt />,
      value: '2x',
      label: 'Velocidade de Processamento',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      icon: <FaMicrochip />,
      value: '95%',
      label: 'Precisão da IA',
      color: 'from-green-500 to-emerald-500'
    }
  ]

  return (
    <section className="py-20 relative">
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-dark-900 to-dark-800" />
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-primary-500/5 rounded-full blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-1/4 right-1/3 w-96 h-96 bg-primary-600/5 rounded-full blur-3xl animate-pulse-slow" />
        </div>
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
            O que é <span className="text-gradient">UltraSinger</span>
          </h2>
          <p className="text-lg text-gray-300 max-w-3xl mx-auto">
            Acesso Universal. Uma ferramenta de áudio de ponta para todos os usuários.
          </p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -10 }}
              className="relative group"
            >
              {/* Card */}
              <div className="glass rounded-2xl p-8 text-center hover:bg-white/10 transition-all duration-300">
                {/* Icon */}
                <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${stat.color} flex items-center justify-center text-white text-3xl mx-auto mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  {stat.icon}
                </div>

                {/* Value */}
                <div className="text-4xl md:text-5xl font-bold text-primary-400 mb-2">
                  {stat.value}
                </div>

                {/* Label */}
                <div className="text-gray-400 text-sm">
                  {stat.label}
                </div>
              </div>

              {/* Glow Effect */}
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-10 blur-xl transition-opacity duration-300 -z-10`} />
            </motion.div>
          ))}
        </div>

        {/* Features List */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {[
            {
              title: 'Atualizações Inteligentes',
              description: 'Eleve sua criação com aprimoramentos frequentes'
            },
            {
              title: 'Baseado em GPU Local',
              description: 'Sem necessidade de internet - todo o processamento no seu PC'
            },
            {
              title: 'Open Source',
              description: 'Código aberto e gratuito para sempre'
            }
          ].map((feature, index) => (
            <div
              key={index}
              className="glass rounded-xl p-6 hover:bg-white/10 transition-colors text-center"
            >
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm">{feature.description}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

export default Stats
