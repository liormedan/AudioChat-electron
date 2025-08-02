import React from 'react';
import { useLanguage } from '../../contexts/language-context';

interface MainLayoutGridProps {
  children: React.ReactNode;
  className?: string;
}

export const MainLayoutGrid: React.FC<MainLayoutGridProps> = ({ 
  children, 
  className = '' 
}) => {
  const { direction } = useLanguage();

  return (
    <div 
      className={`main-layout-grid ${direction === 'rtl' ? 'rtl' : 'ltr'} ${className}`}
      style={{
        display: 'grid',
        gridTemplateColumns: '240px 1fr',
        gridTemplateRows: '60px 1fr',
        height: '100vh',
        overflow: 'hidden'
      }}
    >
      {children}
    </div>
  );
};

interface ContentAreaProps {
  children: React.ReactNode;
  className?: string;
}

export const ContentArea: React.FC<ContentAreaProps> = ({ 
  children, 
  className = '' 
}) => {
  return (
    <div 
      className={`content-area ${className}`}
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '20px',
        padding: '20px',
        overflow: 'hidden',
        gridColumn: '2',
        gridRow: '2'
      }}
    >
      {children}
    </div>
  );
};

interface ColumnProps {
  children: React.ReactNode;
  className?: string;
  column?: 1 | 2 | 3;
}

export const Column: React.FC<ColumnProps> = ({ 
  children, 
  className = '',
  column = 1 
}) => {
  return (
    <div 
      className={`layout-column layout-column-${column} ${className}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        overflow: 'hidden'
      }}
    >
      {children}
    </div>
  );
};

interface CompactComponentProps {
  children: React.ReactNode;
  height: number;
  className?: string;
  scrollable?: boolean;
}

export const CompactComponent: React.FC<CompactComponentProps> = ({
  children,
  height,
  className = '',
  scrollable = false
}) => {
  return (
    <div 
      className={`compact-component ${className}`}
      style={{
        height: `${height}px`,
        overflow: scrollable ? 'auto' : 'hidden',
        display: 'flex',
        flexDirection: 'column',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        backgroundColor: 'var(--card)'
      }}
    >
      {children}
    </div>
  );
};