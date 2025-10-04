import { motion } from 'framer-motion'
import { FaStar, FaQuoteLeft } from 'react-icons/fa'

const Testimonials = () => {
  const testimonials = [
    {
      name: 'Carlos Silva',
      role: 'Criador de Conteúdo Musical',
      avatar: '👨‍🎤',
      rating: 5,
      text: 'Como criador de conteúdo, encontrar um software removedor de vocais confiável foi crucial para meus projetos. O UltraSinger não apenas remove vocais de forma limpa, mas também oferece várias opções de exportação. Tornou-se uma ferramenta inestimável no meu processo criativo.'
    },
    {
      name: 'Ana Beatriz',
      role: 'Entusiasta de Karaokê',
      avatar: '🎤',
      rating: 5,
      text: 'Estou absolutamente impressionada com a simplicidade e a eficácia do UltraSinger. Ele cria arquivos de karaokê sem esforço, elevando minha experiência a um nível totalmente novo. É uma ferramenta essencial para qualquer amante da música!'
    },
    {
      name: 'Roberto Santos',
      role: 'DJ Profissional',
      avatar: '🎧',
      rating: 5,
      text: 'A separação vocal é incrivelmente precisa! Uso o UltraSinger para criar remixes e versions instrumentais das minhas músicas favoritas. A qualidade é profissional e o processamento é surpreendentemente rápido com minha RTX 3080.'
    },
    {
      name: 'Marina Costa',
      role: 'Professora de Música',
      avatar: '🎼',
      rating: 5,
      text: 'Ferramenta perfeita para ensino! Consigo criar material didático personalizado removendo vocais para que meus alunos pratiquem. A transcrição automática de letras economiza horas do meu tempo.'
    }
  ]

  return (
    <section className="py-20 relative">
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
            Avaliações de <span className="text-gradient">Usuários</span>
          </h2>
          <p className="text-lg text-gray-300 max-w-3xl mx-auto">
            Veja o que nossos usuários têm a dizer
          </p>
        </motion.div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="glass rounded-2xl p-8 hover:bg-white/10 transition-all duration-300 relative"
            >
              {/* Quote Icon */}
              <FaQuoteLeft className="absolute top-6 right-6 text-4xl text-primary-500/20" />

              {/* Stars */}
              <div className="flex gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <FaStar key={i} className="text-yellow-400 text-lg" />
                ))}
              </div>

              {/* Text */}
              <p className="text-gray-300 mb-6 leading-relaxed">
                {testimonial.text}
              </p>

              {/* Author */}
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-2xl">
                  {testimonial.avatar}
                </div>
                <div>
                  <div className="font-bold text-white">{testimonial.name}</div>
                  <div className="text-sm text-gray-400">{testimonial.role}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Testimonials
