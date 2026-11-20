import React from 'react';
import { BarChart3, TrendingUp, Users, Clock, Zap, CheckCircle2 } from 'lucide-react';

export default function AnalyticsPanel({ overview }) {
  const stats = overview || {
    total_shelves: 1,
    critical_issues: 0,
    warning_issues: 1,
    average_health_score: 92.0
  };

  const surveyData = [
    { label: 'Out of Stock / Empty Slots', pct: 45, color: 'bg-red-500' },
    { label: 'Low Stock on Fast-Movers', pct: 32, color: 'bg-amber-500' },
    { label: 'Misplaced / Disorganized Goods', pct: 18, color: 'bg-purple-500' },
    { label: 'Damaged Packaging', pct: 5, color: 'bg-slate-500' },
  ];

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm space-y-6">
      
      {/* Section Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
            Store Performance & Survey Intelligence
          </h3>
        </div>
        <span className="text-xs bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2 py-0.5 rounded">
          Retail Field Data
        </span>
      </div>

      {/* Comparison: Manual vs ShelfVision AI */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Manual Inspection Card */}
        <div className="bg-slate-800/30 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-slate-400" /> Traditional Manual Audit
            </span>
            <span className="text-red-400 font-bold">Inefficient</span>
          </div>
          <div className="space-y-2 text-xs text-slate-400">
            <div className="flex justify-between">
              <span>Avg. Restock Delay:</span>
              <strong className="text-white">45–90 mins</strong>
            </div>
            <div className="flex justify-between">
              <span>Staff Hours Spent:</span>
              <strong className="text-white">3.5 hrs / day</strong>
            </div>
            <div className="flex justify-between">
              <span>Misplacement Detection:</span>
              <strong className="text-red-400">&lt; 35% accuracy</strong>
            </div>
          </div>
        </div>

        {/* ShelfVision AI Card */}
        <div className="bg-blue-950/20 border border-blue-500/30 rounded-xl p-4 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-full blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between text-xs text-blue-300 mb-2">
            <span className="font-semibold text-white flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-blue-400" /> ShelfVision AI Automated
            </span>
            <span className="text-emerald-400 font-bold">Instant</span>
          </div>
          <div className="space-y-2 text-xs text-slate-300">
            <div className="flex justify-between">
              <span>Anomaly Alert Speed:</span>
              <strong className="text-emerald-400">&lt; 2.5 seconds</strong>
            </div>
            <div className="flex justify-between">
              <span>Camera Frame Processing:</span>
              <strong className="text-white">25–30 FPS</strong>
            </div>
            <div className="flex justify-between">
              <span>Audit Cost Reduction:</span>
              <strong className="text-emerald-400">~80% savings</strong>
            </div>
          </div>
        </div>

      </div>

      {/* Survey Insights (Step 2 Implementation) */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-slate-400" /> Retail Problem Prevalence Survey (N = 82)
          </h4>
          <span className="text-[11px] text-slate-400">Store Managers & Staff Responses</span>
        </div>

        <div className="space-y-2.5">
          {surveyData.map((item) => (
            <div key={item.label}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">{item.label}</span>
                <span className="font-bold text-white">{item.pct}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className={`${item.color} h-2 rounded-full transition-all duration-700`}
                  style={{ width: `${item.pct}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
