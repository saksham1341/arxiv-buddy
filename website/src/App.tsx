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
    let isMounted: boolean = true;
    let timeoutId: number;

    async function checkServers() {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 3000);

        const [resp1, resp2] = await Promise.all([
          fetch(import.meta.env.VITE_API_URL, { signal: controller.signal }),
          fetch(import.meta.env.VITE_API_URL_2, { signal: controller.signal }),
        ]);

        clearTimeout(timeout);

        const [data1, data2] = await Promise.all([
          resp1.json(),
          resp2.json(),
        ]);

        const bothUp =
          resp1.ok && data1.success &&
          resp2.ok && data2.success;

        if (isMounted) {
          setAreServersUp(bothUp);
        }
      } catch (err) {
        if (isMounted) {
          setAreServersUp(false);
        }
      }

      // schedule next check
      timeoutId = setTimeout(checkServers, 5000);
    }

    checkServers();

    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
    };
  }, []);

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
