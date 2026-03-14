import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axiosConfig";
import { getAllVendors } from "../../api/vendors";
import type { Vendor } from "../../types"

const CheckCircleIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="size-6 text-green-500">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
);

const ChevronDownIcon = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className || "size-5"}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
    </svg>
);

export default function CustomerReports() {
    const navigate = useNavigate();
    const [message, setMessage] = useState("");
    const [subject, setSubject] = useState("");

    const [target, setTarget] = useState<number | "">("");
    const [vendors, setVendors] = useState<Vendor[]>([]);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");

    const [success, setSuccess] = useState(false);
    const [serverError, setServerError] = useState("");
    const [loading, setLoading] = useState(false);

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

    useEffect(() => {
        const fetchVendors = async () => {
            try {
                const data = await getAllVendors();
                if (data && data.vendors) {
                    setVendors(data.vendors);
                } else {
                    setVendors([]);
                }
            } catch (err) {
                console.error("Failed to fetch vendors:", err)
                setServerError("Could not load vendors.")
            }
        };

        fetchVendors();
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

        setLoading(true);

        try  {
            const payload = {
                vendor_id: target,
                title: subject,
                complaint: message
            };

            await api.post("/reports/create", payload)

            setSuccess(true);
            setTimeout(() => {
                navigate("/customer/home")
            }, 2000);
        } catch (err: any) {
            console.error(err);
            setServerError(err.response?.data?.detail || "Submission failed. Please try again.")
        } finally {
            setLoading(false);
        }
    };

    return (
    
        <div className="min-h-screen bg-pattern pb-12 pt-24 px-4 sm:px-6">
            <div className="max-w-3xl mx-auto">

                {/* Header */}
                <div className="text-center mb-10">
                    <h1 className="text-3xl font-extrabold text-[hsl(var(--text-main))] mb-2">
                        Leave Feedback
                    </h1>
                    <p className="text-gray-500">Fill the form below to leave feedback for a vendor.</p>
                </div>

                <div className="bg-white rounded-xl shadow-lg p-6 md:p-8">
                    {success && (
                        <div className="min-h-screen bg-pattern flex items-center justify-center p-4">
                            <div className="bg-white rounded-xl shadow-xl p-8 max-w-md w-full text-center animate-in zoom-in duration-300">
                                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                                    <CheckCircleIcon />
                                </div>
                                <h2 className="text-2xl font-extrabold text-gray-800 mb-2">Feedback submitted successfully.</h2>
                                <div className="animate-pulse text-[hsl(var(--primary))] font-bold">Redirecting...</div>
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
                                    className="w-full text-left px-4 py-2 pr-10 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-[hsl(158,48%,46%)]"
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
                                                className="px-4 py-2 hover:bg-[hsl(158,48%,46%)] hover:text-white cursor-pointer transition-colors"
                                            >
                                                {vendor.name}
                                            </li>
                                        ))
                                    )}
                                </ul>
                            )}
                        </div>

                        {/* Subject Input */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Subject
                            </label>
                            <input
                                type="text"
                                required
                                value={subject}
                                onChange={(e) => setSubject(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-[hsl(158,48%,46%)]"
                                placeholder="Brief summary of your feedback"
                            />
                        </div>

                        {/* Message Input */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Message
                            </label>
                            <textarea
                                required
                                rows={4}
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-[hsl(158,48%,46%)]"
                                placeholder="Please provide your feedback details..."
                            />
                        </div>

                        {serverError && (
                            <div className="mb-4 text-red-600 bg-red-60 p-3 rounded">
                                {serverError}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-[hsl(var(--primary))] text-white font-bold text-lg py-3 rounded shadow-md shadow-green-200 hover:shadow-lg hover:translate-y-[-1px] active:translate-y-[0px] transition-all disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center gap-2"
                        >
                            {loading ? (
                            <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                            ) : (
                            <span>Submit Feedback</span>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}