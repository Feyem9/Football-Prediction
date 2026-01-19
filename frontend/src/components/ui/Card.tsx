/**
 * Card Component - Container avec style glassmorphism
 */
import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

export default function Card({ children, className = '', hover = false }: CardProps) {
  return (
    <div 
      className={`
        bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 
        ${hover ? 'hover:border-blue-500 transition-all hover:scale-[1.02] cursor-pointer' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
