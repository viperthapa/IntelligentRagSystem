import { useState } from 'react';
import Header from './components/Header';
import DocumentUpload from './components/DocumentUpload';
import ChatInterface from './components/ChatInterface';

export default function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowedTypes = [
      'application/pdf',
      'text/plain',
      'text/markdown',
      'text/x-markdown'
    ];
    
    if (!allowedTypes.includes(file.type) && !file.name.endsWith('.md')) {
      setUploadError('Please upload a PDF, TXT, or Markdown file');
      return;
    }

    setUploadError('');
    setIsUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/upload/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setUploadedFile({
        id: data.id,
        name: data.file_name,
        fileType: file.file_type
      });
      
      setMessages([{
        role: 'system',
        content: `Document "${file.name}" uploaded successfully. You can now ask questions about it.`,
        timestamp: new Date().toISOString()
      }]);
    } catch (error) {
      setUploadError('Failed to upload file. Please try again.');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isSending) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsSending(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: input,
          document_id: uploadedFile?.id || null,
        }),
      });

      if (!response.ok) {
        throw new Error('Chat request failed');
      }

      const data = await response.json();
      
      const assistantMessage = {
        role: 'assistant',
        content: data.response || data.message || 'No response received',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'system',
        content: 'Failed to send message. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Chat error:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />
      
      <DocumentUpload
        uploadedFile={uploadedFile}
        isUploading={isUploading}
        uploadError={uploadError}
        onFileSelect={handleFileSelect}
        onRemoveFile={handleRemoveFile}
      />
      
      <ChatInterface
        messages={messages}
        input={input}
        isSending={isSending}
        uploadedFile={uploadedFile}
        onInputChange={setInput}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
}