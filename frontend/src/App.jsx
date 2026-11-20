import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ShelfHealthCard from './components/ShelfHealthCard';
import LiveVideoFeed from './components/LiveVideoFeed';
import ShelfPlanogram from './components/ShelfPlanogram';
import AlertCenter from './components/AlertCenter';
import AnalyticsPanel from './components/AnalyticsPanel';
import {
  fetchShelves,
  fetchShelfDetails,
  fetchShelfHealth,
  fetchAlerts,
  fetchAnalyticsOverview,
  connectShelfWebSocket
} from './services/api';

export default function App() {
  const [shelves, setShelves] = useState([]);
  const [activeShelf, setActiveShelf] = useState(null);
  const [shelfDetails, setShelfDetails] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [analyticsOverview, setAnalyticsOverview] = useState(null);
  const [liveDetectionsCount, setLiveDetectionsCount] = useState(0);
  const [liveSections, setLiveSections] = useState([]);

  // Load initial store data
  useEffect(() => {
    async function initData() {
      try {
        const shelfList = await fetchShelves();
        setShelves(shelfList);
        if (shelfList.length > 0) {
          setActiveShelf(shelfList[0]);
        }
        const overview = await fetchAnalyticsOverview();
        setAnalyticsOverview(overview);
      } catch (err) {
        console.error('Failed to load initial shelves:', err);
      }
    }
    initData();
  }, []);

  // When active shelf changes, fetch details, health, and alerts
  useEffect(() => {
    if (!activeShelf) return;

    let ws = null;

    async function loadShelfState() {
      try {
        const details = await fetchShelfDetails(activeShelf.id);
        setShelfDetails(details);
        setLiveSections(details.sections || []);

        const health = await fetchShelfHealth(activeShelf.id);
        setHealthData(health);

        const currentAlerts = await fetchAlerts(activeShelf.id, true);
        setAlerts(currentAlerts);
      } catch (err) {
        console.error('Failed to load shelf state:', err);
      }
    }

    loadShelfState();

    // Connect WebSocket for live telemetry (400ms updates)
    try {
      ws = connectShelfWebSocket(
        activeShelf.id,
        (data) => {
          if (data.total_detected !== undefined) {
            setLiveDetectionsCount(data.total_detected);
          }
          if (data.sections) {
            setLiveSections(data.sections);
          }
          if (data.metrics) {
            setHealthData((prev) => ({
              ...(prev || {}),
              metrics: data.metrics,
              total_sections: data.sections?.length || 4,
              empty_sections: data.sections?.filter(s => s.status === 'EMPTY').length || 0,
              low_stock_sections: data.sections?.filter(s => s.status === 'LOW_STOCK').length || 0,
              misplaced_items_count: data.sections?.reduce((acc, s) => acc + (s.misplaced_count || 0), 0) || 0
            }));
          }
        },
        (err) => console.log('WS connection reconnecting...', err)
      );
    } catch (e) {
      console.error(e);
    }

    // Interval to refresh alerts every 4 seconds
    const alertInterval = setInterval(async () => {
      try {
        const updatedAlerts = await fetchAlerts(activeShelf.id, true);
        setAlerts(updatedAlerts);
      } catch (e) {}
    }, 4000);

    return () => {
      if (ws) ws.close();
      clearInterval(alertInterval);
    };
  }, [activeShelf]);

  const refreshAlerts = async () => {
    if (!activeShelf) return;
    try {
      const updated = await fetchAlerts(activeShelf.id, true);
      setAlerts(updated);
      const overview = await fetchAnalyticsOverview();
      setAnalyticsOverview(overview);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Navigation */}
      <Navbar
        activeShelf={activeShelf}
        shelves={shelves}
        onSelectShelf={setActiveShelf}
        alertCount={alerts.length}
      />

      {/* Main Content Dashboard */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        
        {/* Top: AI Shelf Health KPI Score Card */}
        <ShelfHealthCard healthData={healthData} />

        {/* Middle Grid: Live Camera Stream & Digital Planogram */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          
          {/* Live Video Feed (7 Cols) */}
          <div className="lg:col-span-7 h-full">
            <LiveVideoFeed
              shelfId={activeShelf?.id}
              shelfName={activeShelf?.name}
              totalDetections={liveDetectionsCount}
            />
          </div>

          {/* 2D Digital Planogram & Section Statuses (5 Cols) */}
          <div className="lg:col-span-5 h-full">
            <ShelfPlanogram sections={liveSections} />
          </div>

        </div>

        {/* Bottom Grid: Live Alert Center & Analytics / Survey Findings */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          
          {/* Alert Center (7 Cols) */}
          <div className="lg:col-span-7">
            <AlertCenter
              alerts={alerts}
              onAlertsUpdated={refreshAlerts}
              shelfId={activeShelf?.id}
            />
          </div>

          {/* Survey & Anomaly Analytics (5 Cols) */}
          <div className="lg:col-span-5">
            <AnalyticsPanel overview={analyticsOverview} />
          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-4 text-center text-xs text-slate-500">
        <p>ShelfVision AI • Real-Time Computer Vision System for Retail Shelf Monitoring and Inventory Anomaly Detection</p>
      </footer>
    </div>
  );
}
