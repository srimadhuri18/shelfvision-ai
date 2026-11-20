import React, { useState } from 'react';
import { Camera, RefreshCw, Maximize2, Layers, AlertCircle, Video } from 'lucide-react';
import { getVideoFeedUrl } from '../services/api';

export default function LiveVideoFeed({ shelfId, shelfName, totalDetections }) {
  const [feedTimestamp, setFeedTimestamp] = useState(Date.now());
  const [showOverlays, setShowOverlays] = useState(true);

  const handleRefresh = () => {
    setFeedTimestamp(Date.now());
  };

  const feedUrl = shelfId
    ? `${getVideoFeedUrl(shelfId)}&overlay=${showOverlays}`
    : '';

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-sm flex flex-col h-full">
      
      {/* Stream Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></div>
          <span className="font-semibold text-sm text-white">Live Camera Feed</span>
          <span className="text-xs text-slate-400">({shelfName || 'Shelf A1'})</span>
        </div>

        <div className="flex items-center space-x-2">
          {/* Detected items tag */}
          <span className="text-xs bg-blue-500/10 border border-blue-500/20 text-blue-400 px-2.5 py-1 rounded-lg font-medium">
            {totalDetections || 0} Products Tracked
          </span>

          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`p-1.5 rounded-lg border text-xs flex items-center gap-1 transition ${
              showOverlays
                ? 'bg-blue-600/20 border-blue-500/40 text-blue-300'
                : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}
            title="Toggle YOLO Bounding Boxes & Shelf Grids"
          >
            <Layers className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">AI Overlay</span>
          </button>

          <button
            onClick={handleRefresh}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition border border-slate-700"
            title="Refresh Stream"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Video Container */}
      <div className="relative flex-1 bg-black flex items-center justify-center min-h-[360px] max-h-[480px] overflow-hidden group">
        {shelfId ? (
          <img
            key={feedTimestamp}
            src={feedUrl}
            alt="Retail Shelf Camera Feed"
            className="w-full h-full object-contain"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        ) : (
          <div className="text-center text-slate-500 p-8">
            <Camera className="w-12 h-12 mx-auto mb-2 opacity-40 animate-pulse" />
            <p className="text-sm">Connecting to ShelfVision CV Stream...</p>
          </div>
        )}

        {/* Live HUD Watermark Overlay */}
        <div className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-md border border-white/10 text-[11px] text-slate-300 flex items-center gap-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>1080p Stream</span>
          <span className="text-slate-500">•</span>
          <span>OpenCV + YOLOv8</span>
          <span className="text-slate-500">•</span>
          <span>~25 FPS</span>
        </div>

        {/* Real-time Legend Indicator */}
        <div className="absolute top-3 right-3 bg-black/70 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 text-[10px] space-y-1 hidden sm:block">
          <div className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2 h-2 rounded bg-emerald-500"></span> Normal Stock
          </div>
          <div className="flex items-center gap-1.5 text-amber-400">
            <span className="w-2 h-2 rounded bg-amber-500"></span> Low Stock
          </div>
          <div className="flex items-center gap-1.5 text-red-400">
            <span className="w-2 h-2 rounded bg-red-500"></span> Empty Slot
          </div>
          <div className="flex items-center gap-1.5 text-purple-400">
            <span className="w-2 h-2 rounded bg-purple-500"></span> Misplaced Item
          </div>
        </div>

      </div>

    </div>
  );
}
