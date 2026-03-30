import InputBar from '../components/InputBar';

import './newchat.css';

function NewChat() {
    return (
        <>
            <div id="newchatbanner">
                <h1>Start a new chat.</h1>
                <p>ArXiv Buddy is your neighborhood friendly agent which uses the vast amount of research information hosted at <a href="https://arxiv.org/">ArXiv</a> to answer your queries.</p>
                <p>Start by asking any question, for example, how are rainbows made?</p>
            </div>
            <InputBar conversation_id={ 'new' } conversationMetadata={ { state: "free", title: "New Conversation" } } />
        </>
    )
}

export default NewChat;