import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `block p-4 hover:bg-gray-700 ${isActive ? 'bg-gray-700' : ''}`;

  return (
    <div className="w-64 bg-gray-800 text-white">
      <div className="p-4 font-bold text-lg">Audio-Chat</div>
      <nav>
        <ul>
          <li><NavLink to="/" className={navLinkClass}>Home</NavLink></li>
          <li><NavLink to="/audio" className={navLinkClass}>Audio</NavLink></li>
          <li><NavLink to="/export" className={navLinkClass}>Export</NavLink></li>
          <li><NavLink to="/stats" className={navLinkClass}>Stats</NavLink></li>
          <li><NavLink to="/llm" className={navLinkClass}>LLM</NavLink></li>
          <li><NavLink to="/profile" className={navLinkClass}>Profile</NavLink></li>
          <li><NavLink to="/settings" className={navLinkClass}>Settings</NavLink></li>
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
