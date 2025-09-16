'use client';

import Image from 'next/image';

interface LogoProps {
  size?: 'small' | 'medium' | 'large';
  variant?: 'compact' | 'full';
  className?: string;
  'data-testid'?: string;
}

export function Logo({ size = 'medium', variant = 'compact', className = '', 'data-testid': dataTestId }: LogoProps) {
  const sizeClasses = {
    small: 'w-6 h-6',
    medium: 'w-10 h-10',
    large: 'w-16 h-16',
  };

  const imageSizes = {
    small: 24,
    medium: 40,
    large: 64,
  };

  const logoSrc = variant === 'compact' ? '/images/logo-compact.svg' : '/images/logo.svg';

  return (
    <div 
      className={`${sizeClasses[size]} flex items-center justify-center ${className}`}
      data-testid={dataTestId}
    >
      <Image
        src={logoSrc}
        alt="PTE QR Logo"
        width={imageSizes[size]}
        height={imageSizes[size]}
        className="w-full h-full"
        priority
      />
    </div>
  );
}
