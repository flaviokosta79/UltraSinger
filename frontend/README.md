# UltraSinger Frontend

Frontend moderno e responsivo para o UltraSinger, criado com React, Vite e Tailwind CSS.

## 🚀 Tecnologias

- **React 18** - Framework JavaScript
- **Vite** - Build tool ultrarrápido
- **Tailwind CSS** - Framework CSS utilitário
- **Framer Motion** - Animações fluidas
- **React Router** - Roteamento
- **React Icons** - Ícones

## 📦 Instalação

```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

## 🎨 Design

O frontend foi inspirado no design moderno de interfaces web, com:

- 🌙 Modo escuro por padrão
- ✨ Animações suaves com Framer Motion
- 📱 Totalmente responsivo
- 🎭 Efeitos glassmorphism
- 🌈 Gradientes vibrantes
- ⚡ Performance otimizada

## 📂 Estrutura

```
frontend/
├── src/
│   ├── components/          # Componentes reutilizáveis
│   │   ├── Navbar.jsx
│   │   ├── Hero.jsx
│   │   ├── Features.jsx
│   │   ├── HowItWorks.jsx
│   │   ├── Stats.jsx
│   │   ├── Testimonials.jsx
│   │   ├── CTA.jsx
│   │   └── Footer.jsx
│   ├── pages/              # Páginas
│   │   ├── HomePage.jsx
│   │   └── ProcessPage.jsx
│   ├── App.jsx             # Componente principal
│   ├── main.jsx            # Entry point
│   └── index.css           # Estilos globais
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🎯 Funcionalidades

### Página Inicial
- Hero section com upload de arquivos
- Grid de recursos/features
- Como funciona (4 passos)
- Estatísticas impressionantes
- Depoimentos de usuários
- Call-to-action

### Página de Processamento
- Seleção de jobs configuráveis
- Preview do arquivo selecionado
- Interface visual para jobs
- Indicadores visuais de recomendação

## 🔗 Integração com Backend

O frontend está preparado para se conectar com um backend Flask/FastAPI:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
    }
  }
}
```

## 🎨 Customização

### Cores
Edite `tailwind.config.js` para alterar o esquema de cores:

```javascript
theme: {
  extend: {
    colors: {
      primary: { ... },
      dark: { ... }
    }
  }
}
```

### Animações
Adicione novas animações em `tailwind.config.js`:

```javascript
animation: {
  'custom': 'custom 2s ease-in-out infinite',
}
```

## 📝 TODO

- [ ] Implementar backend API (Flask/FastAPI)
- [ ] Sistema de fila de processamento
- [ ] Progress bar em tempo real
- [ ] Download de resultados
- [ ] Histórico de processamentos
- [ ] Sistema de autenticação (opcional)
- [ ] Dark/Light mode toggle
- [ ] Internacionalização (i18n)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é parte do UltraSinger e segue a mesma licença.

## 👨‍💻 Autor

**Flavio Kosta**
- GitHub: [@flaviokosta79](https://github.com/flaviokosta79)

---

Feito com ❤️ e ☕
