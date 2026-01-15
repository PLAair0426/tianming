import React, { useState, useEffect, useRef } from 'react';

interface TypewriterProps {
  text: string;
  speed: number;
  onComplete?: () => void;
  className?: string;
}

const Typewriter: React.FC<TypewriterProps> = ({ text, speed, onComplete, className }) => {
  const [displayedText, setDisplayedText] = useState('');
  const indexRef = useRef(0);

  useEffect(() => {
    setDisplayedText('');
    indexRef.current = 0;
    if (!text) return;

    const timer = setInterval(() => {
      if (indexRef.current < text.length) {
        const char = text.charAt(indexRef.current);
        setDisplayedText((prev) => prev + char);
        indexRef.current++;
      } else {
        clearInterval(timer);
        if (onComplete) onComplete();
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed, onComplete]);

  return (
    <div className={`whitespace-pre-wrap ${className}`}>
      {displayedText}
      <span 
        className="animate-pulse inline-block w-2 h-4 bg-green-500 ml-1 align-middle"
        style={{ boxShadow: '0 0 5px #22c55e' }}
      ></span>
    </div>
  );
};

export default Typewriter;