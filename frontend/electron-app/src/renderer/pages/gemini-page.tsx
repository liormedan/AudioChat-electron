import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { ArrowLeft, Bot } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import GeminiChat from '../components/chat/gemini-chat';

export const GeminiPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="p-6 space-y-6">
      <div className="space-y-4">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/chat')}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Chat</span>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
              <Bot className="h-8 w-8 text-blue-600" />
              Gemini Chat
            </h1>
            <p className="text-muted-foreground">
              שוחח עם Gemini AI - העוזר החכם של Google
            </p>
          </div>
        </div>
      </div>

      <Card className="h-[800px]">
        <CardContent className="p-0 h-full">
          <GeminiChat />
        </CardContent>
      </Card>
    </div>
  );
};