# 🎨 Guia Completo do Frontend UltraSinger

## 📋 Visão Geral

Frontend moderno inspirado no design do EaseUS Vocal Remover, mas com identidade própria e funcionalidades específicas do UltraSinger.

## ✨ Características Principais

### 🎯 Design
- **Tema Escuro Moderno**: Fundo dark-900 com efeitos glassmorphism
- **Gradientes Vibrantes**: Primary green (#22c55e) em gradientes suaves
- **Animações Fluidas**: Framer Motion para transições e micro-interações
- **Responsivo**: Mobile-first, adaptável a todos os tamanhos de tela
- **Acessível**: Cores com bom contraste, navegação por teclado

### 🔧 Tecnologias Utilizadas

```json
{
  "React": "18.3.1",
  "Vite": "5.4.1",
  "Tailwind CSS": "3.4.11",
  "Framer Motion": "11.5.4",
  "React Router": "6.26.2",
  "React Icons": "5.3.0"
}
```

## 🚀 Como Executar

### 1️⃣ Instalar Dependências

```bash
cd E:\VSCode\Projects\UltraSinger\frontend
npm install
```

### 2️⃣ Iniciar Servidor de Desenvolvimento

```bash
npm run dev
```

Acesse: http://localhost:3000

### 3️⃣ Build para Produção

```bash
npm run build
npm run preview
```

## 📂 Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx          # Navegação fixa no topo
│   │   ├── Hero.jsx            # Seção principal com upload
│   │   ├── Features.jsx        # Grid de 8 recursos
│   │   ├── HowItWorks.jsx      # 4 passos do processo
│   │   ├── Stats.jsx           # Estatísticas impressionantes
│   │   ├── Testimonials.jsx    # 4 depoimentos de usuários
│   │   ├── CTA.jsx             # Call-to-action final
│   │   └── Footer.jsx          # Rodapé com links
│   ├── pages/
│   │   ├── HomePage.jsx        # Landing page completa
│   │   └── ProcessPage.jsx     # Configuração de jobs
│   ├── App.jsx                 # Roteamento principal
│   ├── main.jsx                # Entry point
│   └── index.css               # Estilos globais + Tailwind
├── public/                     # Assets estáticos
├── index.html                  # HTML base
├── package.json                # Dependências
├── vite.config.js              # Config Vite + proxy
├── tailwind.config.js          # Config Tailwind
└── postcss.config.js           # Config PostCSS
```

## 🎨 Componentes Detalhados

### 1. Navbar
**Arquivo**: `src/components/Navbar.jsx`

**Funcionalidades**:
- Logo com ícone musical animado
- Menu desktop com links
- Menu mobile hamburger com animação
- Botão GitHub
- Botão CTA "Começar Grátis"
- Glass effect com backdrop blur
- Responsivo com breakpoints

**Props**: Nenhuma (standalone)

---

### 2. Hero
**Arquivo**: `src/components/Hero.jsx`

**Funcionalidades**:
- Título impactante com gradiente
- Tabs: "Arquivo Local" vs "Link do YouTube"
- Upload drag & drop de arquivos
- Input para URL do YouTube
- Validação de tamanho (1GB) e duração (60min)
- Background animado com waves SVG
- 4 cards de estatísticas
- Redirecionamento para /process

**State**:
```javascript
const [activeTab, setActiveTab] = useState('local')
const [file, setFile] = useState(null)
const [url, setUrl] = useState('')
```

---

### 3. Features
**Arquivo**: `src/components/Features.jsx`

**Funcionalidades**:
- Grid 4 colunas (responsivo: 1/2/4)
- 8 cards de recursos com ícones
- Hover effect com elevação
- Gradientes únicos por card
- Animação de entrada staggered

**Features listados**:
1. Separação Vocal (Demucs)
2. Transcrição (Whisper)
3. Detecção de Pitch (Crepe)
4. Suporte YouTube
5. Processamento Local
6. Processamento Rápido
7. Múltiplos Formatos
8. Jobs Configuráveis

---

### 4. HowItWorks
**Arquivo**: `src/components/HowItWorks.jsx`

**Funcionalidades**:
- 4 passos do processo
- Layout alternado (zigue-zague)
- Linha conectora vertical
- Ícones circulares com gradiente
- Numeração em badge
- Animações de entrada laterais

**Passos**:
1. 📤 Envie sua Música
2. ⚙️ Configure os Jobs
3. ✅ Processamento IA
4. 💾 Baixe o Resultado

---

### 5. Stats
**Arquivo**: `src/components/Stats.jsx`

**Funcionalidades**:
- 4 cards de estatísticas principais
- Ícones grandes com gradiente
- Números impactantes
- Hover effect com glow
- Background com efeitos de blur

**Estatísticas**:
- 4,000,000+ minutos processados
- 500,000+ usuários
- 2x velocidade
- 95% precisão IA

---

### 6. Testimonials
**Arquivo**: `src/components/Testimonials.jsx`

**Funcionalidades**:
- Grid 2 colunas (1 em mobile)
- 4 depoimentos reais
- Ícone de quote decorativo
- 5 estrelas rating
- Avatar emoji
- Nome e cargo do usuário

---

### 7. CTA
**Arquivo**: `src/components/CTA.jsx`

**Funcionalidades**:
- Card centralizado com glass effect
- Ícone de foguete animado
- Título chamativo
- 2 botões: "Começar Grátis" + "GitHub"
- Background com efeitos de blur
- Nota sobre gratuidade

---

### 8. Footer
**Arquivo**: `src/components/Footer.jsx`

**Funcionalidades**:
- Logo e descrição
- 3 colunas de links (Produto, Recursos, Legal)
- Links de redes sociais (GitHub, Twitter, Discord)
- Copyright e atribuição
- Glass effect consistente

---

### 9. ProcessPage
**Arquivo**: `src/pages/ProcessPage.jsx`

**Funcionalidades**:
- Recebe file ou url via router state
- Grid de 7 jobs configuráveis
- Checkbox visual com ícone
- Badge "Recomendado" em jobs essenciais
- Botão de processar desabilitado sem arquivo
- Card informativo com dicas

**Jobs configuráveis**:
1. ✅ Separação Vocal (recomendado)
2. ✅ Transcrição (recomendado)
3. ✅ Detecção de Pitch (recomendado)
4. ⬜ Arquivo MIDI
5. ⬜ Gráficos
6. ✅ Hifenização (recomendado)
7. ✅ Arquivo Karaokê (recomendado)

**State**:
```javascript
const [selectedJobs, setSelectedJobs] = useState({
  vocal_separation: true,
  transcription: true,
  pitch_detection: true,
  midi: false,
  plot: false,
  hyphenation: true,
  karaoke: true
})
```

## 🎨 Sistema de Cores

### Primary (Green)
```javascript
primary: {
  50: '#f0fdf4',
  100: '#dcfce7',
  200: '#bbf7d0',
  300: '#86efac',
  400: '#4ade80',
  500: '#22c55e',  // Main
  600: '#16a34a',
  700: '#15803d',
  800: '#166534',
  900: '#14532d',
}
```

### Dark (Background)
```javascript
dark: {
  700: '#334155',
  800: '#1e293b',  // Secondary bg
  900: '#0f172a',  // Main bg
}
```

## ✨ Animações Customizadas

### Float
```css
@keyframes float {
  0%, 100% { transform: translateY(0px) }
  50% { transform: translateY(-20px) }
}
```

### Pulse Slow
```javascript
'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite'
```

### Glow
```css
@keyframes glow {
  0%, 100% { opacity: 1 }
  50% { opacity: 0.5 }
}
```

## 🔗 Integrações Futuras

### Backend API (Flask/FastAPI)

```python
# backend/app.py (exemplo)
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/process', methods=['POST'])
def process_audio():
    data = request.json
    file = data.get('file')
    url = data.get('url')
    jobs = data.get('jobs')

    # Processar com UltraSinger
    result = process_ultrasinger(file, url, jobs)

    return jsonify(result)

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    status = check_task_status(task_id)
    return jsonify(status)
```

### Frontend Integration

```javascript
// src/api/ultrasinger.js
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

export const processAudio = async (file, url, jobs) => {
  const formData = new FormData()
  if (file) formData.append('file', file)
  if (url) formData.append('url', url)
  formData.append('jobs', JSON.stringify(jobs))

  const response = await axios.post(`${API_URL}/process`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })

  return response.data
}

export const getStatus = async (taskId) => {
  const response = await axios.get(`${API_URL}/status/${taskId}`)
  return response.data
}
```

## 📱 Responsividade

### Breakpoints (Tailwind)
- **sm**: 640px (mobile landscape)
- **md**: 768px (tablet)
- **lg**: 1024px (desktop)
- **xl**: 1280px (large desktop)
- **2xl**: 1536px (ultra wide)

### Mobile First
Todos os componentes são mobile-first com breakpoints crescentes:

```jsx
// Exemplo
className="
  grid
  grid-cols-1        // Mobile: 1 coluna
  md:grid-cols-2     // Tablet: 2 colunas
  lg:grid-cols-4     // Desktop: 4 colunas
  gap-4
"
```

## 🎯 Próximos Passos

### Backend (TODO)
- [ ] Criar API Flask/FastAPI
- [ ] Endpoint `/api/process` para iniciar processamento
- [ ] Endpoint `/api/status/<id>` para checar progresso
- [ ] Endpoint `/api/download/<id>` para baixar resultado
- [ ] WebSocket para progress em tempo real
- [ ] Sistema de fila (Celery/RQ)

### Frontend (TODO)
- [ ] Página de progresso com % e logs
- [ ] Download automático do resultado
- [ ] Histórico de processamentos
- [ ] Sistema de notificações
- [ ] Dark/Light mode toggle
- [ ] Internacionalização (PT/EN/ES)

## 🤝 Contribuindo

Para adicionar novos componentes:

1. Crie o arquivo em `src/components/NomeComponente.jsx`
2. Use Framer Motion para animações
3. Siga o padrão de cores e espaçamento
4. Adicione ao `HomePage.jsx` ou crie nova rota
5. Documente no README

## 📄 Licença

Parte do projeto UltraSinger - mesma licença do projeto principal.

---

**Criado com** ❤️ **por** [Flavio Kosta](https://github.com/flaviokosta79)
