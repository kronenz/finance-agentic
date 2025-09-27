import React from 'react';

// Placeholder icons
import { SunIcon, MoonIcon, ChartBarIcon, BellAlertIcon, TableCellsIcon, BookOpenIcon, NewspaperIcon } from '@heroicons/react/24/outline';

// Recharts components for placeholder charts
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// const ResponsiveGridLayout = WidthProvider(Responsive);

// --- Mock Data ---
const priceChartData = [
  { name: '09:00', price: 100 }, { name: '09:05', price: 102 }, { name: '09:10', price: 101 }, 
  { name: '09:15', price: 105 }, { name: '09:20', price: 110 }, { name: '09:25', price: 108 },
];

// --- Widget Components (Placeholders) ---

const Widget: React.FC<{ title: string; icon: React.ReactNode; children: React.ReactNode }> = ({ title, icon, children }) => (
  <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 h-full flex flex-col">
    <div className="p-4 border-b border-neutral-200 dark:border-neutral-700 flex items-center space-x-2">
      {icon}
      <h3 className="font-semibold text-neutral-800 dark:text-neutral-200">{title}</h3>
    </div>
    <div className="flex-grow p-4 overflow-hidden">
      {children}
    </div>
  </div>
);

const PriceChartWidget = () => (
  <Widget title="Price Chart" icon={<ChartBarIcon className="w-5 h-5 text-blue-500"/>}>
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={priceChartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(128, 128, 128, 0.3)"/>
        <XAxis dataKey="name" stroke="#9ca3af"/>
        <YAxis stroke="#9ca3af"/>
        <Tooltip contentStyle={{ backgroundColor: '#374151', border: 'none' }}/>
        <Legend />
        <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={false}/>
      </LineChart>
    </ResponsiveContainer>
  </Widget>
);

const TradingSignalsWidget = () => {
    // const { data: signal, isConnected } = useSocket<{ type: 'buy' | 'sell', price: number, time: string }>('trading-signal');
    const signal = null;
    const isConnected = true;
    return (
        <Widget title="Trading Signals" icon={<BellAlertIcon className="w-5 h-5 text-yellow-500"/>}>
            <div className="text-sm text-neutral-600 dark:text-neutral-400">
                <p>Status: {isConnected ? <span className='text-green-500'>Connected</span> : <span className='text-red-500'>Disconnected</span>}</p>
                {signal ? (
                    <div className={`mt-4 p-3 rounded ${(signal as any).type === 'buy' ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                        <p>New Signal: <span className={`font-bold ${(signal as any).type === 'buy' ? 'text-green-400' : 'text-red-400'}`}>{(signal as any).type.toUpperCase()}</span></p>
                        <p>Price: {(signal as any).price}</p>
                        <p>Time: {new Date((signal as any).time).toLocaleTimeString()}</p>
                    </div>
                ) : <p className="mt-4">Awaiting signals...</p>}
            </div>
        </Widget>
    );
};

const PositionStatusWidget = () => (
    <Widget title="Position Status" icon={<TableCellsIcon className="w-5 h-5 text-green-500"/>}>
        <div className="text-sm text-neutral-600 dark:text-neutral-400">
            <p>BTC/USD: <span className="font-bold text-green-400">LONG</span></p>
            <p>Entry Price: $68,000</p>
            <p>Unrealized P/L: <span className="text-green-400">+$1,250.75</span></p>
        </div>
    </Widget>
);

const OrderBookWidget = () => (
    <Widget title="Order Book" icon={<BookOpenIcon className="w-5 h-5 text-purple-500"/>}>
        <div className="text-xs text-neutral-600 dark:text-neutral-400">
            {/* Mock order book data */}
            <div className="flex justify-between"><span className="text-red-400">68500.50</span> <span>0.123</span> <span>1234.56</span></div>
            <div className="flex justify-between"><span className="text-red-400">68500.00</span> <span>0.456</span> <span>5678.90</span></div>
            <div className="h-2"></div>
            <div className="flex justify-between"><span className="text-green-400">68499.50</span> <span>0.789</span> <span>9012.34</span></div>
            <div className="flex justify-between"><span className="text-green-400">68499.00</span> <span>1.011</span> <span>12345.67</span></div>
        </div>
    </Widget>
);

const NewsFeedWidget = () => (
    <Widget title="News Feed" icon={<NewspaperIcon className="w-5 h-5 text-orange-500"/>}>
        <div className="text-sm text-neutral-600 dark:text-neutral-400 space-y-2">
            <p>Bitcoin surges past $70,000 resistance level.</p>
            <p>Ethereum developers announce new upgrade timeline.</p>
        </div>
    </Widget>
);

const widgetMap: { [key: string]: React.ReactNode } = {
    'priceChart': <PriceChartWidget />,
    'tradingSignals': <TradingSignalsWidget />,
    'positionStatus': <PositionStatusWidget />,
    'orderBook': <OrderBookWidget />,
    'newsFeed': <NewsFeedWidget />,
};

// --- Main Dashboard Component ---

const TradingDashboard: React.FC = () => {
  // const { theme, toggleTheme } = useTheme();
  const theme = 'light';
  const toggleTheme = () => {};

  const layouts = {
    lg: [
      { i: 'priceChart', x: 0, y: 0, w: 6, h: 8 },
      { i: 'tradingSignals', x: 6, y: 0, w: 3, h: 4 },
      { i: 'positionStatus', x: 6, y: 4, w: 3, h: 4 },
      { i: 'orderBook', x: 0, y: 8, w: 6, h: 6 },
      { i: 'newsFeed', x: 6, y: 8, w: 3, h: 6 },
    ],
    md: [
        { i: 'priceChart', x: 0, y: 0, w: 10, h: 8 },
        { i: 'tradingSignals', x: 0, y: 8, w: 5, h: 4 },
        { i: 'positionStatus', x: 5, y: 8, w: 5, h: 4 },
        { i: 'orderBook', x: 0, y: 12, w: 5, h: 6 },
        { i: 'newsFeed', x: 5, y: 12, w: 5, h: 6 },
    ],
  };

  return (
    <div className="min-h-screen bg-neutral-100 dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 transition-colors duration-300">
      <header className="bg-white dark:bg-neutral-800 shadow-sm border-b border-neutral-200 dark:border-neutral-700 sticky top-0 z-10">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-semibold">
              Professional Trading Dashboard
            </h1>
            <button onClick={toggleTheme} className="p-2 rounded-full hover:bg-neutral-200 dark:hover:bg-neutral-700">
              {theme === 'light' ? <MoonIcon className="w-6 h-6" /> : <SunIcon className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </header>

      <main className="p-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {layouts.lg.map(item => (
            <div key={item.i} className="widget-container">
              {widgetMap[item.i]}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};

export default TradingDashboard;