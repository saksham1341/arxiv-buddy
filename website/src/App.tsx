import Header from './components/Header'
import Chat from './pages/Chat'
import NotFound from './pages/NotFound'
import NewChat from './pages/NewChat'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'

function App() {
  return (
    <>
    <BrowserRouter>
      <Routes>
        <Route path="/chat/:current_conversation_id" element={<Sidebar />} />
        <Route path="*" element={<Sidebar />} />
      </Routes>
      <div id="inner-root">
        <Header />
          <Routes>
            <Route path="/" element={<NewChat />} />
            <Route path="/chat/:conversation_id" element={<Chat />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
      </div>
    </BrowserRouter>
    </>
  )
}

export default App
