import React, { forwardRef } from 'react';
import { clsx } from 'clsx';

type ButtonVariant = 'primary' | 'secondary' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

type ButtonProps = {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: React.ReactNode;
} & React.ButtonHTMLAttributes<HTMLButtonElement>;

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', className, children, ...props }, ref) => {
    const baseStyles =
      'inline-flex items-center justify-center font-semibold rounded-lg focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 transition-all duration-200 ease-in-out';

    const variantStyles = {
      primary:
        'bg-primary-500 text-white hover:bg-primary-600 focus-visible:ring-primary-500 disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed shadow-sm hover:shadow-md hover:-translate-y-px',
      secondary:
        'bg-transparent text-primary-500 border border-primary-500 hover:bg-primary-50 hover:text-primary-600 focus-visible:ring-primary-500 disabled:border-gray-300 disabled:text-gray-400 disabled:bg-transparent',
      danger:
        'bg-danger-500 text-white hover:bg-danger-600 focus-visible:ring-danger-500 disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed shadow-sm hover:shadow-md hover:-translate-y-px',
    };

    const sizeStyles = {
      sm: 'px-3 py-1.5 text-xs',
      md: 'px-4 py-2 text-sm',
      lg: 'px-6 py-3 text-base',
    };

    return (
      <button
        ref={ref}
        className={clsx(
          baseStyles,
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
export type { ButtonProps };