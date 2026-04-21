import { useEffect, useRef, useState, type Dispatch, type SetStateAction } from "react";
import { useNavigate, useParams } from "react-router-dom"

import "./sidebar.css"

type SidebarItemProps = {
    conversation_id: string;
    title: string;
    is_current: boolean;
}

type BYOKSetterProps = {
    setGeminiAPIKey: Dispatch<SetStateAction<string>>;
}

function BYOKSetter({ setGeminiAPIKey }: BYOKSetterProps) {
    const ref = useRef<HTMLInputElement>(null);
    const [ showError, setShowError ] = useState<boolean>(true);

    function handleChange(e: any) {
        const api_key = ref.current?.value.trim();

        setGeminiAPIKey(api_key?? "");
        
        if (api_key) {
            setShowError(false);
        } else {
            setShowError(true);
        }
    }

    return (
        <input ref={ ref } id="byok-setter" className={ showError ? "error" : "" } onChange={ handleChange } placeholder="Enter your Gemini API Key" />
    )
}

function NewChatSidebarItem() {
    const navigator = useNavigate();

    return (
        <span className="sidebar-item" onClick={() => navigator('/')}>+ Start New Chat</span>
    )
}

function SidebarItem({ conversation_id, title, is_current }: SidebarItemProps) {
    const navigator = useNavigate();
    
    return (
        <span className={ "sidebar-item" + (is_current ? " current" : "") } onClick={() => navigator(`/chat/${conversation_id}`)}>{ title }</span>
    )
}

type ParamsType = {
    current_conversation_id: string;
}

type SidebarProps = {
    setGeminiAPIKey: Dispatch<SetStateAction<string>>;
}

function Sidebar({ setGeminiAPIKey }: SidebarProps) {
    const [ sidebarData, setSidebarData ] = useState<Array<any>>([]);
    const { current_conversation_id } = useParams<ParamsType>();

    useEffect(() => {
        async function loadSidebarData() {
            const url = import.meta.env.VITE_API_URL;
            const resp = await fetch(`${url}/list_of_conversations`).then(resp => resp.json()).catch(() => null);

            if (resp !== null) {
                setSidebarData(resp.conversations);
            }
        }

        loadSidebarData();

        const _ = setInterval(loadSidebarData, 1000);

        return () => {
            clearInterval(_);
        }
    }, [])

    return (
        <div id="sidebar">
            <h2>All Chats</h2>
            <BYOKSetter setGeminiAPIKey={ setGeminiAPIKey }/>
            <NewChatSidebarItem />
            {
                sidebarData.map((i) => (<SidebarItem key={i.conversation_id} conversation_id={i.conversation_id} title={i.title} is_current={i.conversation_id === current_conversation_id} />))
            }
        </div>
    )
}

export default Sidebar
