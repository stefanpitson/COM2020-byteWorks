import { useState, useEffect, useRef } from "react";
import api from "../../api/axiosConfig";
import { getAllVendors } from "../../api/vendors";
import { getReportList } from "../../api/reports";
import type { Vendor, Report } from "../../types";

const CheckCircleIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="size-6 text-green-500">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
);

const ChevronDownIcon = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className || "size-5"}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
    </svg>
);

export default function CustomerReports() {
    const [activeTab, setActiveTab] = useState<"submit" | "history">("submit");
    const [expandedReportId, setExpandedReportId] = useState<number | null>(null);

    const [message, setMessage] = useState("");
    const [subject, setSubject] = useState("");
    const [target, setTarget] = useState<number | "">("");
    const [searchTerm, setSearchTerm] = useState("");
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    const [vendors, setVendors] = useState<Vendor[]>([]);
    const [myReports, setMyReports] = useState<Report[]>([]);;

    const [success, setSuccess] = useState(false);
    const [serverError, setServerError] = useState("");
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsDropdownOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const fetchPageData = async () => {
        try {
            setLoading(true);
            const [vendorsData, reportsData] = await Promise.all([
                getAllVendors(),
                getReportList()
            ]);
            
            setVendors(vendorsData?.vendors || []);
            setMyReports(reportsData?.reports || []);
        } catch (err) {
            console.error("Failed to load page data:", err);
            setServerError("Could not load data. Please refresh.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPageData();
    }, []);

    const handleVendorSelection = (vendorId: number, vendorName: string) => {
        setTarget(vendorId);
        setSearchTerm(vendorName);
        setIsDropdownOpen(false);
    }

    const filteredVendors = vendors.filter((vendor) =>
        vendor.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const validateForm = () => {
        if (!target) {
            setServerError("Please select a vendor.");
            return false;
        }
        if (!subject.trim() || !message.trim()) {
            setServerError("Please provide both a subject and a message.");
            return false;
        }
        return true;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setServerError("");

        if (!validateForm()) return;

        setSubmitting(true);

        try  {
            const payload = {
                vendor_id: target,
                title: subject,
                complaint: message
            };

            await api.post("/reports/create", payload)

            setSuccess(true);
            fetchPageData(); 
            
            setTarget("");
            setSearchTerm("");
            setSubject("");
            setMessage("");

            setTimeout(() => {
                setSuccess(false);
                setActiveTab("history"); 
            }, 2000);

        } catch (err: any) {
            console.error(err);
            setServerError(err.response?.data?.detail || "Submission failed. Please try again.")
        } finally {
            setSubmitting(false);
        }
    };

    const getVendorName = (vendorId: number) => {
        const vendor = vendors.find(v => v.vendor_id === vendorId);
        return vendor ? vendor.name : `Vendor #${vendorId}`;
    };

    if (loading) {
        return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="animate-spin w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full" />
        </div>
        );
    }

    return (
        <div className="min-h-screen bg-pattern pb-12 pt-24 px-4 sm:px-6">
            <div className="max-w-4xl mx-auto">

                <div className="text-center mb-8">
                    <h1 className="text-3xl font-extrabold text-[hsl(var(--text-main))] mb-6">
                        Feedback & Reports
                    </h1>
                    
                    <div className="flex justify-center gap-4">
                        <button
                            onClick={() => setActiveTab("submit")}
                            className={`px-6 py-2.5 rounded-full font-bold transition-all shadow-sm ${
                                activeTab === "submit" 
                                ? "bg-primary text-white scale-105" 
                                : "bg-white text-gray-600 hover:bg-gray-50 hover:text-primary"
                            }`}
                        >
                            Submit Feedback
                        </button>
                        <button
                            onClick={() => setActiveTab("history")}
                            className={`px-6 py-2.5 rounded-full font-bold transition-all shadow-sm flex items-center gap-2 ${
                                activeTab === "history" 
                                ? "bg-primary text-white scale-105" 
                                : "bg-white text-gray-600 hover:bg-gray-50 hover:text-primary"
                            }`}
                        >
                            My History
                            {myReports.length > 0 && (
                                <span className={`text-xs px-2 py-0.5 rounded-full ${activeTab === "history" ? "bg-white text-primary" : "bg-gray-200 text-gray-700"}`}>
                                    {myReports.length}
                                </span>
                            )}
                        </button>
                    </div>
                </div>

                <div className="transition-all duration-300 ease-in-out">
                    
                    {activeTab === "history" && (
                        <div className="bg-white rounded-xl shadow-lg p-6 md:p-8 animate-in fade-in slide-in-from-bottom-4 duration-300">
                            <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Feedback History</h2>
                            
                            {myReports.length === 0 ? (
                                <div className="text-center py-10">
                                    <p className="text-gray-500 italic mb-4">You have not submitted any feedback yet.</p>
                                    <button 
                                        onClick={() => setActiveTab("submit")}
                                        className="text-primary font-bold hover:underline"
                                    >
                                        Create a report &rarr;
                                    </button>
                                </div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left border-collapse">
                                        <thead>
                                            <tr className="bg-gray-50 text-gray-600 text-sm border-b">
                                                <th className="p-3">Vendor</th>
                                                <th className="p-3">Subject</th>
                                                <th className="p-3">Status</th>
                                                <th className="p-3">Response</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200">
                                            {myReports.map((report) => (
                                                <tr 
                                                    key={report.report_id} 
                                                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                                                    onClick={() => setExpandedReportId(expandedReportId === report.report_id ? null : report.report_id)}
                                                >
                                                    <td className="p-3 text-sm font-medium text-gray-900 whitespace-nowrap">
                                                        {getVendorName(report.vendor_id)}
                                                    </td>
                                                    <td className="p-3 text-sm text-gray-700">
                                                        {report.title}
                                                    </td>
                                                    <td className="p-3">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${report.responded ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>
                                                            {report.responded ? "Replied" : "Pending"}
                                                        </span>
                                                    </td>
                                                    <td 
                                                        className={`p-3 text-sm text-gray-600 transition-all ${
                                                            expandedReportId === report.report_id
                                                                ? "whitespace-pre-wrap"
                                                                : "max-w-xs truncate"
                                                        }`}
                                                    >
                                                        {report.responded && report.response ? (
                                                            <span className="italic">"{report.response}"</span>
                                                        ) : (
                                                            <span className="text-gray-400">-</span>
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

                    {activeTab === "submit" && (
                        <div className="bg-white rounded-xl shadow-lg p-6 md:p-8">
                            <h2 className="text-xl font-bold text-gray-800 mb-6 border-b pb-2">Submit New Feedback</h2>

                            {success && (
                                <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                                    <div className="bg-white rounded-xl shadow-xl p-8 max-w-md w-full text-center">
                                        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                                            <CheckCircleIcon />
                                        </div>
                                        <h2 className="text-2xl font-extrabold text-gray-800 mb-2">Feedback submitted!</h2>
                                        <div className="text-gray-500">Redirecting to history...</div>
                                    </div>
                                </div>
                            )}

                            <form onSubmit={handleSubmit} className="space-y-6">
                                <div className="relative" ref={dropdownRef}>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Vendor
                                    </label>
                                    
                                    <div className="relative">
                                        <input
                                            type="text"
                                            value={searchTerm}
                                            placeholder="Select or search for a vendor..."
                                            onClick={() => setIsDropdownOpen(true)}
                                            onChange={(e) => {
                                                setSearchTerm(e.target.value);
                                                setTarget(""); 
                                                setIsDropdownOpen(true); 
                                            }}
                                            className="w-full text-left px-4 py-2 pr-10 border border-gray-300 rounded shadow-sm ring-0 focus:ring-2 focus:ring-primary focus:border-transparent focus:outline-none"
                                        />
                                        
                                        <div 
                                            className="absolute inset-y-0 right-0 flex items-center pr-3 cursor-pointer"
                                            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                        >
                                            <ChevronDownIcon 
                                                className={`size-5 text-gray-500 transition-transform duration-200 ${isDropdownOpen ? "rotate-180" : ""}`} 
                                            />
                                        </div>
                                    </div>

                                    {isDropdownOpen &&(
                                        <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                                            {vendors.length === 0 ? (
                                                <li className="px-4 py-2 text-gray-500">Loading vendors...</li>
                                            ) : filteredVendors.length === 0 ? (
                                                <li className="px-4 py-2 text-gray-500">No vendors found.</li>
                                            ) : (
                                                filteredVendors.map((vendor) => (
                                                    <li
                                                        key={vendor.vendor_id}
                                                        onClick={() => handleVendorSelection(vendor.vendor_id!, vendor.name)}
                                                        className="px-4 py-2 hover:bg-primary hover:text-white cursor-pointer transition-colors"
                                                    >
                                                        {vendor.name}
                                                    </li>
                                                ))
                                            )}
                                        </ul>
                                    )}
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Subject
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        value={subject}
                                        onChange={(e) => setSubject(e.target.value)}
                                        className="w-full px-4 py-2 border border-gray-300 rounded shadow-sm ring-0 focus:ring-2 focus:ring-primary focus:border-transparent focus:outline-none"
                                        placeholder="Brief summary of your feedback (minimum 5 characters)..."
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Message
                                    </label>
                                    <textarea
                                        required
                                        rows={4}
                                        value={message}
                                        onChange={(e) => setMessage(e.target.value)}
                                        className="w-full px-4 py-2 border border-gray-300 rounded shadow-sm ring-0 focus:ring-2 focus:ring-primary focus:border-transparent focus:outline-none resize-none"
                                        placeholder="Write your feedback here (minimum 32 characters)...."
                                    />
                                </div>

                                {serverError && (
                                    <div className="mb-4 text-red-600 bg-red-50 p-3 border border-red-200 rounded">
                                        {serverError}
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    disabled={submitting || message.length < 32 || subject.length < 5 || !target}
                                    className="w-full bg-primary text-white font-bold text-lg py-3 rounded hover:bg-primaryHover hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 shadow-sm"
                                >
                                    {submitting ? (
                                    <span>Submitting...</span>
                                    ) : (
                                    <span>Submit Feedback</span>
                                    )}
                                </button>
                            </form>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
