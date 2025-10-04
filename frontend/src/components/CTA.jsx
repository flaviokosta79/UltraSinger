import { motion } from 'framer-motion'
import { FaRocket, FaArrowRight } from 'react-icons/fa'
import { Link } from 'react-router-dom'

const CTA = () => {
  return (
    <section className="py-20 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600/20 via-dark-900 to-primary-500/20" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full max-w-4xl">
          <div className="absolute inset-0 bg-primary-500/10 rounded-full blur-3xl animate-pulse-slow" />
        </div>
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto"
        >
          {/* Card */}
          <div className="glass rounded-3xl p-8 sm:p-12 md:p-16 text-center relative overflow-hidden">
            {/* Decorative Elements */}
            <div className="absolute top-0 left-0 w-32 h-32 bg-primary-500/20 rounded-full blur-3xl" />
            <div className="absolute bottom-0 right-0 w-32 h-32 bg-primary-600/20 rounded-full blur-3xl" />

            {/* Content */}
            <div className="relative z-10">
              {/* Icon */}
              <motion.div
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 mb-6 glow-primary"
              >
                <FaRocket className="text-3xl text-white" />
              </motion.div>

              {/* Title */}
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
                Pronto para Criar Seu
                <br />
                <span className="text-gradient">Karaokê Perfeito?</span>
              </h2>

              {/* Description */}
              <p className="text-lg text-gray-300 mb-8 max-w-2xl mx-auto">
                Junte-se a milhares de usuários que já criaram mais de 4 milhões de minutos de karaokê profissional
              </p>

              {/* Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Link
                  to="/process"
                  className="group inline-flex items-center gap-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 px-8 py-4 rounded-full font-bold text-lg transition-all duration-200 glow-primary hover:glow-primary-strong"
                >
                  <span>Começar Gratuitamente</span>
                  <FaArrowRight className="group-hover:translate-x-1 transition-transform" />
                </Link>

                <a
                  href="https://github.com/flaviokosta79/UltraSinger"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-3 glass hover:bg-white/10 px-8 py-4 rounded-full font-bold text-lg transition-all duration-200"
                >
                  Ver no GitHub
                </a>
              </div>

              {/* Note */}
              <p className="text-sm text-gray-500 mt-6">
                Grátis e open source • Sem registro necessário • Processamento local
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default CTA
