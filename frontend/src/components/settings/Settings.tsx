import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CogIcon,
  BellIcon,
  KeyIcon,
  ShieldCheckIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  timezone: string;
  currency: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
    trading: boolean;
    alerts: boolean;
  };
  trading: {
    autoTrading: boolean;
    riskLevel: 'low' | 'medium' | 'high';
    maxPositionSize: number;
    stopLoss: number;
    takeProfit: number;
  };
  api: {
    binanceApiKey: string;
    binanceSecretKey: string;
    testnet: boolean;
  };
}

const Settings: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error] = useState<string | null>(null);
  const [settings, setSettings] = useState<UserSettings>({
    theme: 'system',
    language: 'en',
    timezone: 'UTC',
    currency: 'USD',
    notifications: {
      email: true,
      push: true,
      sms: false,
      trading: true,
      alerts: true
    },
    trading: {
      autoTrading: false,
      riskLevel: 'medium',
      maxPositionSize: 1000,
      stopLoss: 5,
      takeProfit: 10
    },
    api: {
      binanceApiKey: '',
      binanceSecretKey: '',
      testnet: true
    }
  });
  const [activeTab, setActiveTab] = useState<'general' | 'notifications' | 'trading' | 'api' | 'security'>('general');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const handleSettingChange = (path: string, value: any) => {
    setSettings(prev => {
      const newSettings = { ...prev };
      const keys = path.split('.');
      let current: any = newSettings;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newSettings;
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSaving(false);
    // Show success message
  };

  const tabs = [
    { id: 'general', name: 'General', icon: CogIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'trading', name: 'Trading', icon: ChartBarIcon },
    { id: 'api', name: 'API Keys', icon: KeyIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon }
  ];

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-neutral-600 dark:text-neutral-400">Loading settings...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <div className="text-red-600 dark:text-red-400">Error: {error}</div>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">
          Settings
        </h2>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="flex space-x-1 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-600'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.name}</span>
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'general' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
                  General Settings
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      Theme
                    </label>
                    <select
                      value={settings.theme}
                      onChange={(e) => handleSettingChange('theme', e.target.value)}
                      className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                    >
                      <option value="light">Light</option>
                      <option value="dark">Dark</option>
                      <option value="system">System</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      Language
                    </label>
                    <select
                      value={settings.language}
                      onChange={(e) => handleSettingChange('language', e.target.value)}
                      className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                    >
                      <option value="en">English</option>
                      <option value="ko">한국어</option>
                      <option value="ja">日本語</option>
                      <option value="zh">中文</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      Timezone
                    </label>
                    <select
                      value={settings.timezone}
                      onChange={(e) => handleSettingChange('timezone', e.target.value)}
                      className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                    >
                      <option value="UTC">UTC</option>
                      <option value="Asia/Seoul">Asia/Seoul</option>
                      <option value="America/New_York">America/New_York</option>
                      <option value="Europe/London">Europe/London</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      Currency
                    </label>
                    <select
                      value={settings.currency}
                      onChange={(e) => handleSettingChange('currency', e.target.value)}
                      className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                    >
                      <option value="USD">USD</option>
                      <option value="KRW">KRW</option>
                      <option value="EUR">EUR</option>
                      <option value="JPY">JPY</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
                  Notification Settings
                </h3>
                <div className="space-y-4">
                  {Object.entries(settings.notifications).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                          {key.charAt(0).toUpperCase() + key.slice(1)} Notifications
                        </div>
                        <div className="text-xs text-neutral-500 dark:text-neutral-500">
                          {key === 'email' && 'Receive notifications via email'}
                          {key === 'push' && 'Receive push notifications'}
                          {key === 'sms' && 'Receive SMS notifications'}
                          {key === 'trading' && 'Trading activity notifications'}
                          {key === 'alerts' && 'Price and market alerts'}
                        </div>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={value}
                          onChange={(e) => handleSettingChange(`notifications.${key}`, e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-neutral-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-neutral-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-neutral-600 peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'trading' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
                  Trading Settings
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                        Auto Trading
                      </div>
                      <div className="text-xs text-neutral-500 dark:text-neutral-500">
                        Enable automated trading based on AI signals
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.trading.autoTrading}
                        onChange={(e) => handleSettingChange('trading.autoTrading', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-neutral-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-neutral-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-neutral-600 peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      Risk Level
                    </label>
                    <select
                      value={settings.trading.riskLevel}
                      onChange={(e) => handleSettingChange('trading.riskLevel', e.target.value)}
                      className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      Max Position Size (USD)
                    </label>
                    <input
                      type="number"
                      value={settings.trading.maxPositionSize}
                      onChange={(e) => handleSettingChange('trading.maxPositionSize', Number(e.target.value))}
                      className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                        Stop Loss (%)
                      </label>
                      <input
                        type="number"
                        value={settings.trading.stopLoss}
                        onChange={(e) => handleSettingChange('trading.stopLoss', Number(e.target.value))}
                        className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                        Take Profit (%)
                      </label>
                      <input
                        type="number"
                        value={settings.trading.takeProfit}
                        onChange={(e) => handleSettingChange('trading.takeProfit', Number(e.target.value))}
                        className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'api' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
                  API Keys
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      Binance API Key
                    </label>
                    <input
                      type="password"
                      value={settings.api.binanceApiKey}
                      onChange={(e) => handleSettingChange('api.binanceApiKey', e.target.value)}
                      placeholder="Enter your Binance API key"
                      className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      Binance Secret Key
                    </label>
                    <input
                      type="password"
                      value={settings.api.binanceSecretKey}
                      onChange={(e) => handleSettingChange('api.binanceSecretKey', e.target.value)}
                      placeholder="Enter your Binance secret key"
                      className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                        Testnet Mode
                      </div>
                      <div className="text-xs text-neutral-500 dark:text-neutral-500">
                        Use testnet for safe testing
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.api.testnet}
                        onChange={(e) => handleSettingChange('api.testnet', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-neutral-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-neutral-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-neutral-600 peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
                  Security Settings
                </h3>
                <div className="space-y-4">
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <ShieldCheckIcon className="w-5 h-5 text-yellow-600" />
                      <span className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                        Security Notice
                      </span>
                    </div>
                    <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                      Keep your API keys secure and never share them with anyone. Enable 2FA for additional security.
                    </p>
                  </div>
                  <div className="space-y-3">
                    <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                      Enable Two-Factor Authentication
                    </button>
                    <button className="w-full px-4 py-2 bg-neutral-600 text-white rounded-md hover:bg-neutral-700">
                      Change Password
                    </button>
                    <button className="w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700">
                      Revoke All API Keys
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
};

export default Settings;