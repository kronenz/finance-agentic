import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  ChartBarIcon,
  CreditCardIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: ChartBarIcon },
  { name: 'Subscription', href: '/subscription', icon: CreditCardIcon },
  { name: 'Profile', href: '/profile', icon: UserCircleIcon },
];

const MainLayout: React.FC = () => {
  const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
    clsx(
      'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
      isActive
        ? 'bg-primary-500 text-white'
        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
    );

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-gray-200 bg-white flex flex-col">
        <div className="h-16 flex items-center justify-center px-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-primary-600">AI Trading</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => (
            <NavLink key={item.name} to={item.href} className={navLinkClasses}>
              <item.icon className="h-5 w-5 mr-3" />
              {item.name}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-200">
          <button className="flex w-full items-center px-4 py-3 text-sm font-medium rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-900">
            <ArrowRightOnRectangleIcon className="h-5 w-5 mr-3" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;