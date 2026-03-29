import { useParams } from "react-router-dom";
import { useEffect, useState, } from "react";
import { UserMessage, AIMessage, GatherContextCallMessage, SearcherCallMessage, LearnerCallMessage } from "../components/Message";
import InputBar from "../components/InputBar";
import { useRef } from "react";

import "./chat.css"

type ParamsType = {
    conversation_id: string;
}

type ConversationItem = {
    conversation_id: string;
    timestamp: string;
    item_type: string;
    data: string;
}

function Chat() {
    const { conversation_id } = useParams<ParamsType>();
    const [ conversationHistory, setConversationHistory ] = useState<ConversationItem[]>([])
    const [ isConversationBusy, setIsConversationBusy ] = useState<boolean>(true)
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // initiate connection to chat
        const server_url = import.meta.env.VITE_API_URL;
        const eventSource = new EventSource(`${server_url}/chat/${conversation_id}`)

        eventSource.onmessage = (event) => {
            const message_data = JSON.parse(event.data);

            if (Array.isArray(message_data)) {
                // set conversation status
                const last_conversation_status_message = message_data.findLast(item => item.item_type === "conversation_state_change");
                if (last_conversation_status_message) setIsConversationBusy(JSON.parse(last_conversation_status_message.data).agent_busy);
                else setIsConversationBusy(false);

                // set conversation history
                setConversationHistory(message_data);
            } else {
                if (message_data.item_type === "conversation_state_change") setIsConversationBusy(JSON.parse(message_data.data).agent_busy);
                setConversationHistory((prev) => [...prev, message_data]);
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
        if (conversationHistory.length == 0) return;

        const latest_item = conversationHistory[conversationHistory.length - 1]
        if (["user_message", "ai_message", "conversation_state_change"].includes(latest_item.item_type)) {
            if (ref.current) ref.current.scrollTo({
                top: ref.current?.scrollHeight,
                behavior: "smooth"
            });
        }
    }, [conversationHistory])

    function parse_conversation_item_to_component(item: ConversationItem, idx: number, arr: ConversationItem[]) {
        const item_data = JSON.parse(item.data);

        if (item.item_type == "user_message") return <UserMessage key={item.timestamp} timestamp={item.timestamp} content={item_data.message} />
        if (item.item_type == "ai_message") return <AIMessage key={item.timestamp} timestamp={item.timestamp} content={item_data.message} />
        if (item.item_type == "gather_context_call") return <GatherContextCallMessage key={item.timestamp} queries={item_data.q} active={idx == arr.length - 1} />
        if (item.item_type == "searcher_call") return <SearcherCallMessage key={item.timestamp} queries={item_data.q} active={idx == arr.length - 1} />
        if (item.item_type == "learner_call") return <LearnerCallMessage key={item.timestamp} article_ids={item_data.article_ids} active={idx == arr.length - 1} />

        return null;
    }

    return (
        <>
        <div ref={ ref } id="chat">
            {conversationHistory.map(parse_conversation_item_to_component).filter((item) => item != null)}
        </div>
        <InputBar conversation_id={ conversation_id } is_conversation_busy={ isConversationBusy } />
        </>
    )
}

export default Chat;
