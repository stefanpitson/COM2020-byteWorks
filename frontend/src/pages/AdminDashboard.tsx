import { useState, useEffect } from "react";
import api from "../api/axiosConfig";
import { getReportList } from "../api/reports";
import type { Vendor, Report, User } from "../types";

const CheckCircleIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="size-6 text-green-500">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
);

const AlertIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="size-6 text-red-500">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
    </svg>
);

const TrashIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
    </svg>
);

type Tab = "vendors" | "reports" | "inventory" | "users";
const TABS: Tab[] = ["vendors", "reports", "inventory", "users"];

export default function AdminDashboard() {
    const [activeTab, setActiveTab] = useState<Tab>("vendors");
    
    const [unverifiedVendors, setUnverifiedVendors] = useState<Vendor[]>([]);
    const [allReports, setAllReports] = useState<Report[]>([]);
    const [allUsers, setAllUsers] = useState<User[]>([]);
    const [expandedReportId, setExpandedReportId] = useState<number | null>(null);

    const [templateIdToDelete, setTemplateIdToDelete] = useState("");
    const [bundleTemplateId, setBundleTemplateId] = useState("");
    const [bundleAmount, setBundleAmount] = useState("");

    const [loading, setLoading] = useState(false);
    const [successMsg, setSuccessMsg] = useState("");
    const [errorMsg, setErrorMsg] = useState("");

    const fetchVendors = async () => {
        try {
            setLoading(true);
            const res = await api.get<{total_count: number; vendors: Vendor[]}>("/admin/vendors");
            setUnverifiedVendors(res.data.vendors || []);
        } catch {
            setErrorMsg("Failed to fetch vendors.");
        } finally {
            setLoading(false);
        }
    };

    const fetchReports = async () => {
        try {
            setLoading(true);
            const res = await getReportList();
            setAllReports(res.reports || []);
        } catch {
            setErrorMsg("Failed to fetch reports.");
        } finally {
            setLoading(false);
        }
    };

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const res = await api.get<{total_count: number; users: User[]}>("/admin/users");
            setAllUsers(res.data.users || []);
        } catch {
            setErrorMsg("Failed to fetch users.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        setErrorMsg("");
        setSuccessMsg("");
        if (activeTab === "vendors") fetchVendors();
        if (activeTab === "reports") fetchReports();
        if (activeTab === "users") fetchUsers();
    }, [activeTab]);


    const handleApproveVendor = async (vendorId: number | undefined) => {
        if (!vendorId) return;
        try {
            await api.patch(`/admin/vendor/validate/${vendorId}`);
            setSuccessMsg(`Vendor #${vendorId} approved.`);
            fetchVendors();
        } catch (err: any) {
            setErrorMsg(err.response?.data?.detail || "Failed to approve vendor.");
        }
    };

    const handleDeleteUser = async (userId: number) => {
        if (!window.confirm(`Are you sure you want to delete User #${userId}? This cannot be undone.`)) return;
        
        try {
            await api.delete(`/admin/users/${userId}`);
            setSuccessMsg(`User #${userId} deleted.`);
            fetchUsers();
        } catch (err: any) {
            setErrorMsg(err.response?.data?.detail || "Failed to delete user.");
        }
    };

    const handleDeleteTemplate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!templateIdToDelete) return;
        if (!window.confirm("Delete this template?")) return;

        try {
            await api.delete(`/templates/${templateIdToDelete}`);
            setSuccessMsg(`Template #${templateIdToDelete} deleted.`);
            setTemplateIdToDelete("");
        } catch (err: any) {
            setErrorMsg(err.response?.data?.detail || "Failed to delete template.");
        }
    };

    const handleDeleteBundles = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!bundleTemplateId || !bundleAmount) return;

        try {
            await api.post("/bundles/delete", {
                template_id: parseInt(bundleTemplateId),
                amount: parseInt(bundleAmount)
            });
            setSuccessMsg(`Deleted up to ${bundleAmount} bundles from template #${bundleTemplateId}.`);
            setBundleTemplateId("");
            setBundleAmount("");
        } catch (err: any) {
            setErrorMsg(err.response?.data?.detail || "Failed to delete bundles.");
        }
    };

    return (
        <div className="min-h-screen pb-12 bg-background pt-24 px-4 sm:px-6">
            <div className="max-w-5xl mx-auto">
                
                {/* Header & Navigation */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-extrabold text-[hsl(var(--text-main))] mb-6">
                        Admin Dashboard
                    </h1>
                    
                    <div className="flex flex-wrap justify-center gap-3">
                        {TABS.map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`px-6 py-2.5 rounded-full font-bold shadow-sm capitalize transition-colors ${
                                    activeTab === tab 
                                    ? "bg-primary text-white" 
                                    : "bg-white text-gray-600 hover:bg-gray-50 hover:text-primary"
                                }`}
                            >
                                {tab}
                                {tab === "vendors" && unverifiedVendors.length > 0 && (
                                    <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${activeTab === tab ? "bg-white text-primary" : "bg-red-100 text-red-600"}`}>
                                        {unverifiedVendors.length}
                                    </span>
                                )}
                            </button>
                        ))}
                    </div>
                </div>

                {successMsg && (
                    <div className="mb-6 p-4 bg-green-50 text-green-700 rounded-lg shadow-sm flex items-center gap-2 font-medium">
                        <CheckCircleIcon /> {successMsg}
                    </div>
                )}
                {errorMsg && (
                    <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg shadow-sm flex items-center gap-2 font-medium">
                        <AlertIcon /> {errorMsg}
                    </div>
                )}

                <div className="bg-white rounded-xl shadow-lg p-6 md:p-8 min-h-[400px]">
                    
                    {/* Vendors Tab */}
                    {activeTab === "vendors" && (
                        <div>
                            <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Pending Vendor Approvals</h2>
                            {loading ? (
                                <div className="text-center py-10 text-gray-500">Loading vendors...</div>
                            ) : unverifiedVendors.length === 0 ? (
                                <div className="text-center py-10 text-gray-500 italic">No vendors currently pending approval.</div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left border-collapse table-fixed">
                                        <thead>
                                            <tr className="bg-gray-50 text-gray-600 text-sm border-b">
                                                <th className="p-3 w-24">ID</th>
                                                <th className="p-3 w-1/3">Name</th>
                                                <th className="p-3 w-1/3">Location</th>
                                                <th className="p-3 w-28 text-right">Action</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200">
                                            {unverifiedVendors.map(v => (
                                                <tr key={v.vendor_id} className="hover:bg-gray-50">
                                                    <td className="p-3 font-medium text-gray-900">#{v.vendor_id}</td>
                                                    <td className="p-3 truncate" title={v.name}>{v.name}</td>
                                                    <td className="p-3 text-gray-600 text-sm truncate" title={`${v.city}, ${v.post_code}`}>{v.city}, {v.post_code}</td>
                                                    <td className="p-3 text-right">
                                                        <button 
                                                            onClick={() => handleApproveVendor(v.vendor_id)}
                                                            className="bg-green-500 hover:bg-green-600 text-white px-4 py-1.5 rounded font-medium shadow-sm text-sm"
                                                        >
                                                            Approve
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Reports Tab */}
                    {activeTab === "reports" && (
                        <div>
                            <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Global System Reports</h2>
                            {loading ? (
                                <div className="text-center py-10 text-gray-500">Loading reports...</div>
                            ) : allReports.length === 0 ? (
                                <div className="text-center py-10 text-gray-500 italic">No reports have been submitted.</div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left border-collapse table-fixed">
                                        <thead>
                                            <tr className="bg-gray-50 text-gray-600 text-sm border-b">
                                                <th className="p-3 w-28">Parties</th>
                                                <th className="p-3 w-1/4">Subject</th>
                                                <th className="p-3 w-24">Status</th>
                                                <th className="p-3">Details</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200">
                                            {allReports.map(r => (
                                                <tr 
                                                    key={r.report_id} 
                                                    className="hover:bg-gray-50 cursor-pointer"
                                                    onClick={() => setExpandedReportId(expandedReportId === r.report_id ? null : r.report_id)}
                                                >
                                                    <td className="p-3 text-sm">
                                                        <div className="truncate" title={`Vendor: #${r.vendor_id}`}>V: #{r.vendor_id}</div>
                                                        <div className="text-gray-500 truncate" title={`Cust: #${r.customer_id}`}>C: #{r.customer_id}</div>
                                                    </td>
                                                    <td className="p-3 text-sm font-medium text-gray-900 truncate" title={r.title}>{r.title}</td>
                                                    <td className="p-3">
                                                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${r.responded ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>
                                                            {r.responded ? "Replied" : "Pending"}
                                                        </span>
                                                    </td>
                                                    <td className="p-3 text-sm text-gray-600">
                                                        {expandedReportId === r.report_id ? (
                                                            <div className="whitespace-pre-wrap break-words">
                                                                <div className="font-semibold text-gray-800 mb-1">Complaint:</div>
                                                                <div className="mb-3 italic border-l-2 pl-2 border-gray-300">{r.complaint}</div>
                                                                {r.responded && r.response && (
                                                                    <>
                                                                        <div className="font-semibold text-gray-800 mb-1">Response:</div>
                                                                        <div className="text-blue-700 bg-blue-50 p-2 rounded">{r.response}</div>
                                                                    </>
                                                                )}
                                                            </div>
                                                        ) : (
                                                            <div className="overflow-hidden">
                                                                <div className="truncate"><span className="font-semibold text-gray-800">C:</span> <span className="italic">{r.complaint}</span></div>
                                                                {r.responded && r.response && (
                                                                    <div className="truncate mt-1"><span className="font-semibold text-gray-800">R:</span> <span className="text-blue-700">{r.response}</span></div>
                                                                )}
                                                            </div>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Inventory Tab */}
                    {activeTab === "inventory" && (
                        <div className="space-y-8">
                            <div>
                                <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2 text-red-600">Delete Template</h2>
                                <p className="text-sm text-gray-500 mb-4">Templates can only be deleted if they do not have active reservations.</p>
                                <form onSubmit={handleDeleteTemplate} className="flex gap-4">
                                    <input 
                                        type="number" 
                                        required
                                        placeholder="Template ID" 
                                        value={templateIdToDelete}
                                        onChange={(e) => setTemplateIdToDelete(e.target.value)}
                                        className="px-4 py-2 border border-gray-300 rounded shadow-sm focus:ring-2 focus:ring-red-500 focus:outline-none w-48"
                                    />
                                    <button type="submit" className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded font-bold shadow-sm flex items-center gap-2">
                                        <TrashIcon /> Delete Template
                                    </button>
                                </form>
                            </div>

                            <div>
                                <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2 text-red-600">Delete Unreserved Bundles</h2>
                                <p className="text-sm text-gray-500 mb-4">Remove a specific amount of unreserved bundles for a given template.</p>
                                <form onSubmit={handleDeleteBundles} className="flex flex-wrap gap-4 items-end">
                                    <div>
                                        <label className="block text-xs font-bold text-gray-500 mb-1 uppercase">Template ID</label>
                                        <input 
                                            type="number" 
                                            required
                                            value={bundleTemplateId}
                                            onChange={(e) => setBundleTemplateId(e.target.value)}
                                            className="px-4 py-2 border border-gray-300 rounded shadow-sm focus:ring-2 focus:ring-red-500 focus:outline-none w-48"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-gray-500 mb-1 uppercase">Amount to Delete</label>
                                        <input 
                                            type="number" 
                                            required
                                            min="1"
                                            value={bundleAmount}
                                            onChange={(e) => setBundleAmount(e.target.value)}
                                            className="px-4 py-2 border border-gray-300 rounded shadow-sm focus:ring-2 focus:ring-red-500 focus:outline-none w-48"
                                        />
                                    </div>
                                    <button type="submit" className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded font-bold shadow-sm flex items-center gap-2 h-[42px]">
                                        <TrashIcon /> Delete Bundles
                                    </button>
                                </form>
                            </div>
                        </div>
                    )}

                    {/* Users Tab */}
                    {activeTab === "users" && (
                        <div>
                            <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">User Management</h2>
                            {loading ? (
                                <div className="text-center py-10 text-gray-500">Loading users...</div>
                            ) : allUsers.length === 0 ? (
                                <div className="text-center py-10 text-gray-500 italic">No users found.</div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left border-collapse table-fixed">
                                        <thead>
                                            <tr className="bg-gray-50 text-gray-600 text-sm border-b">
                                                <th className="p-3 w-24">ID</th>
                                                <th className="p-3 w-1/3">Email</th>
                                                <th className="p-3 w-1/4">Role</th>
                                                <th className="p-3 w-28 text-center">Action</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200">
                                            {allUsers.map(u => (
                                                <tr key={u.user_id} className="hover:bg-gray-50">
                                                    <td className="p-3 font-medium text-gray-900">#{u.user_id}</td>
                                                    <td className="p-3 truncate" title={u.email}>{u.email}</td>
                                                    <td className="p-3 capitalize text-gray-600">{u.role}</td>
                                                    <td className="p-3 text-center">
                                                        <button 
                                                            onClick={() => handleDeleteUser(u.user_id)}
                                                            className="bg-red-500 hover:bg-red-600 text-white px-3 py-1.5 rounded font-medium shadow-sm flex items-center gap-1 justify-center w-full text-sm transition-colors"
                                                            disabled={u.role === "admin"}
                                                        >
                                                            <TrashIcon /> {u.role === "admin" ? "Admin" : "Delete"}
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
}