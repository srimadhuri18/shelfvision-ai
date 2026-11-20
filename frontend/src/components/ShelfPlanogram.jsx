import React from 'react';
import { Package, AlertCircle, CheckCircle, HelpCircle, Layers } from 'lucide-react';

export default function ShelfPlanogram({ sections }) {
  if (!sections || sections.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 text-center text-slate-400">
        No shelf sections configured yet.
      </div>
    );
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
            Digital Shelf Planogram
          </h3>
        </div>
        <span className="text-xs text-slate-400">
          Spatial ROI Section Mapping
        </span>
      </div>

      {/* Grid of Shelf Sections */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
        {sections.map((sec) => {
          const isNormal = sec.status === 'NORMAL';
          const isLow = sec.status === 'LOW_STOCK';
          const isEmpty = sec.status === 'EMPTY';
          const isMisplaced = sec.status === 'MISPLACED';

          let borderClass = 'border-emerald-500/30 bg-emerald-950/10';
          let statusBadge = (
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              NORMAL
            </span>
          );
          let progressBg = 'bg-emerald-500';

          if (isEmpty) {
            borderClass = 'border-red-500/40 bg-red-950/20 animate-pulse';
            statusBadge = (
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/30">
                EMPTY
              </span>
            );
            progressBg = 'bg-red-500';
          } else if (isMisplaced) {
            borderClass = 'border-purple-500/40 bg-purple-950/20';
            statusBadge = (
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                MISPLACED ITEM
              </span>
            );
            progressBg = 'bg-purple-500';
          } else if (isLow) {
            borderClass = 'border-amber-500/40 bg-amber-950/20';
            statusBadge = (
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                LOW STOCK
              </span>
            );
            progressBg = 'bg-amber-500';
          }

          const fillPercentage = Math.min(100, Math.round((sec.detected_count / sec.capacity) * 100));

          return (
            <div
              key={sec.section_id || sec.label}
              className={`border rounded-xl p-4 transition-all duration-300 relative ${borderClass}`}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-200">{sec.label}</span>
                {statusBadge}
              </div>

              {/* Product Info */}
              <div className="space-y-1 mb-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Target Product:</span>
                  <span className="font-semibold text-white">{sec.expected_product}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Category:</span>
                  <span className="text-slate-300">{sec.expected_category}</span>
                </div>
              </div>

              {/* Counts & Capacity Bar */}
              <div className="pt-2 border-t border-slate-800/80">
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="text-slate-400">Inventory Level</span>
                  <span className="font-bold text-white">
                    {sec.detected_count} / {sec.capacity} items
                  </span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div
                    className={`${progressBg} h-full rounded-full transition-all duration-500`}
                    style={{ width: `${fillPercentage}%` }}
                  ></div>
                </div>
              </div>

              {/* Misplaced item warning note */}
              {sec.misplaced_count > 0 && (
                <div className="mt-2.5 px-2 py-1 bg-purple-500/10 border border-purple-500/20 rounded text-[11px] text-purple-300 flex items-center gap-1.5">
                  <AlertCircle className="w-3.5 h-3.5 shrink-0 text-purple-400" />
                  <span>{sec.misplaced_count} unauthorized product(s) detected in this slot!</span>
                </div>
              )}

            </div>
          );
        })}
      </div>
    </div>
  );
}
