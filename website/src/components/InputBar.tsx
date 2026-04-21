import { useState, useRef } from 'react';
import './inputbar.css';
import { useNavigate } from 'react-router-dom';

type InputBarProps = {
    conversation_id: string;
    conversationMetadata: any;
    geminiAPIKey: string;
}

function InputBar({ conversation_id, conversationMetadata, geminiAPIKey }: InputBarProps) {
    const [classes, setClasses] = useState("empty");
    const ref = useRef<HTMLDivElement>(null);
    const navigator = useNavigate();

    function on_inputbar_value_change(e: any) {
        const content: string = e.currentTarget.textContent ?? "";
        const trimmed_content = content.trim();
        if (trimmed_content === "") {
            if (ref.current) {
                ref.current.innerHTML = "";
            }
            setClasses("empty");
        } else {
            setClasses("");
        }
    }

    async function on_key_down(e: any) {
        if (e.key == "Enter" && !e.shiftKey) {
            e.preventDefault();

            await on_submit();
        }
    }

    async function on_submit() {
        const content = ref.current?.textContent ?? "";

        if (!content) return;

        if (conversation_id == "") conversation_id = "new";

        const url = `${import.meta.env.VITE_API_URL}/chat/${conversation_id}`;

        try {
            const res = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: content, byok: geminiAPIKey }),
                redirect: "follow"
            });

            if (!res.ok) throw new Error("Request failed");
            
            const result = await res.json();
            if (!result.success) throw new Error(result.error);

            // ✅ Clear input after sending
            if (ref.current) {
                ref.current.innerHTML = "";
            }
            setClasses("empty");


            // if result contains a different conversation_id than our current one (in cases of nwe conversations) navgiate to that one.
            if (conversation_id != result.conversation_id) navigator(`/chat/${result.conversation_id}`);

        } catch (err) {
            console.error(err);
        }
    }

    return (
        <div id="inputbar-container">
            <div id="inputbar">
                <div
                    ref={ref}
                    id="inputbar-field"
                    className={classes}
                    data-placeholder="Type something..."
                    contentEditable
                    suppressContentEditableWarning
                    onInput={on_inputbar_value_change}
                    onKeyDown={on_key_down}
                />
                <button id="inputbar-send" onClick={on_submit} disabled={ conversationMetadata?.state == "busy" }>
                    Send
                </button>
            </div>
        </div>
    );
}

export default InputBar;