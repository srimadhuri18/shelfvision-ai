import React, { useState } from 'react';
import { Bell, AlertTriangle, AlertOctagon, CheckCheck, Check, Clock, Filter } from 'lucide-react';
import { acknowledgeAlert, acknowledgeAllAlerts } from '../services/api';

export default function AlertCenter({ alerts, onAlertsUpdated, shelfId }) {
  const [filter, setFilter] = useState('ALL');
  const [loadingId, setLoadingId] = useState(null);

  const handleAcknowledge = async (id) => {
    try {
      setLoadingId(id);
      await acknowledgeAlert(id);
      onAlertsUpdated();
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingId(null);
    }
  };

  const handleAckAll = async () => {
    try {
      await acknowledgeAllAlerts(shelfId);
      onAlertsUpdated();
    } catch (err) {
      console.error(err);
    }
  };

  const filteredAlerts = alerts.filter(a => {
    if (filter === 'ALL') return true;
    return a.alert_type === filter;
  });

  return (
    <div id="alert-center" className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm flex flex-col h-full scroll-mt-20">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-amber-400" />
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
            Real-Time Alert Feed
          </h3>
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-red-500/10 text-red-400 border border-red-500/20">
            {alerts.length} Active
          </span>
        </div>

        {alerts.length > 0 && (
          <button
            onClick={handleAckAll}
            className="text-xs text-slate-400 hover:text-white flex items-center gap-1 transition px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700"
          >
            <CheckCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Clear All</span>
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 py-3 text-xs border-b border-slate-800/60 overflow-x-auto">
        {['ALL', 'EMPTY', 'LOW_STOCK', 'MISPLACED'].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-2.5 py-1 rounded-lg font-medium transition ${
              filter === type
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800/80 text-slate-400 hover:text-slate-200'
            }`}
          >
            {type.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Alert List */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pt-3 max-h-[380px] pr-1">
        {filteredAlerts.length === 0 ? (
          <div className="py-12 text-center text-slate-500">
            <CheckCheck className="w-10 h-10 mx-auto mb-2 text-emerald-500/40" />
            <p className="text-sm font-medium text-slate-400">All shelves in optimal condition</p>
            <p className="text-xs text-slate-500 mt-0.5">No unacknowledged inventory anomalies</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const isCritical = alert.severity === 'CRITICAL';
            const isMisplaced = alert.alert_type === 'MISPLACED';
            const isLowStock = alert.alert_type === 'LOW_STOCK';

            let icon = <AlertOctagon className="w-4 h-4 text-red-400 shrink-0" />;
            let borderStyle = 'border-red-500/30 bg-red-950/10';

            if (isMisplaced) {
              icon = <AlertTriangle className="w-4 h-4 text-purple-400 shrink-0" />;
              borderStyle = 'border-purple-500/30 bg-purple-950/10';
            } else if (isLowStock) {
              icon = <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />;
              borderStyle = 'border-amber-500/30 bg-amber-950/10';
            }

            return (
              <div
                key={alert.id}
                className={`p-3 rounded-xl border flex items-start justify-between gap-3 transition ${borderStyle}`}
              >
                <div className="flex items-start gap-2.5">
                  <div className="mt-0.5">{icon}</div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white">{alert.section_label || 'Shelf Alert'}</span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1 leading-snug">{alert.message}</p>
                  </div>
                </div>

                <button
                  onClick={() => handleAcknowledge(alert.id)}
                  disabled={loadingId === alert.id}
                  className="px-2 py-1 rounded bg-slate-800 hover:bg-emerald-600 hover:text-white text-slate-300 text-[11px] font-semibold flex items-center gap-1 transition shrink-0 border border-slate-700"
                  title="Mark as resolved by staff"
                >
                  <Check className="w-3 h-3 text-emerald-400" />
                  <span>Resolve</span>
                </button>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
}
