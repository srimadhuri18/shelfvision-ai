import React from 'react';
import { Award, CheckCircle2, AlertTriangle, XCircle, Shuffle, TrendingUp } from 'lucide-react';

export default function ShelfHealthCard({ healthData, liveStats }) {
  const metrics = healthData?.metrics || {
    health_score: 92,
    availability_pct: 100,
    placement_accuracy_pct: 88,
    stock_level_pct: 75,
    status_label: 'EXCELLENT'
  };

  const score = metrics.health_score;

  // Determine color theme based on score
  let scoreColor = 'text-emerald-400';
  let ringColor = 'stroke-emerald-500';
  let badgeBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';

  if (score < 50) {
    scoreColor = 'text-red-400';
    ringColor = 'stroke-red-500';
    badgeBg = 'bg-red-500/10 text-red-400 border-red-500/30';
  } else if (score < 70) {
    scoreColor = 'text-amber-400';
    ringColor = 'stroke-amber-500';
    badgeBg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  } else if (score < 85) {
    scoreColor = 'text-blue-400';
    ringColor = 'stroke-blue-500';
    badgeBg = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
  }

  // Circular gauge calculation (circumference = 2 * PI * r)
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm relative overflow-hidden">
      
      {/* Background glow */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-blue-500/5 rounded-full blur-3xl -z-10 pointer-events-none"></div>

      <div className="flex flex-col md:flex-row items-center justify-between gap-6">
        
        {/* Left: Health Score Radial Gauge */}
        <div className="flex items-center gap-5">
          <div className="relative w-28 h-28 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r={radius}
                className="stroke-slate-800"
                strokeWidth="8"
                fill="transparent"
              />
              <circle
                cx="50"
                cy="50"
                r={radius}
                className={`${ringColor} transition-all duration-700 ease-out`}
                strokeWidth="8"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className={`text-2xl font-black ${scoreColor}`}>{Math.round(score)}</span>
              <span className="text-[10px] text-slate-400 font-medium">/ 100</span>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-white tracking-wide uppercase">AI Shelf Health Score</h2>
              <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full border ${badgeBg}`}>
                {metrics.status_label}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-xs">
              Automated composite score measuring shelf stock sufficiency, item availability, and placement compliance.
            </p>
          </div>
        </div>

        {/* Right: Key Breakdown Metrics */}
        <div className="grid grid-cols-3 gap-3 w-full md:w-auto flex-1 max-w-xl">
          
          <div className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-3">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Availability</span>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="text-lg font-bold text-white">{metrics.availability_pct}%</div>
            <div className="w-full bg-slate-700/60 rounded-full h-1.5 mt-2">
              <div
                className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${metrics.availability_pct}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-3">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Placement</span>
              <Shuffle className="w-3.5 h-3.5 text-purple-400" />
            </div>
            <div className="text-lg font-bold text-white">{metrics.placement_accuracy_pct}%</div>
            <div className="w-full bg-slate-700/60 rounded-full h-1.5 mt-2">
              <div
                className="bg-purple-500 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${metrics.placement_accuracy_pct}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-3">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Stock Level</span>
              <TrendingUp className="w-3.5 h-3.5 text-blue-400" />
            </div>
            <div className="text-lg font-bold text-white">{metrics.stock_level_pct}%</div>
            <div className="w-full bg-slate-700/60 rounded-full h-1.5 mt-2">
              <div
                className="bg-blue-500 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${metrics.stock_level_pct}%` }}
              ></div>
            </div>
          </div>

        </div>

      </div>

      {/* Mini Anomaly Summary Pills */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-4 text-xs text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          Total Sections: <strong className="text-white">{healthData?.total_sections || 4}</strong>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-red-500"></span>
          Empty Slots: <strong className="text-white">{healthData?.empty_sections || 0}</strong>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-500"></span>
          Low Stock: <strong className="text-white">{healthData?.low_stock_sections || 0}</strong>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-purple-500"></span>
          Misplaced Items: <strong className="text-white">{healthData?.misplaced_items_count || 0}</strong>
        </span>
      </div>

    </div>
  );
}
