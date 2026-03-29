import ReactMarkdown from 'react-markdown'

import './message.css'

type UserMessageProps = {
    content: string;
    timestamp: string;
}

function UserMessage({ content, timestamp }: UserMessageProps) {
    const d = new Date(timestamp);
    const formatter = new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    });

    return (
        <>
        <span className="timestamp user">{ formatter.format(d) }</span>
        <div className="message user">
            <ReactMarkdown>{ content }</ReactMarkdown>
        </div>
        </>
    )
}

type AIMessageProps = {
    content: string;
    timestamp: string;
}

function AIMessage({ content, timestamp }: AIMessageProps) {
    const d = new Date(timestamp);
    const formatter = new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    });

    return (
        <>
        <span className="timestamp ai">{ formatter.format(d) }</span>
        <div className="message ai">
            <ReactMarkdown>{ content }</ReactMarkdown>
        </div>
        </>
    )
}

type GatherContextCallMessageProps = {
    queries: string[];
    active: boolean;
}

function GatherContextCallMessage({ queries, active }: GatherContextCallMessageProps) {
    return (
        <div className={ "message activity gathering-context" + (active ? " active" : "")}>
            { (active ? "Gathering context from knowledge base." : "Gathered context from knowledge base.") + ` (${queries.length} Queries)` }
        </div>
    )
}

type SearcherCallMessageProps = {
    queries: string[];
    active: boolean;
}

function SearcherCallMessage({ queries, active }: SearcherCallMessageProps) {
    return (
        <div className={ "message activity searching" + (active ? " active" : "")}>
            { (active ? "Searching for articles." : "Searched for articles.") + ` (${queries.length} Queries)` }
        </div>
    )
}

type LearnerCallMessageProps = {
    article_ids: string[];
    active: boolean;
}

function LearnerCallMessage({ article_ids, active }: LearnerCallMessageProps) {
    return (
        <div className={ "message activity learning" + (active ? " active" : "")}>
            { active ? `Learning ${article_ids.length} articles.` : `Learned ${article_ids.length} articles.` }
        </div>
    )
}

export { UserMessage, AIMessage, GatherContextCallMessage, SearcherCallMessage, LearnerCallMessage }
