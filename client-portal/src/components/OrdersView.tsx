import React, { useState, useEffect } from 'react';
import { 
  Truck, 
  CheckCircle2, 
  XCircle, 
  Search, 
  ExternalLink, 
  ShieldAlert, 
  Package, 
  Send,
  Loader2,
  RefreshCw,
  Plus,
  FileText,
  User,
  Phone,
  MapPin,
  DollarSign
} from 'lucide-react';
import { CourierOrder, CourierSettings } from '../types';

interface OrdersViewProps {
  deferredData: any;
  fetchDeferred: () => Promise<void>;
  handleConfirmOrder: (orderId: string) => Promise<void>;
  handleCancelOrder: (orderId: string) => Promise<void>;
  showToast: (msg: string, isErr?: boolean) => void;
}

export function OrdersView({
  deferredData,
  fetchDeferred,
  handleConfirmOrder,
  handleCancelOrder,
  showToast
}: OrdersViewProps) {
  const [activeTab, setActiveTab] = useState<'pending' | 'shipped'>('pending');
  const [courierOrders, setCourierOrders] = useState<CourierOrder[]>([]);
  const [courierSettings, setCourierSettings] = useState<CourierSettings | null>(null);
  const [loadingOrders, setLoadingOrders] = useState<boolean>(false);
  const [submittingCourier, setSubmittingCourier] = useState<boolean>(false);
  
  // Search & Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [providerFilter, setProviderFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Send to Courier Modal State
  const [isSendModalOpen, setIsSendModalOpen] = useState<boolean>(false);
  const [selectedOrder, setSelectedOrder] = useState<any>(null);
  const [courierProvider, setCourierProvider] = useState<string>('steadfast');
  const [recipientName, setRecipientName] = useState<string>('');
  const [recipientPhone, setRecipientPhone] = useState<string>('');
  const [recipientAddress, setRecipientAddress] = useState<string>('');
  const [codAmount, setCodAmount] = useState<number>(0);
  const [itemId, setItemId] = useState<number>(0); // Pending Event ID

  const fetchCourierOrders = async () => {
    setLoadingOrders(true);
    try {
      const res = await fetch('/api/courier/orders');
      if (res.ok) {
        const data = await res.json();
        setCourierOrders(data);
      } else {
        showToast("Failed to fetch courier orders.", true);
      }
    } catch (err) {
      console.error(err);
      showToast("Error loading courier orders.", true);
    } finally {
      setLoadingOrders(false);
    }
  };

  const fetchCourierSettings = async () => {
    try {
      const res = await fetch('/api/courier/settings');
      if (res.ok) {
        const data = await res.json();
        setCourierSettings(data);
        if (data.default_courier) {
          setCourierProvider(data.default_courier);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchCourierSettings();
    fetchCourierOrders();
  }, []);

  const openSendModal = (order: any) => {
    // Find the original pending event from deferredData or fallback to fields
    // Find the event ID corresponding to orderId
    const pendingEvent = deferredData?.pendingList?.find((o: any) => o.orderId === order.orderId);
    
    // We need to fetch the full pending event metadata to get name, phone, address if available
    // For now, let's prefill with what we have
    setSelectedOrder(order);
    setRecipientName(order.customer.includes('@') ? '' : order.customer);
    setRecipientPhone(order.customer.match(/^\+?[0-9\s-]{10,15}$/) ? order.customer : '');
    setRecipientAddress('');
    setCodAmount(order.amount);
    
    // Try to find full address or details if stored locally in raw event payload (deferredData may have details)
    // In our backend, user_data.ph contains phone, user_data.em contains email, 
    // Let's call /api/events to search or use default inputs.
    // Actually, we can fetch event details or let them type it.
    // Let's call a fast endpoint to get raw event data for recipient info!
    setIsSendModalOpen(true);

    // Fetch the pending event ID
    fetchPendingEventDetails(order.orderId);
  };

  const fetchPendingEventDetails = async (orderId: string) => {
    try {
      const res = await fetch(`/api/events?limit=5&search=${orderId}`);
      if (res.ok) {
        const data = await res.json();
        const found = data.events?.find((e: any) => e.deduplicationKey === orderId || e.payload?.order_id === orderId || e.payload?.custom_data?.order_id === orderId || e.id === orderId);
        
        // Find in local pending events instead
        const peRes = await fetch(`/api/deferred`);
        if (peRes.ok) {
          const peData = await peRes.json();
          // We need event ID
          // Let's fetch details of the specific order
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Helper to retrieve the pending event DB ID
  const handleOpenSendToCourier = async (order: any) => {
    try {
      // Fetch matching pending event from server to get ID and customer details
      const res = await fetch(`/api/deferred`);
      if (res.ok) {
        const data = await res.json();
        // Since get_deferred_purchases returns pendingList with orderId, amount, customer, etc.
        // We need the database primary key ID of the PendingEvent to make a POST to /api/courier/send
        // Let's add a backend endpoint or search for the event
        // Wait! Let's check how we retrieve it.
        // We can expose the ID in `pendingList` in `client_api.py`!
        // Oh! Let's check `client_api.py` line 1020:
        // `pending_list.append({ "orderId": pe.order_id, "amount": ... })`
        // It does not include `id: pe.id`!
        // Let's modify `client_api.py` in our next step to include `"id": pe.id` in `pending_list`!
        // For now, let's assume `id` is passed, or we can find it.
        // Let's make sure we update client_api.py to include pe.id.
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSendToCourierSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!recipientName.trim() || !recipientPhone.trim() || !recipientAddress.trim()) {
      showToast("Please fill in recipient name, phone, and address.", true);
      return;
    }

    setSubmittingCourier(true);
    try {
      // Find the database ID from the selected order
      const dbId = selectedOrder.dbId || selectedOrder.id;
      if (!dbId) {
        showToast("Error: Database event ID missing.", true);
        setSubmittingCourier(false);
        return;
      }

      const payload = {
        pending_event_id: dbId,
        courier_provider: courierProvider,
        recipient_name: recipientName,
        recipient_phone: recipientPhone,
        recipient_address: recipientAddress,
        cod_amount: Number(codAmount)
      };

      const res = await fetch('/api/courier/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        showToast(`Order successfully sent to ${courierProvider.toUpperCase()}!`, false);
        setIsSendModalOpen(false);
        fetchDeferred();
        fetchCourierOrders();
      } else {
        const errData = await res.json();
        showToast(errData.detail || "Failed to send order to courier.", true);
      }
    } catch (err) {
      console.error(err);
      showToast("Network error while sending order to courier.", true);
    } finally {
      setSubmittingCourier(false);
    }
  };

  // Filtered courier orders
  const filteredCourierOrders = courierOrders.filter(order => {
    const matchesSearch = 
      order.order_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (order.recipient_phone && order.recipient_phone.includes(searchQuery)) ||
      (order.recipient_name && order.recipient_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (order.courier_tracking_id && order.courier_tracking_id.toLowerCase().includes(searchQuery.toLowerCase()));
      
    const matchesProvider = providerFilter === 'all' ? true : order.courier_provider === providerFilter;
    const matchesStatus = statusFilter === 'all' ? true : order.courier_status === statusFilter;

    return matchesSearch && matchesProvider && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const s = status.toLowerCase();
    if (s === 'delivered' || s === 'completed') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/30 dark:text-emerald-400 dark:border-emerald-900/40">
          Delivered
        </span>
      );
    }
    if (s === 'returned' || s === 'partial_returned') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/30 dark:text-rose-400 dark:border-rose-900/40">
          Returned
        </span>
      );
    }
    if (s === 'cancelled') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-50 text-slate-700 border border-slate-200 dark:bg-slate-800/40 dark:text-slate-400 dark:border-slate-800">
          Cancelled
        </span>
      );
    }
    if (s === 'in_transit' || s === 'picked_up' || s === 'shipped') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/30 dark:text-indigo-400 dark:border-indigo-900/40">
          In Transit
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/30 dark:text-amber-400 dark:border-amber-900/40">
        Pending
      </span>
    );
  };

  const getCapiStatusBadge = (sent: boolean) => {
    return sent ? (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-250 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900/60">
        Purchase Dispatched
      </span>
    ) : (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-550 border border-slate-200 dark:bg-slate-800/60 dark:text-slate-405 dark:border-slate-800">
        Awaiting Delivery
      </span>
    );
  };

  return (
    <div className="space-y-6">
      
      {/* Tab bar header */}
      <div className="flex border-b border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setActiveTab('pending')}
          className={`px-5 py-3 text-sm font-bold border-b-2 transition-all flex items-center gap-2 cursor-pointer ${
            activeTab === 'pending'
              ? 'border-indigo-650 text-indigo-650 dark:border-indigo-500 dark:text-indigo-400'
              : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-250'
          }`}
        >
          <Package className="w-4 h-4" />
          Pending COD Queue ({deferredData?.pendingCount || 0})
        </button>
        <button
          onClick={() => setActiveTab('shipped')}
          className={`px-5 py-3 text-sm font-bold border-b-2 transition-all flex items-center gap-2 cursor-pointer ${
            activeTab === 'shipped'
              ? 'border-indigo-650 text-indigo-650 dark:border-indigo-500 dark:text-indigo-400'
              : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-250'
          }`}
        >
          <Truck className="w-4 h-4" />
          Shipped Courier Log ({courierOrders.length})
        </button>
        
        <button 
          onClick={() => {
            fetchDeferred();
            fetchCourierOrders();
            showToast("Syncing data feeds...", false);
          }}
          className="ml-auto p-2 self-center rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800/40 cursor-pointer"
          title="Reload lists"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {activeTab === 'pending' && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col space-y-4 dark:bg-slate-900 dark:border-slate-800">
          <div>
            <h3 className="font-bold text-slate-850 text-sm uppercase tracking-wide dark:text-white">COD Hold Queue (Awaiting Verification)</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500">
              Orders placed via Cash on Delivery are held here. You can manually confirm them, cancel them, or automatically book them onto couriers.
            </p>
          </div>

          <div className="overflow-x-auto min-h-64">
            <table className="w-full text-left text-xs text-slate-650 divide-y divide-slate-100 min-w-[750px] dark:text-slate-300 dark:divide-slate-800">
              <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-555 dark:bg-slate-950 dark:text-slate-400">
                <tr>
                  <th className="px-6 py-3">Order ID</th>
                  <th className="px-6 py-3">Customer Info</th>
                  <th className="px-6 py-3">Value</th>
                  <th className="px-6 py-3">Fraud Score</th>
                  <th className="px-6 py-3">Time Held</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {!deferredData?.pendingList || deferredData.pendingList.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-slate-400 font-medium dark:text-slate-500">
                      <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-400 mb-2" />
                      No pending orders waiting in the verification queue.
                    </td>
                  </tr>
                ) : (
                  deferredData.pendingList.map((order: any) => (
                    <tr key={order.orderId} className="hover:bg-slate-50/50 transition-colors dark:hover:bg-slate-800/40">
                      <td className="px-6 py-3 font-mono font-bold text-slate-850 dark:text-slate-100">{order.orderId}</td>
                      <td className="px-6 py-3 font-mono text-slate-550 dark:text-slate-400">{order.customer}</td>
                      <td className="px-6 py-3 font-semibold text-slate-850 dark:text-slate-200">৳{order.amount.toLocaleString()}</td>
                      <td className="px-6 py-3">
                        <span 
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[10px] font-bold border ${
                            order.fraudScore >= 75 ? 'bg-rose-50 text-rose-700 border-rose-150 dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/60' : 
                            order.fraudScore >= 35 ? 'bg-amber-50 text-amber-700 border-amber-150 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/60' : 
                            'bg-green-50 text-green-700 border-green-150 dark:bg-green-950/20 dark:text-green-400 dark:border-green-900/60'
                          }`}
                        >
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            order.fraudScore >= 75 ? 'bg-rose-500' : 
                            order.fraudScore >= 35 ? 'bg-amber-500' : 'bg-green-500'
                          }`} />
                          Score: {order.fraudScore}/100
                        </span>
                      </td>
                      <td className="px-6 py-3 text-slate-400 font-mono dark:text-slate-500">{order.ageHours}h ago</td>
                      <td className="px-6 py-3 text-right space-x-2 whitespace-nowrap">
                        <button
                          onClick={() => {
                            setSelectedOrder(order);
                            // Pre-fill recipient fields from order
                            setRecipientName('');
                            setRecipientPhone(order.customer.match(/^\+?[0-9\s-]{10,15}$/) ? order.customer : '');
                            setRecipientAddress('');
                            setCodAmount(order.amount);
                            setIsSendModalOpen(true);
                          }}
                          className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-750 text-white text-[10px] font-bold rounded shadow-sm transition-colors cursor-pointer inline-flex items-center gap-1"
                        >
                          <Send className="w-2.5 h-2.5" /> Book Courier
                        </button>
                        <button 
                          onClick={() => handleConfirmOrder(order.orderId)}
                          className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white text-[10px] font-bold rounded shadow-sm transition-colors cursor-pointer"
                          title="Confirm without Courier (Direct CAPI Trigger)"
                        >
                          Verify Direct
                        </button>
                        <button 
                          onClick={() => handleCancelOrder(order.orderId)}
                          className="px-2.5 py-1 bg-rose-600 hover:bg-rose-700 text-white text-[10px] font-bold rounded shadow-sm transition-colors cursor-pointer"
                        >
                          Cancel
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'shipped' && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col space-y-4 dark:bg-slate-900 dark:border-slate-800">
          <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
            <div>
              <h3 className="font-bold text-slate-850 text-sm uppercase tracking-wide dark:text-white">Shipped Consignment Log</h3>
              <p className="text-xs text-slate-405 dark:text-slate-500">
                Track delivery statuses on SteadFast or Pathao. Delivery completion triggers a CAPI Purchase event; Returns fire a Refund event.
              </p>
            </div>
          </div>

          {/* Filters Bar */}
          <div className="flex flex-wrap gap-3 p-3 bg-slate-50 rounded-lg dark:bg-slate-950 border border-slate-100 dark:border-slate-850">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                placeholder="Search by Order ID, tracking or recipient..."
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white"
              />
            </div>
            
            <div className="w-[150px]">
              <select
                value={providerFilter}
                onChange={(e) => setProviderFilter(e.target.value)}
                className="w-full p-2 text-xs bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white cursor-pointer"
              >
                <option value="all">All Couriers</option>
                <option value="steadfast">SteadFast</option>
                <option value="pathao">Pathao</option>
              </select>
            </div>

            <div className="w-[150px]">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full p-2 text-xs bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white cursor-pointer"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="in_transit">In Transit</option>
                <option value="delivered">Delivered</option>
                <option value="returned">Returned</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto min-h-64">
            <table className="w-full text-left text-xs text-slate-650 divide-y divide-slate-100 min-w-[900px] dark:text-slate-300 dark:divide-slate-800">
              <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-555 dark:bg-slate-950 dark:text-slate-400">
                <tr>
                  <th className="px-5 py-3">Order ID</th>
                  <th className="px-5 py-3">Courier / Tracking</th>
                  <th className="px-5 py-3">Recipient Info</th>
                  <th className="px-5 py-3">COD Amount</th>
                  <th className="px-5 py-3">Courier Status</th>
                  <th className="px-5 py-3">CAPI Telemetry</th>
                  <th className="px-5 py-3">Booked Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {loadingOrders ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                      <Loader2 className="w-6 h-6 mx-auto animate-spin text-indigo-500 mb-2" />
                      Fetching consignment details...
                    </td>
                  </tr>
                ) : filteredCourierOrders.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-slate-400 font-medium">
                      No matching courier consignments found.
                    </td>
                  </tr>
                ) : (
                  filteredCourierOrders.map((order) => (
                    <tr key={order.id} className="hover:bg-slate-50/50 transition-colors dark:hover:bg-slate-800/40">
                      <td className="px-5 py-3 font-mono font-bold text-slate-850 dark:text-slate-100">{order.order_id}</td>
                      <td className="px-5 py-3">
                        <div className="flex flex-col">
                          <span className="font-semibold text-xs capitalize text-slate-800 dark:text-slate-200">
                            {order.courier_provider}
                          </span>
                          {order.courier_tracking_id ? (
                            <span className="font-mono text-[10px] text-slate-450 dark:text-slate-400 flex items-center gap-1 mt-0.5">
                              {order.courier_tracking_id}
                              <a
                                href={
                                  order.courier_provider === 'steadfast'
                                    ? `https://portal.steadfast.com.bd/tracking/${order.courier_tracking_id}`
                                    : `https://pathao.com/courier/tracking`
                                }
                                target="_blank"
                                rel="noreferrer"
                                className="text-indigo-500 hover:text-indigo-750 inline"
                              >
                                <ExternalLink className="w-2.5 h-2.5 inline" />
                              </a>
                            </span>
                          ) : (
                            <span className="text-[10px] text-slate-400">No Tracking</span>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex flex-col text-[11px] leading-tight">
                          <span className="font-bold text-slate-800 dark:text-slate-205">{order.recipient_name || '—'}</span>
                          <span className="text-slate-500 font-mono mt-0.5">{order.recipient_phone || '—'}</span>
                          <span className="text-[10px] text-slate-405 truncate max-w-[200px] mt-0.5" title={order.recipient_address}>
                            {order.recipient_address || '—'}
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex flex-col">
                          <span className="font-bold text-slate-850 dark:text-slate-100">৳{order.cod_amount.toLocaleString()}</span>
                          {order.delivery_charge > 0 && (
                            <span className="text-[10px] text-rose-500 font-medium">Charge: ৳{order.delivery_charge}</span>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3">{getStatusBadge(order.courier_status)}</td>
                      <td className="px-5 py-3">{getCapiStatusBadge(order.purchase_event_sent)}</td>
                      <td className="px-5 py-3 text-slate-400 font-mono text-[10px]">
                        {new Date(order.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Book to Courier Form Modal */}
      {isSendModalOpen && selectedOrder && (
        <div className="fixed inset-0 bg-slate-900/60 z-50 flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl p-6 flex flex-col space-y-5 animate-slide-in-up">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Truck className="w-5 h-5 text-indigo-650 dark:text-indigo-400" />
                <h3 className="font-bold text-slate-850 dark:text-white text-base">Book Consignment with Courier</h3>
              </div>
              <button 
                onClick={() => setIsSendModalOpen(false)}
                className="text-slate-400 hover:text-slate-655 p-1 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/40 cursor-pointer"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body Form */}
            <form onSubmit={handleSendToCourierSubmit} className="space-y-4">
              
              <div className="grid grid-cols-2 gap-4">
                {/* Order Meta details read-only */}
                <div className="p-3 bg-slate-50 rounded-lg dark:bg-slate-950/40 border border-slate-100 dark:border-slate-850">
                  <span className="block text-[10px] text-slate-400 uppercase font-bold tracking-wider">Order Reference ID</span>
                  <span className="font-mono font-bold text-sm text-slate-850 dark:text-white">{selectedOrder.orderId}</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg dark:bg-slate-950/40 border border-slate-100 dark:border-slate-850">
                  <span className="block text-[10px] text-slate-400 uppercase font-bold tracking-wider">Original Value</span>
                  <span className="font-bold text-sm text-slate-850 dark:text-white">৳{selectedOrder.amount.toLocaleString()}</span>
                </div>
              </div>

              {/* Courier Selection */}
              <div>
                <label className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Select Courier Partner</label>
                <div className="grid grid-cols-2 gap-3">
                  <label className={`border rounded-xl p-3 flex items-center justify-between cursor-pointer transition-all duration-200 ${
                    courierProvider === 'steadfast' 
                      ? 'border-indigo-600 bg-indigo-50/10 text-indigo-700 dark:border-indigo-500 dark:bg-indigo-950/20 dark:text-indigo-400' 
                      : 'border-slate-200 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-950/20'
                  }`}>
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-slate-800 dark:text-slate-200">SteadFast Courier</span>
                      <span className="text-[9px] text-slate-400 mt-0.5">Automated API Booking</span>
                    </div>
                    <input 
                      type="radio" 
                      name="provider" 
                      value="steadfast"
                      checked={courierProvider === 'steadfast'}
                      onChange={() => setCourierProvider('steadfast')}
                      className="accent-indigo-600 cursor-pointer h-4 w-4"
                    />
                  </label>

                  <label className={`border rounded-xl p-3 flex items-center justify-between cursor-pointer transition-all duration-200 ${
                    courierProvider === 'pathao' 
                      ? 'border-indigo-650 bg-indigo-50/10 text-indigo-700 dark:border-indigo-500 dark:bg-indigo-950/20 dark:text-indigo-400' 
                      : 'border-slate-200 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-950/20'
                  }`}>
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Pathao Courier</span>
                      <span className="text-[9px] text-slate-400 mt-0.5">OAuth-secured Aladdin Booking</span>
                    </div>
                    <input 
                      type="radio" 
                      name="provider" 
                      value="pathao"
                      checked={courierProvider === 'pathao'}
                      onChange={() => setCourierProvider('pathao')}
                      className="accent-indigo-600 cursor-pointer h-4 w-4"
                    />
                  </label>
                </div>
              </div>

              {/* Recipient details */}
              <div className="space-y-3 pt-2">
                <h4 className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider border-b border-slate-100 dark:border-slate-850 pb-1">
                  Recipient Information
                </h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Customer Name</label>
                    <div className="relative">
                      <User className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-400" />
                      <input
                        type="text"
                        required
                        value={recipientName}
                        onChange={(e) => setRecipientName(e.target.value)}
                        placeholder="e.g. Hridoy Hossain"
                        className="w-full pl-8 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-950 dark:border-slate-850 dark:text-white"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Phone Number</label>
                    <div className="relative">
                      <Phone className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-400" />
                      <input
                        type="tel"
                        required
                        value={recipientPhone}
                        onChange={(e) => setRecipientPhone(e.target.value)}
                        placeholder="e.g. 01712345678"
                        className="w-full pl-8 pr-3 py-2 text-xs bg-slate-50 border border-slate-205 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-950 dark:border-slate-850 dark:text-white"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Delivery Address</label>
                  <div className="relative">
                    <MapPin className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-400" />
                    <textarea
                      required
                      value={recipientAddress}
                      onChange={(e) => setRecipientAddress(e.target.value)}
                      placeholder="Enter complete shipping details (Street, District, Area)..."
                      rows={2}
                      className="w-full pl-8 pr-3 py-2 text-xs bg-slate-50 border border-slate-205 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-950 dark:border-slate-850 dark:text-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">COD Collection Amount</label>
                    <div className="relative">
                      <DollarSign className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-400" />
                      <input
                        type="number"
                        required
                        value={codAmount}
                        onChange={(e) => setCodAmount(Number(e.target.value))}
                        className="w-full pl-8 pr-3 py-2 text-xs bg-slate-50 border border-slate-205 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-950 dark:border-slate-850 dark:text-white font-bold"
                      />
                    </div>
                  </div>
                  
                  {courierProvider === 'pathao' && (
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Pathao Store ID</label>
                      <input
                        type="text"
                        disabled
                        value={courierSettings?.pathao_store_id || 'Not Set'}
                        className="w-full px-3 py-2 text-xs bg-slate-100 border border-slate-200 rounded-lg text-slate-500 dark:bg-slate-900 dark:border-slate-850 dark:text-slate-450"
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Submit Buttons */}
              <div className="flex gap-3 justify-end pt-3 border-t border-slate-100 dark:border-slate-850">
                <button
                  type="button"
                  onClick={() => setIsSendModalOpen(false)}
                  className="px-4 py-2 border border-slate-200 dark:border-slate-850 rounded-lg text-xs font-bold text-slate-500 hover:bg-slate-50 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-850 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingCourier}
                  className="px-5 py-2 bg-gradient-to-r from-indigo-600 to-violet-650 hover:from-indigo-700 hover:to-violet-755 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-md transition-all cursor-pointer flex items-center gap-1.5"
                >
                  {submittingCourier ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Booking on Courier...
                    </>
                  ) : (
                    <>
                      <Send className="w-3.5 h-3.5" /> Book on Courier
                    </>
                  )}
                </button>
              </div>

            </form>

          </div>
        </div>
      )}

    </div>
  );
}
