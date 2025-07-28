import React from 'react';

interface AudioChatMessageProps {
  audioUrl: string;
  transcript: string;
}

const AudioChatMessage: React.FC<AudioChatMessageProps> = ({ audioUrl, transcript }) => {
  return (
    <div className="flex flex-col gap-2 rounded-lg bg-gray-100 p-4 dark:bg-gray-800">
      <audio controls src={audioUrl} className="w-full" />
      <p className="text-sm text-gray-500 dark:text-gray-400">{transcript}</p>
    </div>
  );
};

export default AudioChatMessage;
