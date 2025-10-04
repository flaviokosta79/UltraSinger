# ⚡ Comandos Rápidos - Frontend UltraSinger

## 🚀 Início Rápido

### Primeira Vez (Instalação)
```bash
# Navegue até o frontend
cd E:\VSCode\Projects\UltraSinger\frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento
npm run dev
```

**Acesse**: http://localhost:3000

---

## 📋 Comandos NPM Disponíveis

```bash
# Desenvolvimento (com hot reload)
npm run dev

# Build para produção
npm run build

# Preview da build de produção
npm run preview

# Lint (verificar problemas no código)
npm run lint
```

---

## 🔧 Comandos de Desenvolvimento

### Limpar Cache e Reinstalar
```bash
# Remover node_modules e package-lock.json
rm -rf node_modules package-lock.json

# Reinstalar tudo
npm install
```

### Atualizar Dependências
```bash
# Ver pacotes desatualizados
npm outdated

# Atualizar todos os pacotes (cuidado!)
npm update

# Atualizar um pacote específico
npm install react@latest
```

### Verificar Vulnerabilidades
```bash
# Auditar segurança
npm audit

# Corrigir vulnerabilidades automaticamente
npm audit fix
```

---

## 🐛 Troubleshooting Rápido

### Problema: Porta 3000 em uso
```bash
# Encontrar processo usando a porta 3000 (Windows)
netstat -ano | findstr :3000

# Matar processo (substitua PID pelo número encontrado)
taskkill /PID <PID> /F

# Ou altere a porta no vite.config.js:
# server: { port: 3001 }
```

### Problema: Módulos não encontrados
```bash
# Limpar e reinstalar
rm -rf node_modules package-lock.json
npm install
```

### Problema: Cache do Vite com problemas
```bash
# Limpar cache do Vite
rm -rf node_modules/.vite
npm run dev
```

### Problema: ESLint mostrando muitos erros
```bash
# Executar fix automático
npm run lint -- --fix
```

---

## 📦 Build e Deploy

### Build de Produção
```bash
# Criar build otimizado
npm run build

# Arquivos criados em: frontend/dist/
```

### Testar Build Localmente
```bash
# Preview da build
npm run preview
```

### Analisar Tamanho do Bundle
```bash
# Instalar analisador
npm install --save-dev rollup-plugin-visualizer

# Adicionar ao vite.config.js e rodar build
npm run build
```

---

## 🔗 Integração com Backend

### Testar API (quando backend estiver pronto)
```bash
# Em um terminal, rode o backend:
cd E:\VSCode\Projects\UltraSinger\backend
python app.py  # ou: uvicorn main:app --reload

# Em outro terminal, rode o frontend:
cd E:\VSCode\Projects\UltraSinger\frontend
npm run dev
```

### Verificar Proxy
O frontend está configurado para fazer proxy das requisições `/api/*` para `http://localhost:5000`

**Teste no console do navegador:**
```javascript
// Deve fazer requisição para http://localhost:5000/api/test
fetch('/api/test')
  .then(r => r.json())
  .then(console.log)
```

---

## 🎨 Customização Rápida

### Mudar Cor Primária
Edite `frontend/tailwind.config.js`:
```javascript
colors: {
  primary: {
    // Altere estes valores:
    500: '#22c55e',  // Verde atual
    600: '#16a34a',
  }
}
```

### Mudar Porta do Frontend
Edite `frontend/vite.config.js`:
```javascript
server: {
  port: 3001,  // Nova porta
}
```

### Mudar URL do Backend
Edite `frontend/vite.config.js`:
```javascript
server: {
  proxy: {
    '/api': 'http://localhost:8000'  // Nova URL
  }
}
```

---

## 📱 Testar Responsividade

### No Navegador (Chrome DevTools)
1. Abra DevTools (F12)
2. Clique no ícone de dispositivo móvel (Ctrl+Shift+M)
3. Teste diferentes tamanhos:
   - Mobile: 375x667 (iPhone SE)
   - Tablet: 768x1024 (iPad)
   - Desktop: 1920x1080

### Dispositivos Recomendados para Teste
- 📱 Mobile: 320px - 640px
- 📱 Tablet: 640px - 1024px
- 💻 Desktop: 1024px+

---

## 🔍 Debug no Navegador

### Verificar Console
```javascript
// No console do navegador (F12):

// Ver estado do React Router
console.log(window.location)

// Ver localStorage
console.log(localStorage)

// Testar Axios
import axios from 'axios'
axios.get('/api/test').then(console.log)
```

### React DevTools
1. Instale extensão: [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
2. Abra DevTools (F12)
3. Vá para aba "⚛️ Components" ou "⚛️ Profiler"

---

## 🧪 Adicionar Novas Páginas

### Exemplo: Criar ProgressPage

1. **Criar arquivo**: `src/pages/ProgressPage.jsx`
```jsx
import { useParams } from 'react-router-dom';

export default function ProgressPage() {
  const { jobId } = useParams();

  return (
    <div className="min-h-screen pt-20 px-4">
      <h1>Processamento: {jobId}</h1>
      {/* Adicione conteúdo aqui */}
    </div>
  );
}
```

2. **Adicionar rota**: `src/App.jsx`
```jsx
import ProgressPage from './pages/ProgressPage';

// Dentro das Routes:
<Route path="/progress/:jobId" element={<ProgressPage />} />
```

3. **Navegar para a página**: Em qualquer componente
```jsx
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();
navigate(`/progress/${jobId}`);
```

---

## 🧩 Adicionar Novos Componentes

### Exemplo: Criar NotificationBanner

1. **Criar arquivo**: `src/components/NotificationBanner.jsx`
```jsx
import { motion } from 'framer-motion';
import { FaTimes } from 'react-icons/fa';

export default function NotificationBanner({ message, type, onClose }) {
  const colors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500',
  };

  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: -100, opacity: 0 }}
      className={`fixed top-20 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50`}
    >
      <div className="flex items-center gap-3">
        <p>{message}</p>
        <button onClick={onClose}>
          <FaTimes />
        </button>
      </div>
    </motion.div>
  );
}
```

2. **Usar no componente**:
```jsx
import NotificationBanner from '../components/NotificationBanner';
import { useState } from 'react';

function MyComponent() {
  const [showNotification, setShowNotification] = useState(true);

  return (
    <>
      {showNotification && (
        <NotificationBanner
          message="Arquivo enviado com sucesso!"
          type="success"
          onClose={() => setShowNotification(false)}
        />
      )}
    </>
  );
}
```

---

## 📦 Adicionar Novas Dependências

### Instalar Pacote
```bash
# Adicionar dependência de produção
npm install nome-do-pacote

# Adicionar dependência de desenvolvimento
npm install --save-dev nome-do-pacote
```

### Exemplos Úteis
```bash
# Gerenciamento de estado global
npm install zustand

# Requisições HTTP mais avançadas
npm install @tanstack/react-query

# Formulários
npm install react-hook-form

# Validação
npm install zod

# Formatação de datas
npm install date-fns

# Toast notifications
npm install react-hot-toast

# Progressbar
npm install nprogress

# UUID
npm install uuid
```

---

## 🔐 Variáveis de Ambiente

### Criar arquivo `.env`
```bash
# Criar arquivo na raiz do frontend
cd frontend
New-Item .env
```

### Exemplo `.env`
```env
VITE_API_URL=http://localhost:5000
VITE_APP_NAME=UltraSinger
VITE_MAX_FILE_SIZE=1073741824
```

### Usar no código
```javascript
const apiUrl = import.meta.env.VITE_API_URL;
const appName = import.meta.env.VITE_APP_NAME;
```

**⚠️ Importante**: Variáveis devem começar com `VITE_`

---

## 🎯 Checklist de Verificação Diária

```
□ npm run dev funciona sem erros
□ Console do navegador sem erros
□ Todas as páginas carregam corretamente
□ Navegação funciona
□ Upload de arquivo funciona (UI)
□ Responsive funciona (teste mobile)
□ Animações estão suaves
□ Links do footer funcionam
□ Menu mobile abre/fecha
```

---

## 📊 Monitoramento de Performance

### Lighthouse (Chrome)
1. Abra DevTools (F12)
2. Vá para aba "Lighthouse"
3. Clique em "Generate report"
4. Analise:
   - Performance
   - Accessibility
   - Best Practices
   - SEO

### Bundle Size
```bash
# Analisar tamanho dos arquivos
npm run build
# Verifique frontend/dist/

# Ver tamanho total
du -sh frontend/dist/
```

---

## 🆘 Comandos de Emergência

### Frontend não inicia
```bash
# 1. Verificar versão do Node
node --version  # Deve ser 16.x ou superior

# 2. Limpar tudo
rm -rf node_modules package-lock.json .vite
npm cache clean --force

# 3. Reinstalar
npm install

# 4. Tentar novamente
npm run dev
```

### Erro de memória (build)
```bash
# Aumentar limite de memória do Node
$env:NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

### Porta não libera (Windows)
```bash
# Ver processos na porta 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess

# Matar processo (PowerShell como Admin)
Stop-Process -Id <PID> -Force
```

---

## 📚 Links Úteis

- **Documentação React**: https://react.dev
- **Vite Docs**: https://vitejs.dev
- **Tailwind Docs**: https://tailwindcss.com/docs
- **Framer Motion**: https://www.framer.com/motion/
- **React Router**: https://reactrouter.com
- **React Icons**: https://react-icons.github.io/react-icons/

---

## 🎓 Comandos Git (Frontend)

```bash
# Status do frontend
git status frontend/

# Adicionar apenas frontend
git add frontend/

# Commit do frontend
git commit -m "feat(frontend): adiciona nova feature"

# Ver histórico do frontend
git log --oneline -- frontend/

# Desfazer mudanças no frontend
git checkout -- frontend/
```

---

## 💡 Dica Final

**Salve este arquivo nos favoritos!** 📌

Sempre que precisar de um comando rápido, consulte aqui primeiro.

---

**Última atualização**: Criado junto com o frontend
**Versão**: 1.0.0
