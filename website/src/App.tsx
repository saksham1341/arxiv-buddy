import Header from './components/Header'
import Chat from './pages/Chat'
import NotFound from './pages/NotFound'
import NewChat from './pages/NewChat'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import { useState } from 'react'

function App() {
  const [ geminiAPIKey, setGeminiAPIKey ] = useState<string>("");

  return (
    <>
    <BrowserRouter>
      <Routes>
        <Route path="/chat/:current_conversation_id" element={<Sidebar setGeminiAPIKey={setGeminiAPIKey}/>} />
        <Route path="*" element={<Sidebar setGeminiAPIKey={setGeminiAPIKey}/>} />
      </Routes>
      <div id="inner-root">
        <Header />
          <Routes>
            <Route path="/" element={<NewChat geminiAPIKey={ geminiAPIKey }/>} />
            <Route path="/chat/:conversation_id" element={<Chat geminiAPIKey={ geminiAPIKey }/>} />
            <Route path="*" element={<NotFound />} />
          </Routes>
      </div>
    </BrowserRouter>
    </>
  )
}

export default App
