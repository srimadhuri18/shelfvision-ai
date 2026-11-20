import React from 'react';
import { Camera, ShieldCheck, Bell, Store, Activity } from 'lucide-react';

export default function Navbar({ activeShelf, shelves, onSelectShelf, alertCount }) {
  return (
    <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Camera className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight">ShelfVision</span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded">AI</span>
            </div>
            <p className="text-xs text-slate-400 font-medium">Smart Retail Shelf & Inventory Anomaly Monitor</p>
          </div>
        </div>

        {/* Controls & Status */}
        <div className="flex items-center space-x-4">
          
          {/* Active Shelf Selector */}
          <div className="flex items-center space-x-2 bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs">
            <Store className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400">Shelf:</span>
            <select
              value={activeShelf?.id || ''}
              onChange={(e) => {
                const found = shelves.find(s => s.id === e.target.value);
                if (found) onSelectShelf(found);
              }}
              className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
            >
              {shelves.map((s) => (
                <option key={s.id} value={s.id} className="bg-slate-900 text-white">
                  {s.name} ({s.code})
                </option>
              ))}
            </select>
          </div>

          {/* Engine Status Badge */}
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="flex items-center gap-1">
              <Activity className="w-3 h-3" /> CV Engine Active (YOLOv8)
            </span>
          </div>

          {/* Alert Badge */}
          <div className="relative">
            <button
              onClick={() => {
                document.getElementById('alert-center')?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition cursor-pointer"
              title="Click to view Real-Time Alert Feed"
            >
              <Bell className="w-4 h-4" />
            </button>
            {alertCount > 0 && (
              <span className="absolute -top-1 -right-1 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 text-[10px] font-bold text-white items-center justify-center">
                  {alertCount > 9 ? '9+' : alertCount}
                </span>
              </span>
            )}
          </div>

        </div>

      </div>
    </header>
  );
}
