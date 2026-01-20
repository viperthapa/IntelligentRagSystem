import React, { useRef, useEffect } from 'react';
import { Upload, Send, Loader2 } from 'lucide-react';

const ChatInterface = (props) => {
    const {messages, 
    input, 
    isSending, 
    uploadedFile,
    onInputChange, 
    onSendMessage } = props;
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        onSendMessage();
        }
    };

    return (
        <>
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
            {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
                <div className="text-center text-gray-400">
                <Upload className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg">Upload a document to get started</p>
                <p className="text-sm mt-2">
                    You can ask questions about the uploaded document
                </p>
                </div>
            </div>
            ) : (
            <div className="space-y-4 max-w-4xl mx-auto">
                {messages.map((msg, idx) => (
                <div
                    key={idx}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                    <div
                    className={`max-w-2xl rounded-lg px-4 py-3 ${
                        msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : msg.role === 'system'
                        ? msg.isError
                            ? 'bg-red-100 text-red-800 border border-red-200'
                            : 'bg-green-100 text-green-800 border border-green-200'
                        : 'bg-white border border-gray-200 text-gray-800'
                    }`}
                    >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>
                </div>
                ))}
                <div ref={messagesEndRef} />
            </div>
            )}
        </div>

        {/* Input Section */}
        <div className="bg-white border-t border-gray-200 px-6 py-4">
            <div className="max-w-4xl mx-auto">
            <div className="flex gap-3">
                <input
                type="text"
                value={input}
                onChange={(e) => onInputChange(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                    uploadedFile
                    ? 'Ask a question about your document...'
                    : 'Upload a document first...'
                }
                disabled={!uploadedFile || isSending}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
                <button
                onClick={onSendMessage}
                disabled={!input.trim() || !uploadedFile || isSending}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                {isSending ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                    <Send className="w-5 h-5" />
                )}
                </button>
            </div>
            </div>
        </div>
        </>
    );
}

export default ChatInterface;