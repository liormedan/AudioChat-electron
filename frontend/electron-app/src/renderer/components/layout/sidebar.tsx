import React from 'react';
import { NavLink } from 'react-router-dom';
import { useLocale } from '../../contexts/locale-provider';

const Sidebar = () => {
  const { t, direction } = useLocale();
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `block p-4 hover:bg-gray-700 ${isActive ? 'bg-gray-700' : ''} ${
      direction === 'rtl' ? 'text-right' : ''
    }`;

  return (
    <div className={`w-64 bg-gray-800 text-white ${direction === 'rtl' ? 'text-right' : ''}`}>
      <div className="p-4 font-bold text-lg">{t('sidebar.title')}</div>
      <nav>
        <ul>
          <li><NavLink to="/" className={navLinkClass}>{t('sidebar.home')}</NavLink></li>
          <li><NavLink to="/terminal" className={navLinkClass}>{t('sidebar.terminal')}</NavLink></li>
          <li><NavLink to="/chat" className={navLinkClass}>{t('sidebar.chat')}</NavLink></li>
          <li><NavLink to="/audio" className={navLinkClass}>{t('sidebar.audio')}</NavLink></li>
          <li><NavLink to="/export" className={navLinkClass}>{t('sidebar.export')}</NavLink></li>
          <li><NavLink to="/stats" className={navLinkClass}>{t('sidebar.stats')}</NavLink></li>
          <li><NavLink to="/llm" className={navLinkClass}>{t('sidebar.llm')}</NavLink></li>
          <li><NavLink to="/testing" className={navLinkClass}>{t('sidebar.testing')}</NavLink></li>
          <li><NavLink to="/profile" className={navLinkClass}>{t('sidebar.profile')}</NavLink></li>
          <li><NavLink to="/settings" className={navLinkClass}>{t('sidebar.settings')}</NavLink></li>
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
