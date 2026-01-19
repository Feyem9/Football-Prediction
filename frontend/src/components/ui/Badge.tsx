/**
 * Badge Component - Indicateur coloré
 */
import { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export default function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  const variants = {
    default: 'bg-slate-700 text-slate-300',
    success: 'bg-green-900/50 text-green-400 border border-green-600',
    warning: 'bg-yellow-900/50 text-yellow-400 border border-yellow-600',
    danger: 'bg-red-900/50 text-red-400 border border-red-600',
    info: 'bg-blue-900/50 text-blue-400 border border-blue-600',
  };
  
  return (
    <span className={`text-xs px-2 py-1 rounded-full ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
}
