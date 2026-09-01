import React, { useState } from 'react';
import { Bot, Send, Sparkles, User, HelpCircle } from 'lucide-react';
import { chatWithAI } from '../../api/client';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  relatedChecks?: string[];
  timestamp: string;
}

interface AIChatPanelProps {
  bidId: string;
  bidderName: string;
}

export const AIChatPanel: React.FC<AIChatPanelProps> = ({ bidId, bidderName }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'init-1',
      sender: 'ai',
      text: `Hello, Officer. I can provide grounded explanations of ${bidderName}'s verification findings, statutory mismatches, and compliance risks based strictly on backend facts.`,
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input.trim();
    if (!query) return;

    const userMsg: Message = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setIsTyping(true);

    try {
      const response = await chatWithAI(bidId, query);
      const aiMsg: Message = {
        id: `msg-${Date.now() + 1}`,
        sender: 'ai',
        text: response.answer,
        relatedChecks: response.related_checks,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: `msg-${Date.now() + 1}`,
        sender: 'ai',
        text: 'Error communicating with AI assistant. Please verify backend connectivity.',
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const quickPrompts = [
    'Why is GST flagged?',
    'Why is this bidder low risk?',
    'Explain ESIC compliance',
    'Explain OEM status',
  ];

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col gap-3">
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-purple-600" />
          <h2 className="text-sm font-bold text-slate-800">GeM AI Compliance Assistant</h2>
        </div>
        <span className="text-[11px] font-bold text-purple-700 bg-purple-50 border border-purple-200 px-2 py-0.5 rounded-full flex items-center gap-1">
          <Sparkles className="w-3 h-3" />
          <span>Grounded Explanations</span>
        </span>
      </div>

      {/* Chat Messages */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 h-44 overflow-y-auto flex flex-col gap-2.5 text-xs">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col gap-1 max-w-[88%] ${
              m.sender === 'user' ? 'self-end items-end' : 'self-start items-start'
            }`}
          >
            <div
              className={`p-2.5 rounded-xl text-xs leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none shadow-sm'
                  : 'bg-white text-slate-800 border border-slate-200 rounded-bl-none shadow-sm'
              }`}
            >
              <div className="flex items-center gap-1.5 mb-1 font-semibold opacity-80 text-[10px]">
                {m.sender === 'user' ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3 text-purple-600" />}
                <span>{m.sender === 'user' ? 'Officer' : 'AI Assistant'}</span>
                <span>• {m.timestamp}</span>
              </div>
              <p>{m.text}</p>

              {m.relatedChecks && m.relatedChecks.length > 0 && (
                <div className="mt-1.5 pt-1.5 border-t border-slate-100 flex items-center gap-1 text-[10px] text-purple-600 font-mono">
                  <span>Related Rules:</span>
                  {m.relatedChecks.map((rc) => (
                    <span key={rc} className="bg-purple-50 px-1.5 py-0.5 rounded font-bold">
                      {rc}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="self-start bg-white text-slate-400 p-2 rounded-lg border border-slate-200 text-xs italic flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
            <span>Analyzing verification facts...</span>
          </div>
        )}
      </div>

      {/* Quick Prompts */}
      <div className="flex flex-wrap gap-1.5">
        {quickPrompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => handleSend(prompt)}
            className="text-[11px] font-medium bg-slate-100 hover:bg-slate-200/80 text-slate-700 px-2.5 py-1 rounded-full border border-slate-200 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input row */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask AI about this bidder's compliance findings..."
          className="flex-1 text-xs p-2.5 rounded-lg border border-slate-300 bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || isTyping}
          className="bg-blue-600 hover:bg-blue-700 text-white px-3.5 py-2 rounded-lg text-xs font-bold transition-all disabled:bg-slate-300 flex items-center gap-1"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Ask</span>
        </button>
      </div>
    </div>
  );
};
