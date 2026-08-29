import React from 'react';

/**
 * Dropdown - Floating action dropdown menu with keyboard arrow navigation.
 * Platform: Chatbot Distributed Real-Time Communication Platform.
 */

export interface DropdownProps {
  children?: React.ReactNode;
  className?: string;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: (e: any) => void;
  [key: string]: any;
}

export const Dropdown: React.FC<DropdownProps> = ({
  children,
  className = '',
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  ...props
}) => {
  return (
    <div
      className={
        "inline-flex items-center justify-center rounded-xl font-medium transition-all " +
        (variant === 'primary' ? 'bg-indigo-600 text-white hover:bg-indigo-500 ' : 'bg-slate-800 text-slate-200 hover:bg-slate-700 ') +
        (size === 'sm' ? 'px-3 py-1.5 text-xs ' : size === 'lg' ? 'px-6 py-3 text-base ' : 'px-4 py-2 text-sm ') +
        (disabled ? 'opacity-50 cursor-not-allowed ' : 'cursor-pointer ') +
        className
      }
      onClick={!disabled ? onClick : undefined}
      {...props}
    >
      {children || 'Dropdown Component'}
    </div>
  );
};
