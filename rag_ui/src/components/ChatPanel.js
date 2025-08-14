import React, { useState, useRef, useEffect } from 'react';
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  ConversationHeader
} from '@chatscope/chat-ui-kit-react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import { askQuestion } from '../services/api';

const ChatPanel = ({ selectedDocument, userId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await askQuestion(
        userMessage,
        userId,
        selectedDocument?.file_id
      );

      setMessages(prev => [
        ...prev,
        {
          type: 'ai',
          content: response.answer,
          sources: response.sources
        }
      ]);
    } catch (error) {
      console.error('Error getting response:', error);
      setMessages(prev => [
        ...prev,
        {
          type: 'error',
          content: 'Sorry, there was an error processing your question. Please try again.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ height: '100%' }}>
      <MainContainer>
        <ChatContainer>
          <ConversationHeader>
            <ConversationHeader.Content>
              {selectedDocument ? (
                <>
                  <ConversationHeader.Back />
                  <span>Chat about: {selectedDocument.filename}</span>
                </>
              ) : (
                <span>Select a document to start chatting</span>
              )}
            </ConversationHeader.Content>
          </ConversationHeader>
          <MessageList>
            {messages.map((message, index) => (
              <Message
                key={index}
                model={{
                  message: message.content,
                  sender: message.type === 'user' ? 'user' : 'ai',
                  direction: message.type === 'user' ? 'outgoing' : 'incoming',
                  position: 'single',
                }}
              />
            ))}
            <div ref={messagesEndRef} />
          </MessageList>
          <MessageInput
            placeholder="Ask a question about the document..."
            value={inputMessage}
            onChange={(value) => setInputMessage(value)}
            onSend={handleSubmit}
            disabled={isLoading || !selectedDocument}
          />
        </ChatContainer>
      </MainContainer>
    </div>
  );
};

export default ChatPanel; 