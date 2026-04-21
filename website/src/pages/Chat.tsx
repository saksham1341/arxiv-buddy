import { useNavigate, useParams } from "react-router-dom";
import { useEffect, useState, } from "react";
import { UserMessage, AIMessage, GatherContextCallMessage, SearcherCallMessage, LearnerCallMessage } from "../components/Message";
import InputBar from "../components/InputBar";
import { useRef } from "react";

import "./chat.css"

type ParamsType = {
    conversation_id: string;
}

type ConversationMessage = {
    conversation_id: string;
    timestamp: string;
    item_type: string;
    data: string;
}

type ConversationMetadata = {
    title: string;
    state: string;
}

type ConversationError = {
    error: string;
}

type ChatProps = {
    geminiAPIKey: string;
}


function Chat({ geminiAPIKey }: ChatProps) {
    const navigate = useNavigate();
    const { conversation_id } = useParams<ParamsType>();
    const [ conversationMetadata, setConversationMetadata ] = useState<ConversationMetadata>({ title: "New Conversation", state: "busy" })
    const [ conversationMessages, setConversationMessages ] = useState<ConversationMessage[]>([])
    const ref = useRef<HTMLDivElement>(null)

    function handleConversationMetadata(data: ConversationMetadata) {
        // handle conversation_metadata message from SSE
        
        setConversationMetadata(prev => ({
            title: data.title ?? prev.title,
            state: data.state ?? prev.state
        }));
    }

    function handleConversationMessage(data: ConversationMessage) {
        // handle conversation_message message from SSE

        setConversationMessages(prev => [...prev, data]);
    }

    function handleConversationHistory(data: ConversationMessage[]) {
        // handle conversation_history message from SSE

        setConversationMessages(data);
    }

    function handleConversationError(data: ConversationError[]) {
        // handle error message from SSE

        console.log(data);

        alert("Some error occured! Make sure your Gemini API key is correct.");
    }

    useEffect(() => {
        // initiate connection to chat
        const server_url = import.meta.env.VITE_API_URL;
        const chat_url = `${server_url}/chat/${conversation_id}`;

        const eventSource = new EventSource(chat_url);

        eventSource.onmessage = (event) => {
            const message = JSON.parse(event.data);

            console.log(message);

            if (message.type == "conversation_not_found") navigate("/");
            else if (message.type == "conversation_metadata") handleConversationMetadata(message.data);
            else if (message.type == "conversation_history") handleConversationHistory(message.data);
            else if (message.type == "conversation_message") handleConversationMessage(message.data);
            else if (message.type == "error") handleConversationError(message.data);
            else {
                console.log(`Received unkown message from server. ${message}`);
            }
        }

        eventSource.onerror = (event) => {
            console.log(event);
        }

        return () => {
            eventSource.close();
        }
    }, [conversation_id])

    useEffect(() => {
        document.title = conversationMetadata.title;
    }, [conversationMetadata.title])

    useEffect(() => {
        if (conversationMessages.length == 0) return;

        const latest_item = conversationMessages[conversationMessages.length - 1]
        if (["user_message", "ai_message"].includes(latest_item.item_type)) {
            if (ref.current) ref.current.scrollTo({
                top: ref.current.scrollHeight,
                behavior: "smooth"
            });
        }
    }, [conversationMessages])

    function parseConversationMessageToComponent(message: ConversationMessage, idx: number, arr: ConversationMessage[]) {
        const message_data = JSON.parse(message.data);

        if (message.item_type == "user_message") return <UserMessage key={message.timestamp} timestamp={message.timestamp} content={message_data.message} />
        if (message.item_type == "ai_message") return <AIMessage key={message.timestamp} timestamp={message.timestamp} content={message_data.message} />
        if (message.item_type == "gather_context_call") return <GatherContextCallMessage key={message.timestamp} queries={message_data.q} active={idx == arr.length - 1} />
        if (message.item_type == "searcher_call") return <SearcherCallMessage key={message.timestamp} queries={message_data.q} active={idx == arr.length - 1} />
        if (message.item_type == "learner_call") return <LearnerCallMessage key={message.timestamp} article_ids={message_data.article_ids} active={idx == arr.length - 1} />

        return null;
    }

    return (
        <>
        <div ref={ ref } id="chat">
            {conversationMessages.map(parseConversationMessageToComponent).filter((item) => item != null)}
        </div>
        <InputBar conversation_id={ conversation_id ? conversation_id : "" } conversationMetadata ={ conversationMetadata } geminiAPIKey={ geminiAPIKey }/>
        </>
    )
}

export default Chat;
