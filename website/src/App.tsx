import Header from './components/Header'
import Chat from './pages/Chat'
import NotFound from './pages/NotFound'
import NewChat from './pages/NewChat'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import { useEffect, useState } from 'react'
import Connecting from './pages/Connecting'

function App() {
  const [ geminiAPIKey, setGeminiAPIKey ] = useState<string>("");
  const [ areServersUp, setAreServersUp ] = useState<boolean>(false);

  useEffect(() => {
    async function _() {
      const resp = await fetch(import.meta.env.VITE_API_URL, { method: "GET" });

      if (!resp.ok || !(await resp.json()).success) {
        setAreServersUp(false);
        setTimeout(_, 5000);
        return;
      }

      const resp2 = await fetch(import.meta.env.VITE_API_URL_2, { method: "GET" });

      if (!resp2.ok || !(await resp2.json()).success) {
        setAreServersUp(false);
        setTimeout(_, 5000);
        return;
      }

      setAreServersUp(true);

      return;
    }

    _();
  }, [])

  return areServersUp ? (
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
  ) : (<Connecting />);
}

export default App
