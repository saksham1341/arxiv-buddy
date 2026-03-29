import Header from './components/Header'
import Chat from './pages/Chat'
import NotFound from './pages/NotFound'
import NewChat from './pages/NewChat'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <>
    <Header />
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<NewChat />} />
        <Route path="/chat/:conversation_id" element={<Chat />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default App
