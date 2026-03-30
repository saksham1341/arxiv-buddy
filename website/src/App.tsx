import Header from './components/Header'
import Chat from './pages/Chat'
import NotFound from './pages/NotFound'
import NewChat from './pages/NewChat'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './pages/Sidebar'

function App() {
  return (
    <>
    <BrowserRouter>
      <Sidebar />
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
