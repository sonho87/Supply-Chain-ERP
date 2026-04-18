import React, { useState, useEffect } from 'react';
import { 
  XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, ComposedChart, Line, Brush, AreaChart, Area, BarChart, Bar, CartesianGrid, Legend
} from 'recharts';
import { 
  LayoutDashboard, Inbox, PackageSearch, SearchX, Truck, Archive, PlayCircle, BarChart as BarChartIcon, Cpu,
  AlertOctagon, CheckCircle2, Package, Filter, ChevronDown, CheckCircle, ArrowRight, ShieldCheck, FileClock,
  Briefcase, TrendingUp, Wallet, ShoppingCart, Activity, ArrowUpRight, Clock, FilePlus, ClipboardList, Menu, X, Download, Barcode, ScanLine, Search, Building2, Boxes, Users, Target, Zap, Navigation, Layers, Camera, ArrowRightLeft, Database, Plus, Map, Smartphone, ListChecks, Route, Cfc, Plug2, Bot, Send, Sparkles, BellRing
} from 'lucide-react';


// Data Mock
const initialChartData = [
  { day: '01', rate: 99.1, volume: 15400 },
  { day: '02', rate: 98.9, volume: 16200 },
  { day: '03', rate: 99.4, volume: 14800 },
  { day: '04', rate: 99.2, volume: 17100 },
  { day: '05', rate: 98.5, volume: 18500 }, // breach
  { day: '06', rate: 99.5, volume: 14200 },
  { day: '07', rate: 99.7, volume: 13900 },
  { day: '08', rate: 99.6, volume: 15100 },
  { day: '09', rate: 99.8, volume: 16000 },
  { day: '10', rate: 99.5, volume: 14500 }
];

const initialTableData = [
  { sku: 'R2-91A', bin: 'B-14', sys: 120, act: 118, status: 'Audit Req' },
  { sku: 'X7-11C', bin: 'V-02', sys: 45, act: 45, status: 'Clear' },
  { sku: 'M4-99P', bin: 'A-91', sys: 810, act: 800, status: 'Critical' },
  { sku: 'L1-00B', bin: 'C-10', sys: 12, act: 12, status: 'Clear' },
  { sku: 'K9-44Z', bin: 'D-05', sys: 50, act: 51, status: 'Audit Req' }
];

// Six Sigma Control Limits
const UCL = 99.9;
const LCL = 98.8;
const TARGET = 99.6;

const initialRevenueData = [
  { day: 'Mon', revenue: 12.4, orders: 1200 },
  { day: 'Tue', revenue: 14.1, orders: 1350 },
  { day: 'Wed', revenue: 13.8, orders: 1310 },
  { day: 'Thu', revenue: 15.2, orders: 1480 },
  { day: 'Fri', revenue: 18.9, orders: 1850 },
  { day: 'Sat', revenue: 21.4, orders: 2100 },
  { day: 'Sun', revenue: 24.5, orders: 2450 },
];

const deadStockMetrics = {
  totalValueLocked: 1850400,
  stuckSKUs: 428,
  avgAge: 114,
  highRiskPlatform: 'Amazon'
};

const deadStockData = [
  { platform: 'Amazon', '30-60 Days': 420, '60-90 Days': 310, '90-120 Days': 150, '120+ Days': 85 },
  { platform: 'Flipkart', '30-60 Days': 310, '60-90 Days': 210, '90-120 Days': 95, '120+ Days': 40 },
  { platform: 'Myntra', '30-60 Days': 120, '60-90 Days': 85, '90-120 Days': 45, '120+ Days': 12 },
  { platform: 'Meesho', '30-60 Days': 250, '60-90 Days': 180, '90-120 Days': 60, '120+ Days': 20 },
  { platform: 'Nykaa', '30-60 Days': 80, '60-90 Days': 45, '90-120 Days': 25, '120+ Days': 5 },
];

const integrationPlatforms = [
  { id: 'amz', name: 'Amazon SP-API', status: 'Live', lastSync: 'Just now', icon: ShoppingCart, type: 'Marketplace' },
  { id: 'flk', name: 'Flipkart API', status: 'Live', lastSync: '2 mins ago', icon: ShoppingCart, type: 'Marketplace' },
  { id: 'myn', name: 'Myntra Partner', status: 'Syncing', lastSync: 'In Progress', icon: ShoppingCart, type: 'Fashion' },
  { id: 'shp', name: 'Shopify Admin', status: 'Failed', lastSync: '1 hr ago', icon: LayoutDashboard, type: 'D2C' },
];

const automationRules = [
  { id: 1, name: 'Low Stock Auto-Alert', condition: 'If SKU stock < Threshold (15)', action: 'Email Procurement Team', status: 'Active', appliesTo: 'All Marketplaces' },
  { id: 2, name: 'Dead Stock Demotion', condition: 'If SKU age > 120 Days', action: 'Reduce Price by 10% on Flipkart', status: 'Paused', appliesTo: 'Flipkart API' },
  { id: 3, name: 'Oversell Prevention', condition: 'When Stock = 0 on Master Node', action: 'Send Out-of-Stock flag to APIs', status: 'Active', appliesTo: 'All Marketplaces' },
];

const deadStockTable = [
  { id: '1', sku: 'SKU-AMZ-001', location: 'BIN-A1-05', marketplace: 'Amazon', daysStuck: 105, qty: 154, price: 450, total: 69300 },
  { id: '2', sku: 'SKU-FLK-042', location: 'BIN-C4-12', marketplace: 'Flipkart', daysStuck: 125, qty: 82, price: 1200, total: 98400 },
  { id: '3', sku: 'SKU-MYN-112', location: 'BIN-B2-08', marketplace: 'Myntra', daysStuck: 85, qty: 310, price: 650, total: 201500 },
  { id: '4', sku: 'SKU-MSH-091', location: 'BIN-E1-22', marketplace: 'Meesho', daysStuck: 110, qty: 1050, price: 150, total: 157500 },
  { id: '5', sku: 'SKU-NYK-882', location: 'BIN-F9-01', marketplace: 'Nykaa', daysStuck: 92, qty: 45, price: 850, total: 38250 },
  { id: '6', sku: 'SKU-AMZ-015', location: 'BIN-A3-44', marketplace: 'Amazon', daysStuck: 140, qty: 22, price: 2100, total: 46200 },
  { id: '7', sku: 'SKU-FLK-191', location: 'BIN-D7-19', marketplace: 'Flipkart', daysStuck: 95, qty: 65, price: 1100, total: 71500 },
  { id: '8', sku: 'SKU-AMZ-089', location: 'BIN-A2-11', marketplace: 'Amazon', daysStuck: 65, qty: 180, price: 300, total: 54000 },
];

const SIDEBAR_ITEMS = [
  { id: 'executive', label: 'Executive Summary', icon: Briefcase, alerts: 0 },
  { id: 'operations', label: 'Operations Command', icon: LayoutDashboard, alerts: 1 },
  { id: 'integrations', label: 'Platform Integrations', icon: Plug2, alerts: 0 },
  { id: 'audit', label: 'Audit Trail', icon: FileClock, alerts: 0 },
  { id: 'grn', label: 'Goods Inward', icon: Inbox, alerts: 0 },
  { id: 'bin', label: 'Bin Management', icon: Package, alerts: 0 },
  { id: 'picking', label: 'Picking Operations', icon: PackageSearch, alerts: 0 },
  { id: 'dispatch', label: 'Dispatch Control', icon: Truck, alerts: 0 },
  { id: 'mismatch', label: 'Inventory Mismatch', icon: SearchX, alerts: 0 },
  { id: 'deadstock', label: 'Dead Stock', icon: Archive, alerts: 0 },
  { id: 'dmaic', label: 'DMAIC Engine', icon: PlayCircle, alerts: 0 },
  { id: 'kpi', label: 'KPI Center', icon: BarChartIcon, alerts: 0 },
  { id: 'ai', label: 'ERP AI Assistant', icon: Bot, alerts: 0 },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('executive');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  // States for Real-time Polling Data
  const [chartData, setChartData] = useState(initialChartData);
  const [tableData, setTableData] = useState(initialTableData);
  
  // Executive Dashboard specific state
  const [executiveMetrics, setExecutiveMetrics] = useState({
    revenue: 2452000,
    orders: 3420,
    dispatched: 3150,
    avgCost: 45.10,
    openOrders: 270,
    aov: 716.95,
    leadTime: 1.2
  });

  const [kpis, setKpis] = useState([
    { label: 'Active SKUs', val: 14204, sub: 'Live counting active', trend: 'up', trendVal: '▲ 12%' },
    { label: 'Inventory Value', val: 110.42, sub: 'Cr. real-time estimate', trend: 'neutral', trendVal: 'Stable' },
    { label: 'Picking Accuracy', val: 99.2, sub: 'Below LCL Target', trend: 'down', alert: true, trendVal: 'Below LCL' },
    { label: 'Dispatch Vol.', val: 4205, sub: 'Pallets processed', trend: 'up', trendVal: '▲ 4.2%' },
    { label: 'Inv. Health Score', val: 94, sub: 'Stockout & Turnover index', trend: 'neutral', trendVal: 'Healthy', type: 'score' }
  ]);

  // Alert & Audit Trail States
  const [alertState, setAlertState] = useState({ 
    status: 'open', 
    step: 1, 
    rootCause: '', 
    correctiveAction: '' 
  });
  
  const [auditLogs, setAuditLogs] = useState([
    { id: 'AUD-9921', timestamp: new Date(Date.now() - 1200000).toLocaleString('en-GB'), operator: 'EX-S6-INDIA-01', action: 'Bin Variance Fixed', details: 'Corrected variance in BIN-A1-12. Adjusted -2 units. Root cause: Process leakage during picking.' },
    { id: 'GRN-3342', timestamp: new Date(Date.now() - 2400000).toLocaleString('en-GB'), operator: 'OP-INWARD-44', action: 'GRN 2-step Failed', details: 'Vendor label mismatch on PO-84192. Quantity mismatch detected via barcode scan. Pallet put into hold.' },
    { id: 'AUD-9920', timestamp: new Date(Date.now() - 3100000).toLocaleString('en-GB'), operator: 'EX-S6-INDIA-01', action: 'Cycle Count', details: 'Completed daily ABC priority cycle count. Accuracy 99.8%.' },
    { id: 'SYS-001', timestamp: new Date(Date.now() - 3600000).toLocaleString('en-GB'), operator: 'SYSTEM', action: 'Shift Initialized', details: 'Automated monitoring started.' }
  ]);

  const [grnScanState, setGrnScanState] = useState<{
    barcode: string;
    scanned: boolean;
    validating: boolean;
    suggestions: any[];
    cameraActive: boolean;
  }>({
    barcode: '',
    scanned: false,
    validating: false,
    suggestions: [],
    cameraActive: false
  });

  const [binTransferModal, setBinTransferModal] = useState<{
    isOpen: boolean;
    sourceBin: string;
    destBin: string;
    qty: string;
  }>({
    isOpen: false,
    sourceBin: '',
    destBin: '',
    qty: ''
  });

  const [bins, setBins] = useState([
    { id: 'BIN-A1-04', type: 'Active Pick', sku: 'SKU-8910', pct: 92, status: 'Optimal', vol: 'High Velocity' },
    { id: 'BIN-B4-12', type: 'Reserve Bulk', sku: 'SKU-1002', pct: 100, status: 'Full', vol: 'Med Velocity' },
    { id: 'BIN-C2-45', type: 'Active Pick', sku: 'SKU-4410', pct: 14, status: 'Refill Needed', vol: 'High Velocity' },
    { id: 'BIN-D1-01', type: 'Buffer Flow', sku: 'Mixed', pct: 45, status: 'Optimal', vol: 'Low Velocity' },
    { id: 'BIN-E5-99', type: 'Active Pick', sku: 'SKU-0912', pct: 0, status: 'Empty', vol: 'High Velocity' }
  ]);

  const [replenishmentTasks, setReplenishmentTasks] = useState([
    { sku: 'SKU-4410', from: 'BIN-B1-02 (Bulk)', to: 'BIN-C2-45 (Pick)', qty: 150, priority: 'Critical' },
    { sku: 'SKU-1122', from: 'INWARD-DOCK', to: 'BIN-A1-08 (Pick)', qty: 45, priority: 'Med' }
  ]);

  // Effect to automatically generate replenishment tasks for low bins
  useEffect(() => {
    const lowBins = bins.filter(b => b.pct < 20 && b.type === 'Active Pick');
    lowBins.forEach(lowBin => {
      const existingTask = replenishmentTasks.find(t => t.to.includes(lowBin.id));
      if (!existingTask) {
        setReplenishmentTasks(prev => [{
          sku: lowBin.sku,
          from: 'AUTO-REPLENISH-QUEUE',
          to: `${lowBin.id} (Pick)`,
          qty: 100,
          priority: lowBin.pct === 0 ? 'Critical' : 'High'
        }, ...prev]);
      }
    });
  }, [bins]);

  const [activeLeaderboardSort, setActiveLeaderboardSort] = useState<'rank' | 'lph' | 'acc'>('rank');
  const [leaderboardDateFilter, setLeaderboardDateFilter] = useState('today');
  const [pickerFilter, setPickerFilter] = useState('All');

  const [pickingEngine, setPickingEngine] = useState<{
    pendingOrders: number;
    pickers: { id: string; name: string; status: 'Available' | 'Picking' | 'Verifying' | 'Packing', isEditing: boolean }[];
    batches: { id: string; pickerId: string; status: 'Picking' | 'Verifying' | 'Handoff' | 'Completed'; items: number }[];
    packQueue: { orderId: string, status: 'Awaiting Pack' | 'Packed & Ready' }[];
    showGenerateSuccess: boolean;
  }>({
    pendingOrders: 142,
    pickers: [
      { id: 'P-1', name: 'AB', status: 'Available', isEditing: false },
      { id: 'P-2', name: 'ABC', status: 'Available', isEditing: false },
      { id: 'P-3', name: 'ABCD', status: 'Available', isEditing: false },
      { id: 'P-4', name: 'ABCDE', status: 'Available', isEditing: false },
      { id: 'P-5', name: 'ABCDEF', status: 'Available', isEditing: false },
      { id: 'P-6', name: 'ABCDEFG', status: 'Available', isEditing: false }
    ],
    batches: [],
    packQueue: [],
    showGenerateSuccess: false
  });

  const generateWave = () => {
    setPickingEngine(prev => {
      const availablePickers = prev.pickers.filter(p => p.status === 'Available');
      if (availablePickers.length === 0 || prev.pendingOrders === 0) return prev;

      const newBatches: any[] = [];
      let remainingOrders = prev.pendingOrders;
      const updatedPickers = [...prev.pickers];

      availablePickers.forEach(picker => {
        if (remainingOrders > 0) {
          const batchSize = Math.min(Math.floor(Math.random() * 15) + 10, remainingOrders); 
          remainingOrders -= batchSize;
          newBatches.push({
            id: `WAVE-${Math.floor(Math.random() * 9000) + 1000}`,
            pickerId: picker.name,
            status: 'Picking',
            items: batchSize
          });
          const pIdx = updatedPickers.findIndex(p => p.id === picker.id);
          if (pIdx > -1) updatedPickers[pIdx].status = 'Picking';
        }
      });

      return { ...prev, pendingOrders: remainingOrders, pickers: updatedPickers, batches: [...prev.batches, ...newBatches], showGenerateSuccess: true };
    });

    setTimeout(() => {
      setPickingEngine(prev => ({ ...prev, showGenerateSuccess: false }));
    }, 4000);
  };

  const advanceBatch = (batchId: string) => {
    setPickingEngine(prev => {
      const updatedBatches = [...prev.batches];
      const updatedPickers = [...prev.pickers];
      const updatedPackQueue = [...prev.packQueue];
      
      const bIdx = updatedBatches.findIndex(b => b.id === batchId);
      if (bIdx === -1) return prev;
      
      const batch = updatedBatches[bIdx];
      const pIdx = updatedPickers.findIndex(p => p.name === batch.pickerId);

      if (batch.status === 'Picking') {
        batch.status = 'Verifying';
        if (pIdx > -1) updatedPickers[pIdx].status = 'Verifying';
      } else if (batch.status === 'Verifying') {
        batch.status = 'Handoff';
        if (pIdx > -1) updatedPickers[pIdx].status = 'Available'; // Free them up
        // When handed off, push to pack queue
        updatedPackQueue.push({ orderId: `ORD-${batch.id.replace('WAVE-', '')}`, status: 'Awaiting Pack' });
      } else if (batch.status === 'Handoff') {
        batch.status = 'Completed';
      }

      return { ...prev, batches: updatedBatches, pickers: updatedPickers, packQueue: updatedPackQueue };
    });
  };

  const updatePickerName = (id: string, newName: string) => {
    setPickingEngine(prev => ({
      ...prev,
      pickers: prev.pickers.map(p => p.id === id ? { ...p, name: newName, isEditing: false } : p)
    }));
  };

  const setPickerEditing = (id: string, isEditing: boolean) => {
    setPickingEngine(prev => ({
      ...prev,
      pickers: prev.pickers.map(p => p.id === id ? { ...p, isEditing } : p)
    }));
  };

  const [packScanInput, setPackScanInput] = useState('');
  
  const handlePackScan = (e: React.FormEvent) => {
    e.preventDefault();
    if (!packScanInput.trim()) return;
    
    setPickingEngine(prev => {
      const q = [...prev.packQueue];
      const i = q.findIndex(item => item.orderId === packScanInput.trim());
      if (i > -1) {
        q[i].status = 'Packed & Ready';
      }
      return { ...prev, packQueue: q };
    });
    setPackScanInput('');
  };

  const downloadCSV = (content: string, filename: string) => {
    try {
      const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", filename);
      // Ensure the link is appended to body for Firefox/Safari compatibility
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
      alert("Download failed. If you are inside the preview iframe, please use the 'Open in New Tab' button in the top right.");
    }
  };

  const generatePicklistData = (batch: any) => {
    let data = "";
    const zones = ['A1', 'B2', 'C4', 'D1', 'E5'];
    // Generate distinct items dynamically based on the batch size requirement
    for(let i=0; i<Math.max(3, batch.items); i++) {
       const sku = `SKU-${Math.floor(1000 + Math.random() * 9000)}`;
       const bin = `BIN-${zones[Math.floor(Math.random() * zones.length)]}-${Math.floor(1 + Math.random() * 20)}`;
       const rack = `R-${Math.floor(Math.random() * 5)}-${Math.floor(1 + Math.random() * 9)}`;
       const qty = Math.floor(1 + Math.random() * 4);
       data += `${batch.id},${batch.pickerId},${sku},${bin},${rack},${qty}\n`;
    }
    return data;
  };

  const downloadIndividualPicklist = (batch: any) => {
    const header = "Wave/Batch ID,Picker Name,SKU,Bin Number,Rack Number,Quantity\n";
    downloadCSV(header + generatePicklistData(batch), `${batch.id}_picklist.csv`);
  };

  const downloadAllPicklists = () => {
    let content = "Wave/Batch ID,Picker Name,SKU,Bin Number,Rack Number,Quantity\n";
    pickingEngine.batches.forEach(batch => {
      content += generatePicklistData(batch);
    });
    downloadCSV(content, `all_active_picklists_export.csv`);
  };

  const handleExecuteTransfer = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate updating bin state
    if (binTransferModal.sourceBin) {
      setBins(prev => prev.map(b => b.id === binTransferModal.sourceBin ? { ...b, pct: Math.max(0, b.pct - 30) } : b));
    }
    if (binTransferModal.destBin) {
      setBins(prev => prev.map(b => b.id === binTransferModal.destBin ? { ...b, pct: Math.min(100, b.pct + 30) } : b));
    }
    setBinTransferModal(prev => ({ ...prev, isOpen: false }));
    // Append to audit
    setAuditLogs(prev => [{
      id: `TRF-${Math.floor(Math.random() * 9000)}`,
      timestamp: new Date().toLocaleString('en-GB'),
      operator: 'EX-S6-INDIA-01',
      action: 'Bin-to-Bin Transfer',
      details: `Moved ${binTransferModal.qty} units from ${binTransferModal.sourceBin} to ${binTransferModal.destBin}.`
    }, ...prev]);
  };

  const handleBarcodeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!grnScanState.barcode) return;
    setGrnScanState(prev => ({ ...prev, validating: true, scanned: true, cameraActive: false }));
    setTimeout(() => {
      setGrnScanState(prev => ({
        ...prev,
        validating: false,
        suggestions: [
          { bin: 'BIN-C4-12', zone: 'Fast Moving', score: 98, reason: 'Adjacent to same style variants' },
          { bin: 'BIN-C4-15', zone: 'Fast Moving', score: 85, reason: 'Empty bin in high-velocity zone' },
        ]
      }));
    }, 800);
  };

  const simulateCameraScan = () => {
    setGrnScanState(prev => ({ ...prev, cameraActive: true }));
    // Simulate finding a barcode after 2.5 seconds
    setTimeout(() => {
      setGrnScanState(prev => ({
        ...prev,
        barcode: 'SKU-88219-AUTO',
        cameraActive: false
      }));
      // Auto submit
      handleBarcodeSubmit({ preventDefault: () => {} } as any);
    }, 2500);
  };

  const resetScan = () => {
    setGrnScanState({ barcode: '', scanned: false, validating: false, suggestions: [], cameraActive: false });
  };

  const currentDateTime = new Date().toLocaleDateString('en-GB', { 
    weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' 
  });

  // Polling Simulation: Jiggle data every 3 seconds to simulate WebSockets/live updates
  useEffect(() => {
    const interval = setInterval(() => {
      // 1. Update Chart Data Streams
      setChartData(prev => {
        const newData = [...prev];
        const last = newData[newData.length - 1];
        const newDay = String(parseInt(last.day, 10) + 1).padStart(2, '0');
        // Random walk for rate, constrained between 98.0 and 100
        const newRate = Number(Math.min(100, Math.max(98, last.rate + (Math.random() * 0.4 - 0.2))).toFixed(2));
        newData.push({ day: newDay, rate: newRate, volume: Math.floor(14000 + Math.random() * 2000) });
        // Keep window at 20 points
        if (newData.length > 20) newData.shift();
        return newData;
      });

      // 2. Update Ops KPIs
      setKpis(prev => {
        const newKpis = [...prev];
        // Fluctuate active SKUs slightly
        newKpis[0].val = Math.max(14000, newKpis[0].val + Math.floor(Math.random() * 5 - 2));
        // Fluctuate Dispatch Vol.
        newKpis[3].val = newKpis[3].val + Math.floor(Math.random() * 3);
        // Fluctuate Health Score occasionally
        if (Math.random() > 0.7 && newKpis[4]) {
          newKpis[4].val = Math.min(100, Math.max(65, newKpis[4].val + Math.floor(Math.random() * 3 - 1)));
        }
        return newKpis;
      });

      // 3. Update Executive Metrics
      setExecutiveMetrics(prev => {
        const factor = Math.random();
        return {
          ...prev,
          revenue: prev.revenue + Math.floor(Math.random() * 2500),
          orders: prev.orders + (factor > 0.5 ? 1 : 0),
          dispatched: prev.dispatched + (factor > 0.3 ? 1 : 0),
          openOrders: prev.openOrders + (factor > 0.5 ? 1 : -1)
        }
      });

      // 4. Update Table Real-time Mismatches (simulate scan updates)
      setTableData(prev => {
        const updated = [...prev];
        // Jiggle the "sys vs act" slightly to show live changes
        if (Math.random() > 0.5) {
          const randomIndex = Math.floor(Math.random() * updated.length);
          if (updated[randomIndex].status !== 'Critical') {
             updated[randomIndex].act += Math.floor(Math.random() * 3 - 1);
             updated[randomIndex].status = updated[randomIndex].sys === updated[randomIndex].act ? 'Clear' : 'Audit Req';
          }
        }
        return updated;
      });
      
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  // Root Cause / Wizard Controls
  const handleAlertNextStep = () => {
    if (alertState.step === 1 && alertState.rootCause) {
      setAlertState({ ...alertState, step: 2 });
    } else if (alertState.step === 2 && alertState.correctiveAction) {
      setAlertState({ ...alertState, step: 3 });
    } else if (alertState.step === 3) {
      setAlertState({ ...alertState, status: 'resolved' });
      
      // Update KPIs since alert is cleared
      setKpis(prev => {
        const reset = [...prev];
        reset[2].alert = false;
        reset[2].trendVal = 'Stabilizing';
        return reset;
      });

      // Log to Audit Trail
      setAuditLogs(prev => [
        { 
          id: `CAPA-${Math.floor(Math.random() * 10000)}`, 
          timestamp: new Date().toLocaleString('en-GB'),
          operator: 'EX-S6-INDIA-01',
          action: 'Resolved Process Breach (Picking Accuracy)',
          details: `Cause: ${alertState.rootCause} | CAPA: ${alertState.correctiveAction}`
        },
        ...prev
      ]);
    }
  };

  return (
    <div className="flex h-screen bg-bg overflow-hidden font-sans">
      
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-accent/20 backdrop-blur-sm z-30 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 w-[240px] bg-sidebar text-text-muted flex flex-col flex-shrink-0 border-r border-border shadow-[1px_0_4px_rgba(0,0,0,0.02)] z-40 transform transition-transform duration-300 md:relative md:translate-x-0 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="py-8 px-6 border-b border-border flex justify-between items-center">
          <div className="flex items-center gap-2">
            <h1 className="font-heading font-bold text-xl text-accent tracking-tighter uppercase">
              SigmaOps <span className="font-light opacity-60">ERP</span>
            </h1>
          </div>
          <button onClick={() => setIsSidebarOpen(false)} className="md:hidden text-text-muted hover:text-accent">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-6 space-y-0.5">
          {SIDEBAR_ITEMS.map((item) => {
            // Recalculate alerts dynamic check
            const showAlert = item.id === 'operations' && alertState.status === 'open';
            return (
              <button
                key={item.id}
                onClick={() => { setActiveTab(item.id); setIsSidebarOpen(false); }}
                className={`w-full flex items-center gap-3 px-6 py-3 transition-colors text-sm font-medium border-l-[3px] ${
                  activeTab === item.id 
                    ? 'bg-slate-100/70 text-accent border-l-accent' 
                    : 'hover:bg-slate-50 text-text-muted border-l-transparent'
                }`}
              >
                <item.icon className="w-4 h-4 opacity-70 flex-shrink-0" />
                <span className="flex-1 text-left text-[13px]">{item.label}</span>
                {showAlert && (
                  <span className="flex items-center justify-center w-5 h-5 bg-error/10 text-error text-[10px] font-bold rounded-full flex-shrink-0">
                    {item.alerts}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <div className="p-6 border-t border-border text-left">
          <div className="text-[11px] text-text-muted">
            v4.2.1-Enterprise<br/>
            Six Sigma Compliance: <span className="text-success font-semibold tracking-wide">99.2%</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden w-full">
        {/* Topbar */}
        <header className="h-[72px] bg-white border-b border-border flex items-center justify-between px-4 md:px-8 flex-shrink-0 z-10 shadow-[0_1px_3px_rgba(0,0,0,0.01)]">
          <div className="flex items-center gap-3 md:gap-4">
            <button onClick={() => setIsSidebarOpen(true)} className="md:hidden text-accent hover:bg-slate-50 p-2 rounded-md">
              <Menu className="w-5 h-5" />
            </button>
            <div className="text-lg md:text-xl font-heading font-semibold text-accent tracking-tight truncate max-w-[180px] sm:max-w-xs md:max-w-none">
              {SIDEBAR_ITEMS.find(i => i.id === activeTab)?.label || 'Command Center'}
            </div>
            {/* Live Indicator inside Header */}
            <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded text-[10px] font-bold uppercase tracking-widest ml-4">
              <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
              Live Polling
            </div>
          </div>
          <div className="flex items-center gap-4 md:gap-6 text-sm">
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-700 border border-amber-200 rounded-full font-medium text-xs cursor-pointer hover:bg-amber-100 transition-colors" onClick={() => setActiveTab('integrations')}>
              <AlertOctagon className="w-3.5 h-3.5" />
              1 Fast-Selling SKU Low
            </div>

            {alertState.status === 'open' && (
              <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-[#FEF2F2] text-error border border-[#FEE2E2] rounded-full font-medium text-xs">
                <AlertOctagon className="w-3.5 h-3.5" />
                1 Critical Exception
              </div>
            )}
            <div className="text-right flex flex-col items-end hidden sm:flex">
              <div className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">OPERATOR ID</div>
              <div className="text-sm font-semibold text-text-main font-heading">EX-S6-INDIA-01</div>
            </div>
            <div className="w-8 h-8 md:w-10 md:h-10 flex-shrink-0 bg-slate-100 border border-slate-200 rounded-full flex items-center justify-center font-bold text-slate-500 shadow-inner text-xs md:text-sm">
              OP
            </div>
          </div>
        </header>

        {/* Dynamic Content Body */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 relative">
          <div className="max-w-7xl mx-auto space-y-6">
            
            {activeTab === 'audit' && (
               <div className="space-y-6 animate-in fade-in duration-500">
                 <div className="flex items-end justify-between mb-4 border-b border-border pb-4">
                   <div>
                     <h2 className="text-2xl font-heading font-bold text-accent tracking-tight">System Audit Trail</h2>
                     <p className="text-sm text-text-muted mt-1">Immutable log of authenticated operator actions & DMAIC reviews</p>
                   </div>
                   <button className="flex items-center gap-2 px-4 py-2 border border-border text-sm font-semibold rounded hover:bg-slate-50 transition-colors text-text-main shadow-sm">
                     <Download className="w-4 h-4" />
                     Export to Excel
                   </button>
                 </div>

                 <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                   <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Cycle Count Accuracy</div>
                     <div className="font-heading text-3xl font-bold text-accent">99.8%</div>
                     <div className="text-[10px] text-success mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                       <TrendingUp className="w-3 h-3" /> Exceeds LCL Target
                     </div>
                   </div>
                   <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Variances Detected</div>
                     <div className="font-heading text-3xl font-bold text-accent">14</div>
                     <div className="text-[10px] text-accent mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                       <CheckCircle className="w-3 h-3" /> 12 Resolved today
                     </div>
                   </div>
                   <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Automated GRN Fails</div>
                     <div className="font-heading text-3xl font-bold text-error">2</div>
                     <div className="text-[10px] text-error mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                       <AlertOctagon className="w-3 h-3" /> Blocked inwarding
                     </div>
                   </div>
                 </div>
                 
                 <div className="enterprise-widget p-0 border border-border rounded-xl bg-white overflow-hidden">
                   <div className="overflow-x-auto">
                     <table className="w-full text-left text-sm border-collapse">
                       <thead className="bg-[#F8FAFC]">
                         <tr>
                           <th className="px-6 py-4 text-[11px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none">Timestamp / ID</th>
                           <th className="px-6 py-4 text-[11px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none">Operator</th>
                           <th className="px-6 py-4 text-[11px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none">Action</th>
                           <th className="px-6 py-4 text-[11px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none">Root Cause / Details</th>
                         </tr>
                       </thead>
                       <tbody className="bg-white divide-y divide-border">
                          {auditLogs.map((log) => (
                            <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                              <td className="px-6 py-4 align-top">
                                <div className="font-semibold text-accent text-xs">{log.timestamp}</div>
                                <div className="text-[10px] text-text-muted font-mono mt-1 tracking-wider">{log.id}</div>
                              </td>
                              <td className="px-6 py-4 text-[13px] font-semibold text-slate-600 align-top">{log.operator}</td>
                              <td className="px-6 py-4 text-[13px] font-bold text-accent align-top">
                                {log.action.includes('Failed') ? (
                                  <span className="text-error">{log.action}</span>
                                ) : log.action.includes('Fixed') ? (
                                  <span className="text-warning">{log.action}</span>
                                ) : (
                                  log.action
                                )}
                              </td>
                              <td className="px-6 py-4 text-[13px] text-text-muted leading-relaxed align-top">
                                {log.details}
                              </td>
                            </tr>
                          ))}
                       </tbody>
                     </table>
                   </div>
                 </div>
               </div>
            )}

            {activeTab === 'executive' && (
              <div className="space-y-6 animate-in fade-in duration-500">
                
                {/* Executive Hero Banner */}
                <div className="flex items-end justify-between mb-2">
                  <div>
                    <h2 className="text-2xl font-heading font-bold text-accent tracking-tight">Today's Performance Overview</h2>
                    <p className="text-sm text-text-muted mt-1">High-level metrics for {currentDateTime}</p>
                  </div>
                  {alertState.status === 'open' && (
                    <button 
                      onClick={() => setActiveTab('operations')}
                      className="flex items-center gap-2 px-4 py-2 bg-error/10 text-error rounded-full text-xs font-bold uppercase tracking-wide hover:bg-error/20 transition-colors cursor-pointer"
                    >
                      <AlertOctagon className="w-4 h-4" />
                      1 Ops Blocker
                    </button>
                  )}
                </div>

                {/* CEO KPI Bar - Simple, not crowded */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
                  {/* Revenue */}
                  <div className="bg-white p-6 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                    <div className="flex items-center gap-3 text-text-muted mb-4">
                      <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-600">
                        <Wallet className="w-4 h-4" />
                      </div>
                      <span className="text-xs font-bold uppercase tracking-wider">Gross Revenue</span>
                    </div>
                    <div className="font-heading text-4xl font-bold text-accent">
                      ₹{(executiveMetrics.revenue / 100000).toFixed(2)}<span className="text-xl text-text-muted">L</span>
                    </div>
                    <div className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-success">
                      <ArrowUpRight className="w-3.5 h-3.5" />
                      <span>+18.4% vs Yesterday</span>
                    </div>
                  </div>

                  {/* Orders */}
                  <div className="bg-white p-6 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                    <div className="flex items-center gap-3 text-text-muted mb-4">
                      <div className="w-8 h-8 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-600">
                        <ShoppingCart className="w-4 h-4" />
                      </div>
                      <span className="text-xs font-bold uppercase tracking-wider">Total Orders</span>
                    </div>
                    <div className="font-heading text-4xl font-bold text-accent">
                      {executiveMetrics.orders.toLocaleString()}
                    </div>
                    <div className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-success">
                      <ArrowUpRight className="w-3.5 h-3.5" />
                      <span>+5.2% vs Yesterday</span>
                    </div>
                  </div>

                  {/* Fulfillment Status */}
                  <div className="bg-white p-6 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                    <div className="flex items-center gap-3 text-text-muted mb-4">
                      <div className="w-8 h-8 rounded-full bg-amber-50 flex items-center justify-center text-amber-600">
                        <Activity className="w-4 h-4" />
                      </div>
                      <span className="text-xs font-bold uppercase tracking-wider">Fulfillment Rate</span>
                    </div>
                    <div className="font-heading text-4xl font-bold text-accent mb-3">
                      {Math.round((executiveMetrics.dispatched / executiveMetrics.orders) * 100)}<span className="text-xl text-text-muted">%</span>
                    </div>
                    {/* Clean Progress Bar inside the KPI */}
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div 
                        className="bg-amber-500 h-full transition-all duration-500" 
                        style={{width: `${(executiveMetrics.dispatched / executiveMetrics.orders) * 100}%`}}
                      ></div>
                    </div>
                    <div className="mt-2 text-[10px] text-text-muted font-medium text-right uppercase tracking-wider">
                      {executiveMetrics.dispatched} / {executiveMetrics.orders} Dispatched
                    </div>
                  </div>

                  {/* Avg Fulfillment Cost */}
                  <div className="bg-white p-6 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                    <div className="flex items-center gap-3 text-text-muted mb-4">
                      <div className="w-8 h-8 rounded-full bg-purple-50 flex items-center justify-center text-purple-600">
                        <TrendingUp className="w-4 h-4" />
                      </div>
                      <span className="text-xs font-bold uppercase tracking-wider">Fulfillment Cost / Order</span>
                    </div>
                    <div className="font-heading text-4xl font-bold text-accent">
                      ₹{executiveMetrics.avgCost.toFixed(2)}
                    </div>
                    <div className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-emerald-600">
                      <ArrowUpRight className="w-3.5 h-3.5 rotate-90" />
                      <span>-2.1% (Improved margin)</span>
                    </div>
                  </div>
                </div>

                {/* Quick Actions & Secondary Metrics */}
                <div className="flex flex-col lg:flex-row gap-6">
                  {/* Secondary Operational Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 flex-1">
                    {[
                      { label: 'Current Open Orders', val: executiveMetrics.openOrders.toLocaleString(), icon: ShoppingCart },
                      { label: 'Average Order Value (AOV)', val: `₹${executiveMetrics.aov.toFixed(2)}`, icon: Wallet },
                      { label: 'Fulfillment Lead Time', val: `${executiveMetrics.leadTime.toFixed(1)} Hrs`, icon: Clock }
                    ].map((metric, i) => (
                      <div key={i} className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)] hover:border-slate-300 transition-colors group cursor-default">
                        <div className="text-[11px] font-bold uppercase tracking-wider text-text-muted mb-2 flex items-center gap-2">
                          <metric.icon className="w-3.5 h-3.5 text-slate-400 group-hover:text-accent transition-colors" />
                          {metric.label}
                        </div>
                        <div className="font-heading text-2xl font-bold text-accent group-hover:text-blue-600 transition-colors">{metric.val}</div>
                      </div>
                    ))}
                  </div>

                  {/* Quick Action Buttons */}
                  <div className="flex flex-col sm:flex-row lg:flex-col justify-between gap-4 lg:w-64 flex-shrink-0">
                    <button className="flex-1 lg:flex-none flex items-center gap-3 bg-white border border-border p-3.5 rounded-xl shadow-sm hover:shadow-md hover:border-slate-300 text-left transition-all group">
                      <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-accent group-hover:bg-accent group-hover:text-white transition-colors">
                        <FilePlus className="w-4 h-4" />
                      </div>
                      <span className="font-semibold text-[13px] text-accent">Create New PO</span>
                    </button>
                    <button className="flex-1 lg:flex-none flex items-center gap-3 bg-white border border-border p-3.5 rounded-xl shadow-sm hover:shadow-md hover:border-slate-300 text-left transition-all group">
                      <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-accent group-hover:bg-accent group-hover:text-white transition-colors">
                        <Truck className="w-4 h-4" />
                      </div>
                      <span className="font-semibold text-[13px] text-accent">View Shipments</span>
                    </button>
                    <button className="flex-1 lg:flex-none flex items-center gap-3 bg-white border border-border p-3.5 rounded-xl shadow-sm hover:shadow-md hover:border-slate-300 text-left transition-all group">
                      <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-accent group-hover:bg-accent group-hover:text-white transition-colors">
                        <ClipboardList className="w-4 h-4" />
                      </div>
                      <span className="font-semibold text-[13px] text-accent">Inventory Report</span>
                    </button>
                  </div>
                </div>

                {/* Clean Visualization Row */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Revenue Growth Chart */}
                  <div className="col-span-1 lg:col-span-2 bg-white rounded-xl border border-border p-6 shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                    <div className="flex justify-between items-end mb-6">
                      <div>
                        <h3 className="font-heading font-bold text-accent">7-Day Revenue Trends</h3>
                        <p className="text-xs text-text-muted mt-1">Gross velocity tracking over rolling period</p>
                      </div>
                      <div className="text-xs font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded">
                        Target: ₹15L/day
                      </div>
                    </div>
                    <div className="h-[280px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={initialRevenueData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                          <defs>
                            <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#2563EB" stopOpacity={0.1}/>
                              <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" opacity={0.5} />
                          <XAxis 
                            dataKey="day" 
                            axisLine={false} 
                            tickLine={false} 
                            tick={{fontSize: 12, fill: '#64748B', fontWeight: 500}}
                            dy={10}
                          />
                          <YAxis 
                            axisLine={false} 
                            tickLine={false} 
                            tick={{fontSize: 12, fill: '#64748B', fontWeight: 500}}
                            tickFormatter={(val) => `₹${val}L`}
                            dx={-10}
                          />
                          <Tooltip 
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                            formatter={(value: any) => [`₹${value}L`, 'Revenue']}
                          />
                          <Area 
                            type="monotone" 
                            dataKey="revenue" 
                            stroke="#2563EB" 
                            strokeWidth={3}
                            fillOpacity={1} 
                            fill="url(#colorRev)" 
                            activeDot={{ r: 6, strokeWidth: 0 }}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Order Journey Timeline */}
                  <div className="col-span-1 bg-white rounded-xl border border-border p-6 shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col">
                    <div>
                      <h3 className="font-heading font-bold text-accent">Order Journey</h3>
                      <p className="text-xs text-text-muted mt-1">Live fulfillment staging overview</p>
                    </div>
                    
                    <div className="flex-1 mt-6">
                      <div className="relative space-y-0 text-sm">
                        
                        {/* Received */}
                        <div className="relative flex gap-4 pb-6 group">
                          <div className="absolute left-4 top-8 bottom-[-8px] w-[2px] bg-emerald-100"></div>
                          <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0 border border-emerald-100 z-10 transition-transform group-hover:scale-105">
                            <ShoppingCart className="w-4 h-4" />
                          </div>
                          <div className="pt-1.5 flex-1">
                            <div className="flex justify-between items-center mb-0.5">
                              <span className="font-bold text-accent text-[13px]">Order Received</span>
                              <span className="font-heading font-bold text-emerald-600">{executiveMetrics.orders}</span>
                            </div>
                            <div className="w-full h-1 bg-slate-100 rounded-full flex-1 overflow-hidden">
                              <div className="w-full h-full bg-emerald-400 rounded-full"></div>
                            </div>
                          </div>
                        </div>

                        {/* Processing */}
                        <div className="relative flex gap-4 pb-6 group">
                          <div className="absolute left-4 top-8 bottom-[-8px] w-[2px] bg-amber-100"></div>
                          <div className="w-8 h-8 rounded-full bg-amber-50 text-amber-600 flex items-center justify-center flex-shrink-0 border border-amber-100 z-10 transition-transform group-hover:scale-105">
                            <Activity className="w-4 h-4" />
                          </div>
                          <div className="pt-1.5 flex-1">
                            <div className="flex justify-between items-center mb-0.5">
                              <span className="font-bold text-accent text-[13px]">Processing & Checked</span>
                              <span className="font-heading font-bold text-amber-600">{executiveMetrics.orders - 120}</span>
                            </div>
                            <div className="w-full h-1 bg-slate-100 rounded-full flex-1 overflow-hidden">
                              <div className="w-[85%] h-full bg-amber-400 rounded-full relative">
                                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-amber-50 rounded-full animate-pulse"></div>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Shipped */}
                        <div className="relative flex gap-4 pb-6 group">
                          <div className="absolute left-4 top-8 bottom-[-8px] w-[2px] bg-slate-100"></div>
                          <div className="w-8 h-8 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0 border border-blue-100 z-10 transition-transform group-hover:scale-105">
                            <Truck className="w-4 h-4" />
                          </div>
                          <div className="pt-1.5 flex-1">
                            <div className="flex justify-between items-center mb-0.5">
                              <span className="font-bold text-accent text-[13px]">Shipped</span>
                              <span className="font-heading font-bold text-blue-600">{executiveMetrics.dispatched}</span>
                            </div>
                            <div className="w-full h-1 bg-slate-100 rounded-full flex-1 overflow-hidden">
                              <div className="w-[60%] h-full bg-blue-400 rounded-full"></div>
                            </div>
                          </div>
                        </div>

                        {/* Delivered */}
                        <div className="relative flex gap-4 group">
                          <div className="w-8 h-8 rounded-full bg-slate-50 text-slate-400 flex items-center justify-center flex-shrink-0 border border-border z-10 transition-transform group-hover:scale-105">
                            <CheckCircle2 className="w-4 h-4" />
                          </div>
                          <div className="pt-1.5 flex-1">
                            <div className="flex justify-between items-center mb-0.5">
                              <span className="font-bold text-slate-600 text-[13px]">Delivered</span>
                              <span className="font-heading font-bold text-slate-600">{executiveMetrics.dispatched - 340 > 0 ? executiveMetrics.dispatched - 340 : 0}</span>
                            </div>
                            <div className="w-full h-1 bg-slate-100 rounded-full flex-1 overflow-hidden">
                              <div className="w-[45%] h-full bg-slate-300 rounded-full"></div>
                            </div>
                          </div>
                        </div>

                      </div>
                    </div>
                  </div>
                </div>

              </div>
            )}

            {activeTab === 'operations' && (
              <>
              {/* Ops Header */}
              <div className="mb-6 pb-4 border-b border-border flex justify-between items-end animate-in fade-in">
                <div>
                  <h2 className="text-2xl font-heading font-bold text-accent tracking-tight">Operations Command Center</h2>
                  <p className="text-sm text-text-muted mt-1">Deep warehouse analytics and Six Sigma tracking</p>
                </div>
              </div>

              {/* KPI Row (Real-time Updated) */}
              <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-6">
                {kpis.map((kpi, i) => (
                  <div key={i} className={`enterprise-widget p-4 xl:p-5 bg-white border border-border rounded-xl`}>
                    <div className="text-[11px] xl:text-[12px] uppercase tracking-wide text-text-muted font-semibold">{kpi.label}</div>
                    
                    {kpi.type === 'score' ? (
                      <div className="flex flex-col gap-1 mt-2">
                        <div className="flex items-center gap-3">
                          <div className={`font-heading text-3xl xl:text-4xl font-bold !leading-none ${kpi.val >= 90 ? 'text-success' : kpi.val > 70 ? 'text-warning' : 'text-error'}`}>
                            {kpi.val}
                          </div>
                          <div className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border inline-block ${kpi.val >= 90 ? 'bg-success/10 text-success border-success/20' : kpi.val > 70 ? 'bg-warning/10 text-warning border-warning/20' : 'bg-error/10 text-error border-error/20'}`}>
                            {kpi.val >= 90 ? 'Healthy' : kpi.val > 70 ? 'Caution' : 'Critical'}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className={`font-heading text-2xl xl:text-3xl font-bold mt-2 truncate transition-colors duration-500 ${kpi.alert && alertState.status === 'open' ? 'text-error' : 'text-accent'}`}>
                        {kpi.label.includes('Value') ? `₹${kpi.val}` : kpi.label.includes('Accuracy') ? `${kpi.val}%` : kpi.val.toLocaleString()}
                      </div>
                    )}
                    
                    <div className="text-[10px] xl:text-xs flex items-center gap-1 mt-2">
                      {kpi.trend === 'up' && <span className="text-success font-medium">{kpi.trendVal}</span>}
                      {kpi.trend === 'down' && <span className="text-error font-medium">{kpi.trendVal}</span>}
                      {kpi.trend === 'neutral' && <span className="text-text-main font-medium">{kpi.trendVal}</span>}
                      <span className="text-text-muted ml-0.5 truncate">{kpi.sub}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                
                {/* Process Control Chart */}
                <div className="col-span-1 lg:col-span-3 enterprise-widget p-4 lg:p-6 flex flex-col">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="font-heading font-bold text-[1.1rem] text-accent tracking-tight">Picking Accuracy Variance (DMAIC)</h3>
                      <p className="text-[0.75rem] text-text-muted mt-1 font-medium tracking-wide uppercase">Statistical Process Control (SPC) Monitoring • Live</p>
                    </div>
                    <div className="bg-[#F1F5F9] text-accent-light px-3 py-1.5 rounded-md text-[10px] font-bold border border-border tracking-wider uppercase shadow-sm">
                      DMAIC Analyze Phase
                    </div>
                  </div>
                  
                  <div className="flex-1 min-h-[260px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={chartData} margin={{ top: 5, right: 20, left: -20, bottom: 0 }}>
                        <XAxis 
                          dataKey="day" 
                          axisLine={false} 
                          tickLine={false} 
                          tick={{fontSize: 11, fill: '#64748b', fontWeight: 500}} 
                          dy={10}
                        />
                        <YAxis 
                          domain={[97.5, 100.5]} 
                          axisLine={false} 
                          tickLine={false} 
                          tick={{fontSize: 11, fill: '#64748b', fontWeight: 500}} 
                          tickFormatter={(val) => `${val}%`}
                          dx={-10}
                        />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#1E293B', 
                            border: 'none', 
                            borderRadius: '8px',
                            color: '#fff',
                            fontSize: '12px',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                          }}
                          itemStyle={{ color: '#E2E8F0', fontWeight: 600 }}
                          labelStyle={{ color: '#94A3B8', marginBottom: '6px', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}
                          formatter={(value: any, name: string) => [
                            name === 'Accuracy' ? `${Number(value).toFixed(2)}%` : value, 
                            name
                          ]}
                        />
                        <ReferenceLine y={UCL} stroke="#EF4444" strokeDasharray="4 4" strokeWidth={1} opacity={0.5} label={{ position: 'insideTopRight', value: 'UCL (99.9%)', fill: '#EF4444', fontSize: '10px' }} />
                        <ReferenceLine y={TARGET} stroke="#10B981" strokeWidth={1} opacity={0.4} label={{ position: 'insideTopRight', value: 'Target (99.6%)', fill: '#10B981', fontSize: '10px' }} />
                        <ReferenceLine y={LCL} stroke="#EF4444" strokeDasharray="4 4" strokeWidth={1} opacity={0.5} label={{ position: 'insideBottomRight', value: 'LCL (98.8%)', fill: '#EF4444', fontSize: '10px' }} />
                        
                        <Line 
                          type="monotone" 
                          dataKey="rate" 
                          stroke="#0F172A" 
                          strokeWidth={2}
                          dot={{ r: 4, strokeWidth: 2, fill: '#fff', stroke: '#0F172A' }}
                          activeDot={{ r: 6, fill: '#0F172A', stroke: '#fff', strokeWidth: 2 }}
                          name="Accuracy"
                          isAnimationActive={false} // Disable to avoid glitching during live polling
                        />
                        {/* Interactive Brush for Zoom/Pan */}
                        <Brush dataKey="day" height={24} stroke="#CBD5E1" fill="#F8FAFC" tickFormatter={() => ''} />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Multi-Step Action Alert Widget */}
                <div className="col-span-4 lg:col-span-1 enterprise-widget flex flex-col overflow-hidden relative">
                  <div className="p-5 border-b border-border bg-[#F8FAFC]">
                    <div className="font-heading font-bold text-[0.8rem] text-accent uppercase tracking-widest">Process Compliance</div>
                  </div>
                  
                  <div className="p-5 flex-1 flex flex-col bg-white">
                    {alertState.status === 'open' ? (
                      <div className="flex-1 flex flex-col">
                        {/* Wizard Progress Indication */}
                        <div className="flex gap-2 mb-5">
                          <div className={`h-1.5 flex-1 rounded-full transition-colors ${alertState.step >= 1 ? 'bg-error' : 'bg-slate-200'}`} />
                          <div className={`h-1.5 flex-1 rounded-full transition-colors ${alertState.step >= 2 ? 'bg-error' : 'bg-slate-200'}`} />
                          <div className={`h-1.5 flex-1 rounded-full transition-colors ${alertState.step >= 3 ? 'bg-error' : 'bg-slate-200'}`} />
                        </div>
                        
                        {/* Step 1: Root Cause */}
                        {alertState.step === 1 && (
                          <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                             <div className="flex items-center gap-2 text-error font-semibold text-xs mb-3 uppercase tracking-wide">
                              <AlertOctagon className="w-4 h-4"/> Step 1: Root Cause
                             </div>
                             <p className="text-xs text-text-muted mb-4 leading-relaxed">
                              Picking accuracy breached LCL (98.8%). Identify the structural cause before initiating Corrective and Preventive Actions (CAPA).
                             </p>
                             <select 
                              value={alertState.rootCause}
                              onChange={(e) => setAlertState({...alertState, rootCause: e.target.value})}
                              className="w-full p-2.5 text-xs font-medium border border-border rounded shadow-sm bg-white text-text-main focus:outline-none focus:ring-1 focus:ring-accent mb-4"
                             >
                              <option value="" disabled>Select Root Cause...</option>
                              <option value="WMS Master Data Desync">WMS Master Data Desync</option>
                              <option value="Operator Training Deficit">Operator Training Deficit</option>
                              <option value="Vendor Barcode Damage">Vendor Barcode Damage</option>
                              <option value="RF Scanner Latency">RF Scanner Latency</option>
                             </select>
                             <button 
                              onClick={handleAlertNextStep}
                              disabled={!alertState.rootCause}
                              className={`w-full py-2.5 rounded text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                                !alertState.rootCause ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-accent text-white hover:bg-slate-800 shadow-md'
                              }`}
                             >
                               Next Phase <ArrowRight className="w-3 h-3"/>
                             </button>
                          </div>
                        )}

                        {/* Step 2: Corrective Action */}
                        {alertState.step === 2 && (
                          <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                             <div className="flex items-center gap-2 text-warning font-semibold text-xs mb-3 uppercase tracking-wide">
                              <ShieldCheck className="w-4 h-4"/> Step 2: CAPA Strategy
                             </div>
                             <p className="text-[11px] bg-slate-50 p-2 rounded border border-border text-text-muted mb-4">
                               <span className="font-semibold text-slate-700">Identified Cause:</span> {alertState.rootCause}
                             </p>
                             <select 
                              value={alertState.correctiveAction}
                              onChange={(e) => setAlertState({...alertState, correctiveAction: e.target.value})}
                              className="w-full p-2.5 text-xs font-medium border border-border rounded shadow-sm bg-white text-text-main focus:outline-none focus:ring-1 focus:ring-accent mb-4"
                             >
                              <option value="" disabled>Select Corrective Action...</option>
                              <option value="Force Hardware Sync & Audit">Force Hardware Sync & Audit</option>
                              <option value="Re-assign to Tier 2 Picker">Re-assign to Tier 2 Picker</option>
                              <option value="Flag Vendor for QA Block">Flag Vendor for QA Block</option>
                              <option value="Restart Gateway Routers">Restart Gateway Routers</option>
                             </select>
                             <button 
                              onClick={handleAlertNextStep}
                              disabled={!alertState.correctiveAction}
                              className={`w-full py-2.5 rounded text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                                !alertState.correctiveAction ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-accent text-white hover:bg-slate-800 shadow-md'
                              }`}
                             >
                               Define Strategy <ArrowRight className="w-3 h-3"/>
                             </button>
                          </div>
                        )}

                        {/* Step 3: Confirmation */}
                        {alertState.step === 3 && (
                          <div className="animate-in fade-in slide-in-from-right-4 duration-300 flex-col flex h-full justify-between">
                             <div>
                               <div className="flex items-center gap-2 text-success font-semibold text-xs mb-3 uppercase tracking-wide">
                                <CheckCircle className="w-4 h-4"/> Step 3: Authorization
                               </div>
                               <div className="text-[11px] border border-border rounded bg-slate-50 overflow-hidden mb-4">
                                 <div className="bg-slate-100 px-3 py-1.5 border-b border-border font-semibold text-text-main">Final Summary</div>
                                 <div className="p-3 space-y-2">
                                   <div><span className="text-text-muted block text-[9px] uppercase tracking-wider">Breach Target</span><span className="font-medium text-error">Picking Accuracy (98.5%)</span></div>
                                   <div><span className="text-text-muted block text-[9px] uppercase tracking-wider">Root Cause</span><span className="font-medium text-slate-700">{alertState.rootCause}</span></div>
                                   <div><span className="text-text-muted block text-[9px] uppercase tracking-wider">Corrective Action</span><span className="font-medium text-slate-700">{alertState.correctiveAction}</span></div>
                                 </div>
                               </div>
                             </div>
                             <button 
                              onClick={handleAlertNextStep}
                              className="w-full py-2.5 rounded text-xs font-bold flex items-center justify-center gap-2 transition-all bg-emerald-600 text-white hover:bg-emerald-700 shadow-md"
                             >
                               Authorize & Commit to Audit
                             </button>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in zoom-in duration-500 py-6">
                        <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-500 flex items-center justify-center mb-4">
                          <CheckCircle2 className="w-6 h-6" />
                        </div>
                        <h4 className="font-heading font-bold text-accent text-sm mb-1">Process In Control</h4>
                        <p className="text-xs text-text-muted max-w-[200px]">All Six Sigma parameters are currently within tolerance bounds.</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Data Table */}
                <div className="col-span-1 lg:col-span-4 enterprise-widget overflow-hidden flex flex-col h-full mt-6">
                  <div className="p-4 lg:p-5 border-b border-border bg-white flex items-center justify-between">
                     <div>
                       <h3 className="font-heading font-bold text-[0.9rem] text-accent">Active Variances & Audits</h3>
                       <p className="text-[0.7rem] text-text-muted mt-0.5">Real-time discrepancy log across Bin Zones</p>
                     </div>
                     <div className="p-1.5 bg-slate-50 hover:bg-slate-100 rounded border border-border text-text-muted cursor-pointer transition-colors">
                       <Filter className="w-3.5 h-3.5" />
                     </div>
                  </div>
                  <table className="w-full text-left text-sm border-collapse">
                    <thead className="bg-[#F8FAFC]">
                      <tr>
                        <th className="px-6 py-3.5 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none">SKU / Bin</th>
                        <th className="px-6 py-3.5 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none">Sys Count</th>
                        <th className="px-6 py-3.5 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none">Actual Count</th>
                        <th className="px-6 py-3.5 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none text-right">Operational Status</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white">
                      {tableData.map((item, i) => (
                        <tr key={i} className="hover:bg-slate-50/50 transition-colors">
                          <td className="px-6 py-3.5 border-b border-border border-dashed text-[0.8rem] text-text-main">
                            <div className="font-semibold text-accent">{item.sku}</div>
                            <div className="text-[10px] text-text-muted font-mono mt-0.5 tracking-wider">{item.bin}</div>
                          </td>
                          <td className="px-6 py-3.5 border-b border-border border-dashed text-[0.85rem] font-mono text-slate-600">
                            {item.sys}
                          </td>
                          <td className="px-6 py-3.5 border-b border-border border-dashed text-[0.85rem] font-mono">
                            <span className={`${item.sys !== item.act ? 'text-error font-bold font-sans px-1.5 py-0.5 bg-error/10 rounded' : 'text-slate-600'}`}>
                              {item.act}
                            </span>
                          </td>
                          <td className="px-6 py-3.5 border-b border-border border-dashed text-right">
                            {item.status === 'Clear' ? (
                              <span className="inline-block px-2.5 py-1 rounded bg-[#DCFCE7] text-[#166534] text-[10px] font-bold uppercase tracking-widest shadow-sm border border-[#166534]/10">
                                OPTIMAL
                              </span>
                            ) : item.status === 'Critical' ? (
                              <span className="inline-block px-2.5 py-1 rounded bg-[#FEF2F2] text-[#991B1B] text-[10px] font-bold uppercase tracking-widest shadow-sm border border-[#991B1B]/10">
                                DEVIATION
                              </span>
                            ) : (
                              <span className="inline-block px-2.5 py-1 rounded bg-[#FFFBEB] text-[#B45309] text-[10px] font-bold uppercase tracking-widest shadow-sm border border-[#B45309]/10">
                                LOW STOCK
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

              </div>
              </>
            )}

            {activeTab === 'dispatch' && (
               <div className="space-y-6 animate-in fade-in duration-500">
                 <div className="flex items-end justify-between mb-4 border-b border-border pb-4">
                   <div>
                     <h2 className="text-2xl font-heading font-bold text-accent tracking-tight">Active Dispatch Control</h2>
                     <p className="text-sm text-text-muted mt-1">Live tracking of outgoing carrier fleets</p>
                   </div>
                 </div>

                 <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                   <div className="bg-white p-5 rounded-xl border border-border">
                     <div className="text-[12px] uppercase tracking-wide text-text-muted font-semibold mb-2">Ready for Packing</div>
                     <div className="font-heading text-3xl font-bold text-accent">{pickingEngine.packQueue.filter(q => q.status === 'Awaiting Pack').length}</div>
                     <div className="text-xs text-amber-600 mt-2 flex items-center gap-1 font-medium">
                       <Clock className="w-3.5 h-3.5" />
                       Handoffs pending boxing
                     </div>
                   </div>
                   <div className="bg-white p-5 rounded-xl border border-border">
                     <div className="text-[12px] uppercase tracking-wide text-text-muted font-semibold mb-2">Packed & Ready to Ship</div>
                     <div className="font-heading text-3xl font-bold text-blue-600">{pickingEngine.packQueue.filter(q => q.status === 'Packed & Ready').length + (executiveMetrics.orders - executiveMetrics.dispatched > 0 ? executiveMetrics.orders - executiveMetrics.dispatched : 0)}</div>
                     <div className="text-xs text-blue-600 mt-2 flex items-center gap-1 font-medium">
                       <Package className="w-3.5 h-3.5" />
                       Awaiting carriers in docking area
                     </div>
                   </div>
                   <div className="bg-white p-5 rounded-xl border border-border">
                     <div className="text-[12px] uppercase tracking-wide text-text-muted font-semibold mb-2">SLA Compliance</div>
                     <div className="font-heading text-3xl font-bold text-emerald-600">98.4%</div>
                     <div className="text-xs text-text-muted mt-2">
                       Within 24hr delivery target
                     </div>
                   </div>
                 </div>

                 {/* Packaging Scanner Block */}
                 <div className="bg-white p-5 border border-border rounded-xl shadow-[0_2px_10px_rgba(0,0,0,0.02)] mb-6 flex flex-col md:flex-row gap-6">
                   <div className="flex-1">
                     <h3 className="text-lg font-heading font-bold text-accent flex items-center gap-2 mb-2">
                       <Package className="w-5 h-5 text-accent" /> Scan Out Packaging Label
                     </h3>
                     <p className="text-sm text-text-muted mb-4">Validate packed orders and queue them for final dispatch scanning.</p>
                     
                     <form onSubmit={handlePackScan} className="flex gap-3">
                       <div className="relative flex-1">
                         <ScanLine className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                         <input
                           type="text"
                           value={packScanInput}
                           onChange={e => setPackScanInput(e.target.value)}
                           className="w-full pl-9 pr-3 py-2 border border-border rounded-md bg-slate-50 font-mono text-sm focus:border-blue-500 outline-none"
                           placeholder="Scan ORD-XXXX..."
                         />
                       </div>
                       <button type="submit" disabled={!packScanInput} className="bg-accent text-white px-5 py-2 font-bold text-sm rounded-md disabled:opacity-50 hover:bg-accent-light transition-colors">
                         Scan Packed
                       </button>
                     </form>
                   </div>

                   <div className="flex-1 bg-slate-50 rounded-lg p-4 h-40 overflow-y-auto border border-border">
                     <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Awaiting Pack Validation Queue</div>
                     {pickingEngine.packQueue.filter(q => q.status === 'Awaiting Pack').length === 0 ? (
                       <div className="text-xs text-slate-400 py-4 text-center">No orders currently awaiting packing. Pickers must handoff batches first.</div>
                     ) : (
                       <div className="space-y-2">
                         {pickingEngine.packQueue.filter(q => q.status === 'Awaiting Pack').map((q, i) => (
                           <div key={i} className="flex items-center justify-between text-sm bg-white p-2 rounded border border-border shadow-sm">
                             <span className="font-mono font-bold text-accent">{q.orderId}</span>
                             <span className="text-[10px] font-bold bg-amber-100 text-amber-700 px-2 py-0.5 rounded">AWAITING PACK</span>
                           </div>
                         ))}
                       </div>
                     )}
                   </div>
                 </div>

                 <div className="enterprise-widget p-0 border border-border rounded-xl bg-white overflow-hidden">
                   <table className="w-full text-left text-sm border-collapse">
                     <thead className="bg-[#F8FAFC] border-b border-border">
                       <tr>
                         <th className="px-6 py-4 text-[11px] font-bold text-text-muted uppercase tracking-widest leading-none">Carrier</th>
                         <th className="px-6 py-4 text-[11px] font-bold text-text-muted uppercase tracking-widest leading-none">Destination Node</th>
                         <th className="px-6 py-4 text-[11px] font-bold text-text-muted uppercase tracking-widest leading-none">Pallets</th>
                         <th className="px-6 py-4 text-[11px] font-bold text-text-muted uppercase tracking-widest leading-none text-right">Status</th>
                       </tr>
                     </thead>
                     <tbody className="divide-y divide-border">
                       {[
                         { carrier: 'BlueDart Air', dest: 'DEL-HUB-01', pallets: 14, status: 'In Transit' },
                         { carrier: 'Delhivery Surface', dest: 'BOM-HUB-04', pallets: 32, status: 'Departed' },
                         { carrier: 'Amazon ATS', dest: 'BLR-HUB-02', pallets: 8, status: 'Loading Dock A' },
                         { carrier: 'Ecom Express', dest: 'CCU-HUB-01', pallets: 12, status: 'Arriving' }
                       ].map((c, i) => (
                         <tr key={i} className="hover:bg-slate-50 transition-colors">
                           <td className="px-6 py-4 font-semibold text-accent">{c.carrier}</td>
                           <td className="px-6 py-4 text-slate-600 font-mono text-xs">{c.dest}</td>
                           <td className="px-6 py-4 text-slate-600">{c.pallets} Pallets</td>
                           <td className="px-6 py-4 text-right">
                             <span className={`inline-block px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-widest shadow-sm border ${
                               c.status.includes('Transit') || c.status.includes('Departed') ? 'bg-[#DCFCE7] text-[#166534] border-[#166534]/10' : 
                               'bg-[#FEF2F2] text-[#991B1B] border-[#991B1B]/10'
                             }`}>
                               {c.status}
                             </span>
                           </td>
                         </tr>
                       ))}
                     </tbody>
                   </table>
                 </div>
               </div>
            )}

            {activeTab === 'mismatch' && (
               <div className="space-y-6 animate-in fade-in duration-500">
                 <div className="flex items-end justify-between mb-4 border-b border-border pb-4">
                   <div>
                     <h2 className="text-2xl font-heading font-bold text-accent tracking-tight">Inventory Reconciliation</h2>
                     <p className="text-sm text-text-muted mt-1">Six Sigma deviation tracking and root cause analysis</p>
                   </div>
                 </div>
                 
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                   <div className="bg-white p-6 rounded-xl border border-border">
                     <div className="flex items-center gap-3 mb-2">
                       <AlertOctagon className="w-5 h-5 text-error" />
                       <h3 className="font-heading font-bold text-accent">Critical Variances</h3>
                     </div>
                     <p className="text-sm text-text-muted mb-4">You have 3 active SKUs showing a variance exceeding LCL thresholds. Immediate cycle count required.</p>
                     <button className="text-xs font-bold text-error border border-error/30 bg-error/5 hover:bg-error/10 px-4 py-2 rounded transition-colors">
                       Initiate Cycle Count
                     </button>
                   </div>
                   <div className="bg-white p-6 rounded-xl border border-border">
                     <div className="flex items-center gap-3 mb-2">
                       <CheckCircle className="w-5 h-5 text-success" />
                       <h3 className="font-heading font-bold text-accent">Inventory Accuracy</h3>
                     </div>
                     <div className="flex items-end gap-2 mb-2">
                       <span className="font-heading text-4xl font-bold text-accent">99.8%</span>
                       <span className="text-sm text-success font-medium mb-1">+0.1% vs last week</span>
                     </div>
                     <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                       <div className="bg-emerald-500 h-full w-[99.8%]"></div>
                     </div>
                   </div>
                 </div>

                 {/* Re-use tableData array from ops tab for demonstration */}
                 <div className="enterprise-widget p-0 border border-border rounded-xl bg-white overflow-hidden">
                   <table className="w-full text-left text-sm border-collapse">
                     <thead className="bg-[#F8FAFC]">
                       <tr>
                         <th className="px-6 py-4 text-[11px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none">SKU / Bin</th>
                         <th className="px-6 py-4 text-[11px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none">System Record</th>
                         <th className="px-6 py-4 text-[11px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none">Actual Scan</th>
                         <th className="px-6 py-4 text-[11px] font-bold text-text-muted border-b border-border uppercase tracking-widest leading-none text-right">Variance Impact</th>
                       </tr>
                     </thead>
                     <tbody className="divide-y divide-border">
                       {tableData.map((item, i) => (
                         <tr key={i} className="hover:bg-slate-50 transition-colors">
                           <td className="px-6 py-4">
                             <div className="font-semibold text-accent">{item.sku}</div>
                             <div className="text-[10px] text-text-muted font-mono mt-0.5 tracking-wider">{item.bin}</div>
                           </td>
                           <td className="px-6 py-4 font-mono text-slate-600">{item.sys} Units</td>
                           <td className="px-6 py-4 font-mono font-bold text-accent">{item.act} Units</td>
                           <td className="px-6 py-4 text-right">
                             {item.sys === item.act ? (
                               <span className="text-slate-400 text-xs">No Variance</span>
                             ) : (
                               <span className="text-error font-bold text-sm">
                                  {item.act - item.sys > 0 ? '+' : ''}{(item.act - item.sys)} Units
                               </span>
                             )}
                           </td>
                         </tr>
                       ))}
                     </tbody>
                   </table>
                 </div>
               </div>
            )}

            {activeTab === 'grn' && (
              <div className="space-y-6 animate-in fade-in duration-500">
                <div className="flex items-end justify-between mb-4 border-b border-border pb-4">
                  <div>
                    <h2 className="text-2xl font-heading font-bold text-accent tracking-tight flex items-center gap-2">
                      Goods Inward (GRN)
                      <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ml-2">2-Step Verification</span>
                    </h2>
                    <p className="text-sm text-text-muted mt-1">Barcode scanning and system-directed putaway sequence</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Scanner Tool */}
                  <div className="bg-white p-6 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col h-full">
                    <div className="flex items-center gap-2 mb-6">
                      <Barcode className="w-5 h-5 text-accent" />
                      <h3 className="font-heading font-bold text-accent">Item-Level Putaway Scanner</h3>
                    </div>
                    
                    <form onSubmit={handleBarcodeSubmit} className="flex flex-col sm:flex-row gap-3 mb-6">
                      <div className="relative flex-1 flex gap-2">
                        <div className="relative flex-1">
                          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <ScanLine className="h-4 w-4 text-slate-400" />
                          </div>
                          <input
                            type="text"
                            value={grnScanState.barcode}
                            onChange={(e) => setGrnScanState({...grnScanState, barcode: e.target.value})}
                            placeholder="Scan or enter SKU barcode..."
                            className="block w-full pl-10 pr-3 py-3 border border-border rounded-lg leading-5 bg-slate-50 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 sm:text-sm font-mono transition-colors"
                            disabled={grnScanState.validating || grnScanState.scanned || grnScanState.cameraActive}
                          />
                        </div>
                        <button
                          type="button"
                          onClick={simulateCameraScan}
                          disabled={grnScanState.validating || grnScanState.scanned || grnScanState.cameraActive}
                          className="bg-slate-100 text-slate-600 border border-border px-4 py-3 rounded-lg hover:bg-slate-200 transition-colors disabled:opacity-50"
                          title="Scan via Device Camera"
                        >
                          <Camera className="w-5 h-5" />
                        </button>
                      </div>
                      <button 
                        type="submit"
                        disabled={!grnScanState.barcode || grnScanState.validating || grnScanState.scanned}
                        className="bg-accent text-white px-8 py-3 rounded-lg font-bold text-sm hover:bg-accent-light disabled:opacity-50 transition-colors shadow-sm"
                      >
                        {grnScanState.validating ? 'Validating...' : 'Scan'}
                      </button>
                    </form>

                    {grnScanState.cameraActive && (
                      <div className="flex-1 flex flex-col items-center justify-center p-4 border border-blue-200 bg-blue-50 rounded-lg animate-in fade-in relative overflow-hidden">
                        <div className="absolute inset-0 bg-[linear-gradient(transparent_0%,rgba(59,130,246,0.1)_50%,transparent_100%)] bg-[length:100%_4px] animate-[scan_2s_linear_infinite]"></div>
                        <Smartphone className="w-12 h-12 text-blue-500 mb-4 animate-pulse" />
                        <div className="text-sm font-bold text-blue-800">Camera Feed Active</div>
                        <div className="text-xs text-blue-600 mt-1">Focusing on barcode...</div>
                        <button onClick={() => setGrnScanState(prev => ({...prev, cameraActive: false}))} className="mt-4 text-xs font-semibold text-slate-500 hover:text-slate-700 underline">Cancel</button>
                      </div>
                    )}

                    {grnScanState.validating && (
                       <div className="flex-1 flex flex-col items-center justify-center py-12 text-center text-text-muted">
                         <div className="w-8 h-8 rounded-full border-2 border-accent border-t-transparent animate-spin mb-4"></div>
                         <div className="text-sm">Running validation against ASN & PO...</div>
                       </div>
                    )}

                    {grnScanState.scanned && !grnScanState.validating && (
                      <div className="flex-1 border border-border rounded-lg p-5 bg-slate-50 relative overflow-hidden animate-in zoom-in-95 duration-200">
                        <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mb-1">Scanned Entity</div>
                            <div className="font-mono text-lg font-bold text-accent">{grnScanState.barcode.toUpperCase()}</div>
                          </div>
                          <span className="bg-emerald-100 text-emerald-700 border border-emerald-200 text-[10px] font-bold px-2 py-0.5 rounded flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" /> VERIFIED
                          </span>
                        </div>
                        
                        <div className="mb-4">
                          <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mb-2">System Directed Putaway</div>
                          {grnScanState.suggestions.map((s, idx) => (
                            <div key={idx} className={`p-3 rounded border mb-2 flex justify-between items-center ${idx === 0 ? 'bg-white border-blue-200 shadow-sm' : 'bg-transparent border-transparent opacity-60'}`}>
                              <div>
                                <div className="font-bold text-accent text-sm flex items-center gap-2">
                                  {s.bin}
                                  {idx === 0 && <span className="bg-blue-100 text-blue-700 text-[9px] px-1.5 py-0.5 rounded leading-none">PRIMARY</span>}
                                </div>
                                <div className="text-[11px] text-text-muted mt-1">{s.reason}</div>
                              </div>
                              <div className="text-right">
                                <div className="text-[10px] text-slate-400 font-bold uppercase">Confidence</div>
                                <div className="text-sm font-bold text-blue-600">{s.score}%</div>
                              </div>
                            </div>
                          ))}
                        </div>

                        <div className="flex gap-2 w-full mt-4">
                          <button onClick={resetScan} className="flex-1 bg-white border border-border text-text-main py-2.5 rounded font-bold text-xs hover:bg-slate-50 transition-colors">
                            Cancel
                          </button>
                          <button onClick={resetScan} className="flex-[2] bg-emerald-600 text-white py-2.5 rounded font-bold text-xs hover:bg-emerald-700 transition-colors shadow-sm">
                            Confirm Placement in BIN-C4-12
                          </button>
                        </div>
                      </div>
                    )}
                    
                    {!grnScanState.scanned && !grnScanState.validating && !grnScanState.cameraActive && (
                      <div className="flex-1 flex flex-col items-center justify-center text-center px-4 py-8 text-slate-400">
                        <Boxes className="w-12 h-12 mb-3 opacity-20" />
                        <p className="text-sm">Scan a barcode to trigger Six Sigma 2-step verification and receive AI bin placement suggestions.</p>
                      </div>
                    )}
                  </div>

                  {/* Bulk Dock Receiving */}
                  <div className="bg-white p-6 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col h-full">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <Building2 className="w-5 h-5 text-accent" />
                        <h3 className="font-heading font-bold text-accent">Active Dock Receiving (Bulk)</h3>
                      </div>
                      <span className="text-[10px] text-slate-500 font-medium">Auto-refreshes</span>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-sm border-collapse">
                        <thead className="bg-[#F8FAFC]">
                          <tr>
                            <th className="px-4 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest">Vendor / PO</th>
                            <th className="px-4 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest">Expected</th>
                            <th className="px-4 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest text-right">Dock Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                          {[
                            { vendor: 'Acme Corp', po: 'PO-84191', qty: '12 Pallets', status: 'Unloading', color: 'text-blue-600 bg-blue-50 border-blue-200' },
                            { vendor: 'Global Supply', po: 'PO-84192', qty: '8 Pallets', status: 'QC Hold', color: 'text-amber-600 bg-amber-50 border-amber-200' },
                            { vendor: 'Techtronics', po: 'PO-84188', qty: '4 Pallets', status: 'Waiting', color: 'text-slate-600 bg-slate-50 border-border' },
                            { vendor: 'Apex Indust.', po: 'PO-84185', qty: '14 Pallets', status: 'Cleared', color: 'text-emerald-700 bg-emerald-50 border-emerald-200' },
                          ].map((row, i) => (
                            <tr key={i} className="hover:bg-slate-50/50">
                              <td className="px-4 py-3">
                                <div className="font-semibold text-accent text-xs">{row.vendor}</div>
                                <div className="font-mono text-[10px] text-slate-500 mt-0.5">{row.po}</div>
                              </td>
                              <td className="px-4 py-3 text-xs text-slate-600 font-medium">{row.qty}</td>
                              <td className="px-4 py-3 text-right">
                                <span className={`inline-block px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded border ${row.color}`}>
                                  {row.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'bin' && (
              <div className="space-y-6 animate-in fade-in duration-500">
                <div className="flex items-end justify-between mb-4 border-b border-border pb-4">
                  <div>
                    <h2 className="text-2xl font-heading font-bold text-accent tracking-tight flex items-center gap-2">
                      Bin Management & Optimization
                      <span className="bg-indigo-100 text-indigo-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ml-2">Smart Routing</span>
                    </h2>
                    <p className="text-sm text-text-muted mt-1">Location tracking, put-away logic, and auto-replenishment</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  {/* KPIs */}
                  <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Storage Utilization</div>
                     <div className="font-heading text-3xl font-bold text-accent">89.4%</div>
                     <div className="w-full bg-slate-100 h-1.5 rounded-full mt-3 overflow-hidden">
                       <div className="bg-blue-600 h-full w-[89.4%]"></div>
                     </div>
                  </div>
                  <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Active Pick Bins</div>
                     <div className="font-heading text-3xl font-bold text-accent">14,204</div>
                     <div className="text-[10px] text-text-muted mt-2 font-medium">Out of 16,000 total capacity</div>
                  </div>
                  <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Pending Replenishments</div>
                     <div className="font-heading text-3xl font-bold text-amber-600">24</div>
                     <div className="text-[10px] text-amber-600 mt-2 font-bold uppercase flex items-center gap-1">
                       <Clock className="w-3 h-3" /> Action Required
                     </div>
                  </div>
                  <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Optimization Score</div>
                     <div className="font-heading text-3xl font-bold text-emerald-600">96.2</div>
                     <div className="text-[10px] text-emerald-600 mt-2 font-bold uppercase flex items-center gap-1">
                       <TrendingUp className="w-3 h-3" /> Velocity matched
                     </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Bin Database Table */}
                  <div className="col-span-1 lg:col-span-2 bg-white rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col h-full overflow-hidden">
                    <div className="p-4 lg:p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex items-center gap-2">
                        <Package className="w-5 h-5 text-accent" />
                        <h3 className="font-heading font-bold text-accent">Live Bin Tracking & Utilization</h3>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="relative">
                           <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                           <input type="text" placeholder="Search bin or barcode..." className="pl-8 pr-3 py-1.5 text-xs border border-border rounded-md bg-slate-50 focus:outline-none focus:border-accent w-full sm:w-48" />
                        </div>
                        <button className="p-1.5 border border-border rounded-md text-text-muted hover:bg-slate-50 flex-shrink-0">
                          <Filter className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                    <div className="overflow-x-auto flex-1">
                       <table className="w-full text-left text-sm border-collapse min-w-[600px]">
                         <thead className="bg-[#F8FAFC]">
                           <tr>
                             <th className="px-5 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest">Bin Index (Barcode)</th>
                             <th className="px-5 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest">Zone Type</th>
                             <th className="px-5 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest">Assigned SKU</th>
                             <th className="px-5 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest">Capacity</th>
                             <th className="px-5 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest text-right">Actions</th>
                           </tr>
                         </thead>
                         <tbody className="divide-y divide-border">
                           {bins.map((b, i) => (
                             <tr key={i} className="hover:bg-slate-50 transition-colors">
                               <td className="px-5 py-3">
                                 <div className="font-mono text-sm font-bold text-accent flex items-center gap-2">
                                   <Barcode className="w-3 h-3 text-slate-400" /> {b.id}
                                 </div>
                                 <div className="text-[10px] text-slate-500 mt-0.5 font-medium">{b.vol}</div>
                               </td>
                               <td className="px-5 py-3">
                                 <span className="text-[11px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">{b.type}</span>
                               </td>
                               <td className="px-5 py-3 text-[13px] font-mono font-semibold text-accent">{b.sku}</td>
                               <td className="px-5 py-3">
                                 <div className="flex items-center justify-between text-xs mb-1">
                                   <span className={`font-bold ${b.pct < 20 ? 'text-error' : b.pct > 90 ? 'text-blue-600' : 'text-emerald-600'}`}>{b.pct}%</span>
                                 </div>
                                 <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                    <div className={`h-full transition-all duration-500 ease-out ${b.pct < 20 ? 'bg-error' : b.pct > 90 ? 'bg-blue-600' : 'bg-emerald-500'}`} style={{ width: `${b.pct}%` }}></div>
                                 </div>
                               </td>
                               <td className="px-5 py-3 text-right">
                                 <button 
                                   onClick={() => setBinTransferModal({ isOpen: true, sourceBin: b.id, destBin: '', qty: '' })}
                                   className="text-[10px] font-bold text-blue-600 bg-blue-50 border border-blue-200 px-2.5 py-1 rounded hover:bg-blue-100 transition-colors"
                                 >
                                   Audit / Transfer
                                 </button>
                               </td>
                             </tr>
                           ))}
                         </tbody>
                       </table>
                    </div>
                  </div>

                  {/* Replenishment Tasks */}
                  <div className="col-span-1 bg-white rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col h-full overflow-hidden">
                    <div className="p-4 lg:p-5 border-b border-border bg-slate-50/50">
                      <div className="flex items-center gap-2 mb-1">
                        <ArrowRight className="w-4 h-4 text-accent" />
                        <h3 className="font-heading font-bold text-accent text-sm">Auto-Replenishment Workflow</h3>
                      </div>
                      <p className="text-[10px] text-text-muted">System-triggered bulk-to-pick transfers</p>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                      {replenishmentTasks.map((t, i) => (
                        <div key={i} className="border border-border rounded-lg p-3 hover:border-blue-300 transition-colors cursor-pointer bg-white group shadow-sm">
                          <div className="flex justify-between items-start mb-2">
                             <span className={`text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${t.priority === 'Critical' ? 'bg-error/10 text-error' : t.priority === 'High' ? 'bg-warning/10 text-warning' : 'bg-blue-100 text-blue-700'}`}>
                               {t.priority} Priority
                             </span>
                             <span className="text-[10px] font-mono font-bold text-accent bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">{t.qty} Units</span>
                          </div>
                          <div className="text-[13px] font-bold text-accent mb-2">{t.sku}</div>
                          <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono bg-slate-50 p-1.5 rounded border border-border mt-2">
                            <span className="truncate">{t.from}</span>
                            <ArrowRight className="w-3 h-3 flex-shrink-0 text-blue-500" />
                            <span className="truncate font-semibold text-accent">{t.to}</span>
                          </div>
                          <button 
                            onClick={(e) => {
                              e.stopPropagation();
                              setReplenishmentTasks(prev => prev.filter((_, idx) => idx !== i));
                              setBins(prev => prev.map(b => b.id === t.to.replace(' (Pick)', '') ? { ...b, pct: 100 } : b));
                            }}
                            className="w-full mt-3 py-1.5 text-[10px] font-bold text-text-main border border-border rounded shadow-sm opacity-0 group-hover:opacity-100 transition-opacity hover:bg-slate-50"
                          >
                            Execute Drop
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>

                </div>

                {/* Physical Warehouse Heatmap representation */}
                <div className="bg-white rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col overflow-hidden mb-6">
                  <div className="p-4 lg:p-5 border-b border-border flex items-center justify-between bg-slate-50/50">
                    <div className="flex items-center gap-2">
                      <Map className="w-5 h-5 text-accent" />
                      <h3 className="font-heading font-bold text-accent">Zone Layout & Heatmap</h3>
                    </div>
                    <div className="flex items-center gap-4 text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                      <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-emerald-500"></div> Optimal</div>
                      <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-blue-600"></div> Full</div>
                      <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-error"></div> Depleted</div>
                    </div>
                  </div>
                  <div className="p-6 warehouse-grid-bg relative h-[250px] overflow-hidden">
                    <div className="absolute inset-4 grid grid-cols-5 md:grid-cols-10 gap-2">
                      {/* Simulating 50 bin blocks in a logical layout */}
                      {Array.from({ length: 50 }).map((_, i) => {
                        let bg = 'bg-slate-200 border-slate-300';
                        if (i === 4 || i === 12 || i === 25) bg = 'bg-error border-red-300 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.4)]';
                        else if (i === 7 || i === 22 || i === 38 || i === 41) bg = 'bg-blue-600 border-blue-400 shadow-[0_0_8px_rgba(37,99,235,0.3)]';
                        else if (i % 3 === 0 || i % 7 === 0) bg = 'bg-emerald-400 border-emerald-500 shadow-sm';
                        
                        return (
                          <div 
                            key={i} 
                            className={`rounded border ${bg} transition-colors duration-500 cursor-pointer hover:scale-110 flex items-center justify-center`}
                            title={`Rack Location R-${Math.floor(i/10)}-${i%10}`}
                          >
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Transfer Modal */}
            {binTransferModal.isOpen && (
              <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in">
                <div className="bg-white rounded-xl shadow-2xl border border-border w-full max-w-md overflow-hidden animate-in zoom-in-95">
                  <div className="flex justify-between items-center p-4 border-b border-border bg-slate-50">
                    <h3 className="font-heading font-bold text-accent flex items-center gap-2">
                      <ArrowRightLeft className="w-4 h-4" /> Issue Transfer Task
                    </h3>
                    <button onClick={() => setBinTransferModal(prev => ({...prev, isOpen: false}))} className="text-slate-400 hover:text-slate-600">
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <form onSubmit={handleExecuteTransfer} className="p-5 space-y-4">
                    <div>
                      <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Source Location (From)</label>
                      <input 
                        type="text" 
                        required
                        value={binTransferModal.sourceBin}
                        onChange={e => setBinTransferModal(prev => ({...prev, sourceBin: e.target.value}))}
                        placeholder="e.g. BIN-B4-12" 
                        className="w-full border border-border rounded-lg px-3 py-2 text-sm font-mono bg-slate-50"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Destination Location (To)</label>
                      <input 
                        type="text" 
                        required
                        value={binTransferModal.destBin}
                        onChange={e => setBinTransferModal(prev => ({...prev, destBin: e.target.value}))}
                        placeholder="e.g. BIN-E5-99" 
                        className="w-full border border-border rounded-lg px-3 py-2 text-sm font-mono focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Quantity to Move</label>
                      <input 
                        type="number" 
                        required
                        min="1"
                        value={binTransferModal.qty}
                        onChange={e => setBinTransferModal(prev => ({...prev, qty: e.target.value}))}
                        placeholder="0" 
                        className="w-full border border-border rounded-lg px-3 py-2 text-sm font-mono focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      />
                    </div>
                    <div className="pt-4 flex gap-3">
                      <button type="button" onClick={() => setBinTransferModal(prev => ({...prev, isOpen: false}))} className="flex-1 bg-white border border-border text-slate-700 font-bold py-2.5 rounded-lg hover:bg-slate-50">
                        Cancel
                      </button>
                      <button type="submit" className="flex-[2] bg-accent text-white font-bold py-2.5 rounded-lg hover:bg-accent-light shadow-sm">
                        Confirm & Issue Task
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            {activeTab === 'picking' && (
              <div className="space-y-6 animate-in fade-in duration-500">
                <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-4 border-b border-border pb-4 gap-4">
                  <div>
                    <h2 className="text-2xl font-heading font-bold text-accent tracking-tight flex items-center gap-2">
                      Picking Operations
                      <span className="bg-orange-100 text-orange-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ml-2">Active Waves</span>
                    </h2>
                    <p className="text-sm text-text-muted mt-1">Multi-modal strategy tracking and operator velocity metrics</p>
                  </div>
                  <button className="flex items-center gap-2 px-4 py-2 border border-border text-sm font-semibold rounded hover:bg-slate-50 transition-colors text-text-main shadow-sm flex-shrink-0">
                    <Download className="w-4 h-4" />
                    Download Metrics
                  </button>
                </div>

                {/* Manager KPIs */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Picking Accuracy</div>
                     <div className="font-heading text-3xl font-bold text-accent flex items-baseline gap-1">
                       99.7<span className="text-xl text-slate-400">%</span>
                     </div>
                     <div className="text-[10px] text-success mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                       <Target className="w-3 h-3" /> Target &gt;99.5%
                     </div>
                  </div>
                  <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Pick Velocity (LPH)</div>
                     <div className="font-heading text-3xl font-bold text-accent justify-start flex items-baseline gap-1">
                       184
                     </div>
                     <div className="text-[10px] text-accent mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                       <Zap className="w-3 h-3 text-amber-500" /> Lines Per Hour Avg
                     </div>
                  </div>
                  <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Order Cycle Time</div>
                     <div className="font-heading text-3xl font-bold text-accent">14.2<span className="text-base text-slate-400 ml-1">Min</span></div>
                     <div className="text-[10px] text-text-muted mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                       <Clock className="w-3 h-3" /> Receipt to staged
                     </div>
                  </div>
                  <div className="bg-white p-5 rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
                     <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">Travel Time Load</div>
                     <div className="font-heading text-3xl font-bold text-emerald-600">42%</div>
                     <div className="text-[10px] text-emerald-600 mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                       <Navigation className="w-3 h-3" /> Down from 55%
                     </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Active Strategies */}
                  <div className="col-span-1 lg:col-span-2 bg-white rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col h-full overflow-hidden">
                    <div className="p-4 lg:p-5 border-b border-border flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Layers className="w-5 h-5 text-accent" />
                        <h3 className="font-heading font-bold text-accent">Active Picking Strategies</h3>
                      </div>
                    </div>
                    <div className="overflow-x-auto flex-1">
                       <table className="w-full text-left text-sm border-collapse min-w-[500px]">
                         <thead className="bg-[#F8FAFC]">
                           <tr>
                             <th className="px-5 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest">Method / Strategy</th>
                             <th className="px-5 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest">Target Use Case</th>
                             <th className="px-5 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest">Active Pools/Zones</th>
                             <th className="px-5 py-3 text-[10px] font-bold text-text-muted border-b border-border uppercase tracking-widest text-right">Completion</th>
                           </tr>
                         </thead>
                         <tbody className="divide-y divide-border">
                           {[
                             { method: 'Wave Picking', target: 'Carrier dispatch schedules', pools: '4 Waves Active', pct: 68 },
                             { method: 'Cluster Picking', target: 'Multi-order sorting', pools: '12 Carts', pct: 45 },
                             { method: 'Zone (Pick & Pass)', target: 'High-density areas', pools: 'Zones A, B, C', pct: 82 },
                             { method: 'Batch Picking', target: 'Single-SKU heavy orders', pools: '2 Batches', pct: 30 },
                             { method: 'Discrete (Single)', target: 'VVIP / Heavy items', pools: '5 Orders', pct: 90 },
                           ].map((s, i) => (
                             <tr key={i} className="hover:bg-slate-50 transition-colors">
                               <td className="px-5 py-4">
                                 <div className="font-semibold text-accent">{s.method}</div>
                               </td>
                               <td className="px-5 py-4 text-xs text-text-muted">{s.target}</td>
                               <td className="px-5 py-4 font-mono text-[11px] font-semibold text-slate-600">{s.pools}</td>
                               <td className="px-5 py-4 text-right">
                                 <div className="flex items-center justify-end gap-2 text-xs mb-1">
                                   <span className="font-bold text-emerald-600">{s.pct}%</span>
                                 </div>
                                 <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden max-w-[100px] ml-auto">
                                    <div className="bg-emerald-500 h-full" style={{ width: `${s.pct}%` }}></div>
                                 </div>
                               </td>
                             </tr>
                           ))}
                         </tbody>
                       </table>
                    </div>
                  </div>

                  {/* Picker Leaderboard */}
                  <div className="col-span-1 bg-white rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col h-full overflow-hidden">
                    <div className="p-4 lg:p-5 border-b border-border bg-slate-50/50">
                      <div className="flex items-center gap-2 mb-3">
                        <Users className="w-4 h-4 text-accent" />
                        <h3 className="font-heading font-bold text-accent text-sm">Picker Performance Rank</h3>
                      </div>
                      <div className="flex bg-slate-200/50 p-1 rounded-md text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-3">
                        <button onClick={() => setActiveLeaderboardSort('rank')} className={`flex-1 py-1 rounded ${activeLeaderboardSort === 'rank' ? 'bg-white text-accent shadow-sm' : ''}`}>Rank</button>
                        <button onClick={() => setActiveLeaderboardSort('lph')} className={`flex-1 py-1 rounded ${activeLeaderboardSort === 'lph' ? 'bg-white text-accent shadow-sm' : ''}`}>Pick Vel</button>
                        <button onClick={() => setActiveLeaderboardSort('acc')} className={`flex-1 py-1 rounded ${activeLeaderboardSort === 'acc' ? 'bg-white text-accent shadow-sm' : ''}`}>Accur</button>
                      </div>
                      <div className="flex gap-2">
                         <select 
                           value={leaderboardDateFilter}
                           onChange={e => setLeaderboardDateFilter(e.target.value)}
                           className="text-[10px] bg-white border border-border rounded px-2 py-1 outline-none font-bold text-slate-600 focus:border-blue-500 flex-1"
                         >
                           <option value="today">Today</option>
                           <option value="yesterday">Yesterday</option>
                           <option value="week">Past Week</option>
                         </select>
                      </div>
                    </div>
                    <div className="flex-1 overflow-y-auto p-0">
                      <table className="w-full text-left text-sm">
                         <tbody className="divide-y divide-border">
                           {pickingEngine.pickers
                           .map((p, idx) => ({
                             op: p.name,
                             lph: leaderboardDateFilter === 'week' ? 215 - (idx * 15) - 15 : 215 - (idx * 15),
                             acc: leaderboardDateFilter === 'yesterday' ? Math.max(98.5, 99.9 - (idx * 0.3) - 0.2) : 99.9 - (idx * 0.3),
                             top: idx === 0,
                             warn: idx >= 3
                           }))
                           .sort((a, b) => {
                             if (activeLeaderboardSort === 'lph') return b.lph - a.lph;
                             if (activeLeaderboardSort === 'acc') return b.acc - a.acc;
                             return 0; // maintain original array 'rank' structure
                           })
                           .map((picker, i) => (
                             <tr key={i} className="hover:bg-slate-50 transition-colors">
                               <td className="px-4 py-3">
                                 <div className="flex items-center gap-2">
                                   <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-bold ${picker.top && activeLeaderboardSort === 'rank' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-500'}`}>
                                     #{i + 1}
                                   </div>
                                   <div>
                                     <div className="font-mono text-[11px] font-bold text-accent">{picker.op}</div>
                                   </div>
                                 </div>
                               </td>
                               <td className="px-4 py-3 text-right">
                                 <div className="font-heading text-sm font-bold text-slate-700">{picker.lph} <span className="text-[9px] text-slate-400 font-sans font-normal">LPH</span></div>
                                 <div className={`text-[10px] font-bold ${picker.warn ? 'text-error' : 'text-emerald-600'}`}>{picker.acc.toFixed(1)}%</div>
                               </td>
                             </tr>
                           ))}
                         </tbody>
                      </table>
                    </div>
                  </div>

                </div>

                {/* Live Picking Dispatch & Execution Engine */}
                <div className="bg-white rounded-xl border border-border shadow-[0_2px_10px_rgba(0,0,0,0.02)] overflow-hidden">
                  <div className="p-4 lg:p-5 border-b border-border bg-slate-50/50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Cpu className="w-5 h-5 text-accent" />
                        <h3 className="font-heading font-bold text-accent">Live Execution & Dispatch Engine</h3>
                      </div>
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider bg-slate-200/50 px-2 py-1 rounded">Interactive Workflow</span>
                    </div>
                  </div>
                  <div className="p-0 flex flex-col md:flex-row divide-y md:divide-y-0 md:divide-x divide-border">
                    {/* Left Col: Pickers Tab */}
                    <div className="w-full md:w-1/3 bg-slate-50 p-5">
                       <div className="flex items-center justify-between mb-4">
                         <h4 className="font-bold text-sm text-accent flex items-center gap-2">
                            <Users className="w-4 h-4" /> Shift Roster
                         </h4>
                         <select 
                           value={pickerFilter}
                           onChange={(e) => setPickerFilter(e.target.value)}
                           className="text-[11px] font-bold text-slate-600 bg-white border border-border rounded px-2 py-1 outline-none focus:border-blue-500 shadow-sm"
                         >
                           <option value="All">All</option>
                           <option value="Available">Available</option>
                           <option value="Picking">Picking</option>
                           <option value="Verifying">Verifying</option>
                           <option value="Packing">Packing</option>
                         </select>
                       </div>
                       <div className="space-y-3">
                         {pickingEngine.pickers
                           .filter(p => pickerFilter === 'All' || p.status === pickerFilter)
                           .map(p => (
                           <div key={p.id} className="flex justify-between items-center p-3 bg-white border border-border rounded-lg shadow-sm">
                             <div className="flex items-center gap-2 flex-1">
                               {p.isEditing ? (
                                 <input 
                                   autoFocus
                                   type="text" 
                                   className="border border-blue-400 rounded px-2 py-0.5 w-full text-xs font-mono outline-none"
                                   defaultValue={p.name}
                                   onBlur={(e) => updatePickerName(p.id, e.target.value || p.name)}
                                   onKeyDown={(e) => e.key === 'Enter' && updatePickerName(p.id, e.currentTarget.value || p.name)}
                                 />
                               ) : (
                                 <div 
                                   className="font-mono text-xs font-bold text-slate-700 cursor-pointer border-b border-dashed border-slate-300 hover:border-blue-400 hover:text-blue-600 transition-colors"
                                   onClick={() => setPickerEditing(p.id, true)}
                                   title="Click to rename"
                                 >
                                   👤 {p.name}
                                 </div>
                               )}
                             </div>
                             <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ml-2 ${
                                p.status === 'Available' ? 'bg-emerald-100 text-emerald-700' :
                                p.status === 'Picking' ? 'bg-orange-100 text-orange-700' :
                                'bg-blue-100 text-blue-700'
                             }`}>{p.status}</span>
                           </div>
                         ))}
                       </div>
                    </div>

                    {/* Right Col: Operations */}
                    <div className="w-full md:w-2/3 p-5">
                       {pickingEngine.showGenerateSuccess && (
                         <div className="mb-4 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg p-3 flex items-center justify-between animate-in slide-in-from-top-2">
                           <div className="flex items-center gap-2">
                             <CheckCircle className="w-5 h-5 text-emerald-500" />
                             <span className="font-semibold text-sm">Picklists successfully generated and randomly assigned to available operators!</span>
                           </div>
                         </div>
                       )}

                       <div className="flex flex-col sm:flex-row justify-between sm:items-end mb-6 bg-slate-50 p-5 border border-slate-200 rounded-xl gap-4">
                         <div>
                           <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">Unreleased Order Queue</div>
                           <div className="text-3xl font-heading font-bold text-accent">{pickingEngine.pendingOrders} <span className="text-sm font-normal text-slate-400">Orders Pending</span></div>
                         </div>
                         <button 
                            onClick={generateWave}
                            disabled={pickingEngine.pendingOrders === 0 || !pickingEngine.pickers.find(p=>p.status==='Available')}
                            className="bg-accent text-white px-5 py-2.5 font-bold text-sm hover:bg-accent-light rounded-lg shadow-sm disabled:opacity-50 transition-colors w-full sm:w-auto"
                         >
                            Generate Picklists
                         </button>
                       </div>

                       <div className="flex flex-col sm:flex-row justify-between sm:items-center mb-4 gap-2 border-b border-border pb-3">
                         <h4 className="font-bold text-sm text-accent flex items-center gap-2">
                            <Activity className="w-4 h-4 text-blue-500" /> Active Dispatched Batches
                         </h4>
                         <button 
                           onClick={downloadAllPicklists} 
                           disabled={pickingEngine.batches.length === 0}
                           className="flex items-center gap-1 text-[11px] font-bold text-slate-600 hover:text-blue-600 disabled:opacity-50 transition-colors"
                         >
                           <Download className="w-3.5 h-3.5" /> Download All
                         </button>
                       </div>

                       <div className="space-y-3">
                         {pickingEngine.batches.filter(b => b.status !== 'Completed').length === 0 ? (
                           <div className="text-center py-8 text-slate-400 text-sm bg-slate-50 rounded-lg border border-dashed border-slate-300">
                             No active batches. Click "Generate Picklists" to dispatch orders to available operators.
                           </div>
                         ) : (
                           pickingEngine.batches.filter(b => b.status !== 'Completed').map(b => (
                             <div key={b.id} className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 bg-white border border-border rounded-lg shadow-sm gap-4">
                               <div>
                                 <div className="font-mono font-bold text-sm text-accent flex items-center gap-2">
                                   <Barcode className="w-3 h-3 text-slate-400" /> {b.id}
                                 </div>
                                 <div className="text-xs text-slate-500 mt-1">Assigned to: <span className="font-mono font-bold">{b.pickerId}</span> • {b.items} Items</div>
                                 <button onClick={() => downloadIndividualPicklist(b)} className="text-[10px] text-blue-500 hover:underline mt-1 font-semibold flex items-center gap-1">
                                   <Download className="w-3 h-3" /> Get CSV
                                 </button>
                               </div>
                               
                               <div className="flex items-center gap-3 w-full sm:w-auto">
                                 <div className={`text-[10px] font-bold px-2 py-1 rounded-sm uppercase tracking-wider ${
                                    b.status === 'Picking' ? 'text-orange-600 bg-orange-50' :
                                    b.status === 'Verifying' ? 'text-blue-600 bg-blue-50' :
                                    'text-indigo-600 bg-indigo-50'
                                 }`}>
                                   {b.status}
                                 </div>
                                 
                                 <button 
                                   onClick={() => advanceBatch(b.id)}
                                   className="text-xs font-bold bg-white border border-border text-slate-700 hover:bg-slate-50 px-3 py-1.5 rounded flex-1 sm:flex-none whitespace-nowrap shadow-sm transition-colors"
                                 >
                                   {b.status === 'Picking' ? 'Finish Collection' : 
                                    b.status === 'Verifying' ? 'Scan & Verify' : 
                                    'Handoff to Pack'}
                                 </button>
                               </div>
                             </div>
                           ))
                         )}
                       </div>
                    </div>
                  </div>
                </div>

              </div>
            )}

            {activeTab === 'deadstock' && (
              <div className="space-y-6 animate-in fade-in duration-500">
                <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-4 border-b border-border pb-4 gap-4">
                  <div>
                    <h2 className="text-2xl font-heading font-bold text-accent tracking-tight flex items-center gap-2">
                       <Archive className="w-6 h-6 text-warning" />
                       Dead Stock Analysis
                    </h2>
                    <p className="text-sm text-text-muted mt-1">Identify and liquidate stagnant inventory across marketplaces</p>
                  </div>
                </div>

                {/* KPIs */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white p-4 rounded-xl border border-border shadow-sm">
                    <div className="text-xs uppercase tracking-wider text-text-muted font-bold mb-1">Value Locked</div>
                    <div className="text-2xl font-bold text-error font-mono">₹{(deadStockMetrics.totalValueLocked / 100000).toFixed(2)}L</div>
                  </div>
                  <div className="bg-white p-4 rounded-xl border border-border shadow-sm">
                    <div className="text-xs uppercase tracking-wider text-text-muted font-bold mb-1">Stuck SKUs</div>
                    <div className="text-2xl font-bold text-slate-700 font-mono">{deadStockMetrics.stuckSKUs}</div>
                  </div>
                  <div className="bg-white p-4 rounded-xl border border-border shadow-sm">
                    <div className="text-xs uppercase tracking-wider text-text-muted font-bold mb-1">Avg Aging</div>
                    <div className="text-2xl font-bold text-warning font-mono">{deadStockMetrics.avgAge} Days</div>
                  </div>
                   <div className="bg-white p-4 rounded-xl border border-border shadow-sm">
                    <div className="text-xs uppercase tracking-wider text-text-muted font-bold mb-1">Highest Risk</div>
                    <div className="text-2xl font-bold text-amber-600 font-heading">{deadStockMetrics.highRiskPlatform}</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* DataTable */}
                  <div className="bg-white rounded-xl border border-border shadow-sm flex flex-col">
                     <div className="p-4 border-b border-border font-bold text-accent flex items-center justify-between">
                        Dead Stock Deep-Dive
                        <button className="text-xs font-semibold text-primary flex items-center gap-1 hover:text-blue-700 bg-blue-50 px-2 py-1 rounded">
                          Export <Download className="w-3 h-3" />
                        </button>
                     </div>
                     <div className="p-0 overflow-x-auto flex-1">
                       <table className="w-full text-sm text-left">
                         <thead className="text-xs text-text-muted uppercase bg-slate-50 border-b border-border">
                           <tr>
                              <th className="px-4 py-3">SKU</th>
                              <th className="px-4 py-3">Location</th>
                              <th className="px-4 py-3">Platform</th>
                              <th className="px-4 py-3">Days</th>
                              <th className="px-4 py-3 text-right">Val (₹)</th>
                           </tr>
                         </thead>
                         <tbody className="divide-y divide-border">
                           {deadStockTable.map(item => (
                             <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                               <td className="px-4 py-3 font-mono font-medium text-slate-700 text-xs">{item.sku}</td>
                               <td className="px-4 py-3 text-xs">{item.location}</td>
                               <td className="px-4 py-3 text-[11px] font-bold text-slate-600"><span className="px-2 py-1 rounded-full bg-slate-100 border border-slate-200 uppercase">{item.marketplace}</span></td>
                               <td className="px-4 py-3 font-bold text-error text-xs">{item.daysStuck}d</td>
                               <td className="px-4 py-3 text-right font-medium text-xs text-slate-600">{(item.total / 1000).toFixed(1)}k</td>
                             </tr>
                           ))}
                         </tbody>
                       </table>
                     </div>
                  </div>

                  {/* Chart representation */}
                  <div className="bg-white rounded-xl border border-border shadow-sm p-4 flex flex-col min-h-[300px]">
                     <div className="font-bold text-accent mb-4">Stock Aging by Marketplace</div>
                     <div className="flex-1 min-h-[250px] mt-2">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={deadStockData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                            <XAxis dataKey="platform" type="category" tickLine={false} axisLine={false} className="text-[11px] font-bold text-text-muted" />
                            <YAxis tickLine={false} axisLine={false} className="text-xs text-text-muted" />
                            <Tooltip 
                               contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}
                               cursor={{fill: 'rgba(0,0,0,0.04)'}}
                            />
                            <Legend wrapperStyle={{fontSize: '11px', fontWeight: 'bold', paddingTop: '10px'}} />
                            <Bar dataKey="120+ Days" stackId="a" fill="#ef4444" radius={[0, 0, 4, 4]} />
                            <Bar dataKey="90-120 Days" stackId="a" fill="#f97316" />
                            <Bar dataKey="60-90 Days" stackId="a" fill="#facc15" />
                            <Bar dataKey="30-60 Days" stackId="a" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                     </div>
                  </div>
                </div>
              </div>
            )}

            {/* AI Assistant Module */}
            {activeTab === 'ai' && (
              <div className="space-y-6 animate-in fade-in duration-500 flex flex-col h-[calc(100vh-140px)]">
                <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-4 border-b border-border pb-4 gap-4 flex-shrink-0">
                  <div>
                    <h2 className="text-2xl font-heading font-bold text-accent tracking-tight flex items-center gap-2">
                       <Sparkles className="w-6 h-6 text-purple-600" />
                       Gemini ERP Assistant
                    </h2>
                    <p className="text-sm text-text-muted mt-1">Ask questions, generate reports, and automate tasks using your ERP data.</p>
                  </div>
                </div>

                <div className="flex-1 bg-white rounded-xl border border-border shadow-sm flex flex-col overflow-hidden">
                  <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50">
                    <div className="flex items-start gap-4">
                       <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0 border border-purple-200">
                          <Bot className="w-5 h-5 text-purple-600" />
                       </div>
                       <div className="bg-white p-4 rounded-xl shadow-sm border border-border rounded-tl-none max-w-[80%]">
                          <p className="text-sm text-slate-700 leading-relaxed font-medium">
                            Hello! I am your AI ERP Assistant powered by Gemini. <br/><br/>
                            <span className="font-bold">I can help you with:</span>
                          </p>
                          <ul className="mt-2 space-y-1 text-sm text-slate-600 list-disc list-inside">
                             <li>Tracking live stock across all integrated platforms.</li>
                             <li>Analyzing picking efficiency and operations bottlenecks.</li>
                             <li>Resolving inventory mismatch data anomalies.</li>
                             <li>Generating SLA breach and DMAIC variance reports.</li>
                          </ul>
                          <p className="text-xs text-text-muted mt-4 p-2 bg-slate-50 border border-border rounded">
                            Note: This assistant is strictly linked to your ERP data. It will not answer questions unrelated to inventory, auditing, executive summaries, or logistics.
                          </p>
                       </div>
                    </div>

                    <div className="flex items-start gap-4 flex-row-reverse">
                       <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 border border-blue-200">
                          <Users className="w-5 h-5 text-blue-600" />
                       </div>
                       <div className="bg-blue-600 text-white p-4 rounded-xl shadow-sm rounded-tr-none max-w-[80%]">
                          <p className="text-sm leading-relaxed">
                            Which platform has the highest dead stock right now?
                          </p>
                       </div>
                    </div>

                    <div className="flex items-start gap-4">
                       <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0 border border-purple-200">
                          <Bot className="w-5 h-5 text-purple-600" />
                       </div>
                       <div className="bg-white p-4 rounded-xl shadow-sm border border-border rounded-tl-none max-w-[80%]">
                          <p className="text-sm text-slate-700 leading-relaxed">
                            Currently, <span className="font-bold text-accent">Amazon</span> represents the highest dead stock exposure with <span className="font-bold text-error">420 units</span> stuck for 30-60 days and <span className="font-bold text-error">85 units</span> stuck for over 120 days.
                          </p>
                       </div>
                    </div>

                  </div>
                  <div className="p-4 border-t border-border bg-white">
                     <div className="flex gap-2">
                        <input 
                          type="text" 
                          placeholder="Ask Gemini about your ERP metrics..." 
                          className="flex-1 bg-slate-50 border border-border px-4 py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition-all"
                          readOnly
                        />
                        <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2.5 rounded-lg transition-colors flex items-center justify-center w-12 flex-shrink-0 shadow-sm border border-purple-700">
                           <Send className="w-4 h-4" />
                        </button>
                     </div>
                     <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
                        <button className="whitespace-nowrap text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-full font-medium transition-colors border border-border">Analyze SLA breaches today</button>
                        <button className="whitespace-nowrap text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-full font-medium transition-colors border border-border">Find low stock SKUs</button>
                        <button className="whitespace-nowrap text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-full font-medium transition-colors border border-border">Generate audit variance report</button>
                     </div>
                  </div>
                </div>
              </div>
            )}

            {/* Integrations Module */}
            {activeTab === 'integrations' && (
              <div className="space-y-6 animate-in fade-in duration-500">
                <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-4 border-b border-border pb-4 gap-4">
                  <div>
                    <h2 className="text-2xl font-heading font-bold text-accent tracking-tight flex items-center gap-2">
                       <Plug2 className="w-6 h-6 text-blue-600" />
                       Marketplace API Integrations
                    </h2>
                    <p className="text-sm text-text-muted mt-1">Live stock tracking, API webhooks, and automated inventory alerts.</p>
                  </div>
                  <button className="bg-accent text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm hover:bg-accent/90 transition-all flex items-center justify-center gap-2">
                    <Plus className="w-4 h-4" /> Add Integration
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                   {/* Left Col: Platforms */}
                   <div className="lg:col-span-2 space-y-4">
                      <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">
                         <div className="p-4 border-b border-border bg-slate-50 flex items-center justify-between">
                            <h3 className="font-bold text-accent">Active Connections</h3>
                         </div>
                         <div className="divide-y divide-border">
                            {integrationPlatforms.map(platform => (
                               <div key={platform.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50 transition-colors">
                                  <div className="flex items-center gap-4">
                                     <div className={`w-12 h-12 rounded-xl flex items-center justify-center border shadow-sm ${
                                        platform.status === 'Live' ? 'bg-emerald-50 border-emerald-100' :
                                        platform.status === 'Syncing' ? 'bg-blue-50 border-blue-100' :
                                        'bg-error/10 border-error/20'
                                     }`}>
                                        <platform.icon className={`w-6 h-6 ${
                                          platform.status === 'Live' ? 'text-emerald-600' :
                                          platform.status === 'Syncing' ? 'text-blue-600' :
                                          'text-error'
                                        }`} />
                                     </div>
                                     <div>
                                        <div className="font-bold text-accent">{platform.name}</div>
                                        <div className="text-xs text-text-muted font-medium mt-0.5">{platform.type}</div>
                                     </div>
                                  </div>
                                  <div className="flex flex-row sm:flex-col items-center sm:items-end justify-between sm:justify-center gap-2 sm:gap-1">
                                     <div className="flex items-center gap-1.5">
                                        <div className={`w-2 h-2 rounded-full ${
                                           platform.status === 'Live' ? 'bg-emerald-500 animate-pulse' :
                                           platform.status === 'Syncing' ? 'bg-blue-500 animate-pulse' :
                                           'bg-error'
                                        }`}></div>
                                        <span className={`text-xs font-bold uppercase tracking-wider ${
                                           platform.status === 'Live' ? 'text-emerald-700' :
                                           platform.status === 'Syncing' ? 'text-blue-700' :
                                           'text-error'
                                        }`}>{platform.status}</span>
                                     </div>
                                     <div className="text-[11px] text-slate-500 font-mono">Last Sync: {platform.lastSync}</div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                     <button className="text-xs font-semibold px-3 py-1.5 border border-border rounded hover:bg-slate-100 text-slate-700 transition-colors bg-white shadow-sm">Config</button>
                                  </div>
                               </div>
                            ))}
                         </div>
                      </div>

                      <div className="bg-white rounded-xl border border-border shadow-sm p-5">
                         <h3 className="font-bold text-accent mb-2 flex items-center gap-2">
                           <Layers className="w-5 h-5 text-purple-600" />
                           Integration Guide (Marketplace APIs)
                         </h3>
                         <div className="text-sm text-slate-600 space-y-3 mt-4">
                           <p><strong>1. API Credentials:</strong> Obtain your Client ID and Setup Tokens directly from the marketplace portal (e.g., Amazon Seller Central, Flipkart Seller Hub).</p>
                           <p><strong>2. Setup Webhooks:</strong> Configure endpoint URLs in the seller portal to point to: <code className="bg-slate-100 text-purple-700 px-1.5 py-0.5 rounded text-xs select-all">https://api.this-erp.com/webhooks/marketplace</code></p>
                           <p><strong>3. Live Stock Tracking:</strong> Once connected, the ERP becomes the "Master Node". Any order received via webhook immediately decrements the stock on the Master Node, which then broadcasts the new stock quantities back to all connected platforms simultaneously to prevent overselling.</p>
                         </div>
                      </div>
                   </div>

                   {/* Right Col: Automations */}
                   <div className="space-y-4">
                      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 shadow-sm text-sm">
                         <div className="font-bold text-amber-800 flex items-center gap-2 mb-2">
                            <BellRing className="w-5 h-5" />
                            Live Trigger Alerts
                         </div>
                         <p className="text-amber-700 text-xs leading-relaxed mb-3">
                            When stock drops below threshold, this system will automatically fire an email to procurement and notify managers.
                         </p>
                         <button className="w-full bg-amber-100 hover:bg-amber-200 text-amber-800 text-xs font-bold py-2 rounded transition-colors border border-amber-300 shadow-sm">View Trigger Logs</button>
                      </div>

                      <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">
                         <div className="p-4 border-b border-border bg-slate-50 flex items-center justify-between">
                            <h3 className="font-bold text-accent">Automations</h3>
                            <button className="text-primary hover:text-blue-700 p-1"><Plus className="w-4 h-4" /></button>
                         </div>
                         <div className="divide-y divide-border">
                            {automationRules.map(rule => (
                               <div key={rule.id} className="p-4">
                                  <div className="flex items-center justify-between mb-2">
                                     <div className="font-bold text-sm text-slate-800">{rule.name}</div>
                                     <div className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${rule.status === 'Active' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-slate-100 text-slate-500 border-slate-200'}`}>
                                        {rule.status}
                                     </div>
                                  </div>
                                  <div className="text-xs text-slate-600 bg-slate-50 p-2 rounded border border-slate-100 font-mono mb-2">
                                     {rule.condition}
                                  </div>
                                  <div className="flex items-center gap-1.5 text-xs font-medium text-purple-700 mb-2">
                                     <ArrowRight className="w-3 h-3" /> {rule.action}
                                  </div>
                                  <div className="text-[10px] font-bold text-text-muted uppercase">Applies To: {rule.appliesTo}</div>
                               </div>
                            ))}
                         </div>
                      </div>
                   </div>
                </div>
              </div>
            )}

            {/* Fallback Module View for unconfigured tabs */}
            {!['executive', 'operations', 'audit', 'dispatch', 'mismatch', 'grn', 'bin', 'picking', 'deadstock', 'integrations', 'ai'].includes(activeTab) && (() => {
              const getFallbackConfig = (tabId: string) => {
                switch (tabId) {
                  case 'grn': return { m1: ['Receiving Queue', Math.floor(executiveMetrics.orders * 0.4)], m2: ['Unloading Time', '45 Min'], m3: ['Dock Occupancy', '82%'], m4: ['Demurrage Risk', 'Low'] };
                  case 'bin': return { m1: ['Active Bins', '24,105'], m2: ['Utilization', '89.4%'], m3: ['Empty Slots', '2,400'], m4: ['Consolidation Op', 'Ready'] };
                  case 'picking': return { m1: ['Active Waves', '14'], m2: ['Units/Hr', '450'], m3: ['Picker Load', 'High'], m4: ['Short Picks', '0.2%'] };
                  case 'deadstock': return { m1: ['Stagnant Units', '1,420'], m2: ['Working Cap Blocked', `₹${Math.floor(executiveMetrics.revenue * 0.05).toLocaleString()}`], m3: ['Avg Aging', '114 Days'], m4: ['Liquidation Est', '₹1.2L'] };
                  case 'dmaic': return { m1: ['Active Projects', '4'], m2: ['Variances Detect', '12'], m3: ['Sigma Level', '4.8'], m4: ['Kaizen Events', '2'] };
                  case 'kpi': return { m1: ['Tracked Metrics', '142'], m2: ['SLA Breaches', '0'], m3: ['Data Latency', '1.2s'], m4: ['Forecast Acc', '94%'] };
                  case 'ai': return { m1: ['Query Volume', '140'], m2: ['Avg Confidence', '98%'], m3: ['Anomalies Found', '3'], m4: ['Time Saved', '14 Hrs'] };
                  default: return { m1: ['Throughput Vol', (executiveMetrics.orders * 2.4).toLocaleString()], m2: ['Cycle Time SLA', `${executiveMetrics.leadTime.toFixed(1)} Hrs`], m3: ['Efficiency Rating', '94.2%'], m4: ['Cost Load', `₹${Math.floor(executiveMetrics.avgCost * 0.8).toLocaleString()}`] };
                }
              };
              const fb = getFallbackConfig(activeTab);

              return (
              <div className="space-y-6 animate-in fade-in duration-500">
                <div className="flex items-end justify-between mb-4 border-b border-border pb-4">
                  <div>
                    <h2 className="text-2xl font-heading font-bold text-accent tracking-tight flex items-center gap-2">
                       {SIDEBAR_ITEMS.find(i => i.id === activeTab)?.label}
                       <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ml-3">Live Integration</span>
                    </h2>
                    <p className="text-sm text-text-muted mt-1">Metrics synchronised with Executive Command</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  {/* Reuse some metrics to make it look active */}
                  <div className="bg-white p-5 rounded-xl border border-border">
                    <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">{fb.m1[0]}</div>
                    <div className="font-heading text-3xl font-bold text-accent">{fb.m1[1]}</div>
                    <div className="text-[10px] text-success mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                      <TrendingUp className="w-3 h-3" /> Nominal
                    </div>
                  </div>
                  <div className="bg-white p-5 rounded-xl border border-border">
                    <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">{fb.m2[0]}</div>
                    <div className="font-heading text-3xl font-bold text-accent">{fb.m2[1]}</div>
                     <div className="text-[10px] text-success mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                      <CheckCircle className="w-3 h-3" /> Target Exceeded
                    </div>
                  </div>
                  <div className="bg-white p-5 rounded-xl border border-border">
                    <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">{fb.m3[0]}</div>
                    <div className="font-heading text-3xl font-bold text-accent">{fb.m3[1]}</div>
                     <div className="text-[10px] text-accent mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                      <Activity className="w-3 h-3 text-slate-400" /> Operational
                    </div>
                  </div>
                  <div className="bg-white p-5 rounded-xl border border-border">
                    <div className="text-[11px] uppercase tracking-wide text-text-muted font-bold mb-2">{fb.m4[0]}</div>
                    <div className="font-heading text-3xl font-bold text-accent">{fb.m4[1]}</div>
                     <div className="text-[10px] text-emerald-600 mt-2 font-bold uppercase flex items-center gap-1 tracking-wider">
                      <ArrowUpRight className="w-3 h-3" /> Favorable
                    </div>
                  </div>
                </div>

                <div className="enterprise-widget flex flex-col items-center justify-center p-12 text-center border border-border bg-slate-50/50 rounded-xl relative overflow-hidden">
                  <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:14px_24px]"></div>
                  <div className="relative z-10 max-w-sm mx-auto">
                    <div className="w-16 h-16 bg-white border border-border rounded-2xl flex items-center justify-center text-slate-400 shadow-sm mx-auto mb-4">
                      <Activity className="w-8 h-8 opacity-50" />
                    </div>
                    <h3 className="font-heading font-bold text-lg text-accent mb-2">Data Synchronized</h3>
                    <p className="text-sm text-text-muted">
                      This module is currently streaming data into the global Operational Command. Dedicated analytical views for this specific namespace are being configured by the administrative team.
                    </p>
                  </div>
                </div>

              </div>
              );
            })()}

          </div>
        </main>
      </div>
    </div>
  );
}

