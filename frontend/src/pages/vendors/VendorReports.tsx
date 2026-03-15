import { useState, useEffect } from "react";
import { getReportList, submitReportResponse } from "../../api/reports";
import type { Report } from "../../types";

export default function VendorReports() {
    const [reports, setReports] = useState<Report[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    
    const [replyingToId, setReplyingToId] = useState<number | null>(null);
    const [replyText, setReplyText] = useState("");
    const [submittingId, setSubmittingId] = useState<number | null>(null);
    const [replyError, setReplyError] = useState("");

    useEffect(() => {
        const fetchReports = async () => {
            try {
                const data = await getReportList();
                setReports(data.reports || []);
            } catch (err) {
                console.error("Failed to load reports:", err);
                setError("Could not load reports.");
            } finally {
                setLoading(false);
            }
        };
        fetchReports();
    }, []);

    const handleReplySubmit = async (reportId: number) => {
        setReplyError("");
        if (replyText.length < 10) {
            setReplyError("Your response must be at least 10 characters long.");
            return;
        }
        
        setSubmittingId(reportId);
        try {
            await submitReportResponse(reportId, replyText);
            
            setReports(prevReports => 
                prevReports.map(report => 
                    report.report_id === reportId 
                        ? { ...report, responded: true, response: replyText } 
                        : report
                )
            );
            
            setReplyingToId(null);
            setReplyText("");
        } catch (err: any) {
            console.error("Failed to submit reply:", err);
            setReplyError(err.response?.data?.detail || "Failed to send reply.");
        } finally {
            setSubmittingId(null);
        }
    };

    // sorts reports by whether they have been responded to
    const sortedReports = [...reports].sort((a, b) => {
        if (a.responded === b.responded) return 0;
        return a.responded ? 1 : -1; 
    });

    if (loading) {
        return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="animate-spin w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full" />
        </div>
        );
    }

    return (
        <div className="min-h-screen pb-12 pt-24 px-4 sm:px-6">
            <div className="max-w-4xl mx-auto">
                {/* Header Text */}
                <div className="text-center mb-10">
                    <h1 className="text-3xl font-extrabold text-[hsl(var(--text-main))] mb-2">
                        Customer Feedback
                    </h1>
                    <p className="text-gray-500">Read and reply to concerns and feedback reported by customers.</p>
                </div>

                {error && <div className="bg-red-50 text-red-600 p-4 rounded-md mb-6 shadow-sm border border-red-100">{error}</div>}

                {reports.length === 0 && !loading && (
                    <div className="text-center bg-white rounded-xl shadow-sm p-12 text-gray-500 border border-gray-100">
                        No reports found. You're all caught up!
                    </div>
                )}

                {/* Display list of all reports */}
                <div className="space-y-6">
                    {sortedReports.map((report) => (
                        <div key={report.report_id} className={`bg-white rounded-xl shadow-sm overflow-hidden border-l-4 transition-all hover:shadow-md ${!report.responded ? "border-yellow-400" : "border-green-500"}`}>
                            <div className="p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="text-xl font-bold text-gray-900">{report.title}</h3>
                                        <span className={`inline-block mt-2 text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wide ${!report.responded ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}`}>
                                            {!report.responded ? "Action Required" : "Resolved"}
                                        </span>
                                    </div>
                                    <div className="text-sm text-gray-400 font-mono">ID: #{report.report_id}</div>
                                </div>
                                
                                <div className="bg-gray-50 p-4 rounded-md border border-gray-100 mb-6">
                                    <p className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">Customer Wrote:</p>
                                    <p className="text-gray-800 italic">"{report.complaint}"</p>
                                </div>

                                {!report.responded && replyingToId !== report.report_id && (
                                    <button 
                                        onClick={() => {
                                            setReplyingToId(report.report_id);
                                            setReplyError("");
                                        }}
                                        className="text-[hsl(var(--primary))] font-bold hover:underline flex items-center gap-2"
                                    >
                                        Write a response &rarr;
                                    </button>
                                )}

                                {replyingToId === report.report_id && (
                                    <div className="mt-4 border-t pt-5">
                                        <label className="block text-sm font-bold text-gray-700 mb-2">Your Reply</label>
                                        <textarea 
                                            rows={3}
                                            value={replyText}
                                            onChange={(e) => setReplyText(e.target.value)}
                                            className="w-full px-4 py-2 mb-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-[hsl(158,48%,46%)]"
                                            placeholder="Write your response here (minimum 10 characters)..."
                                        />
                                        
                                        {replyError && <p className="text-red-500 text-sm mb-3 font-medium">{replyError}</p>}
                                        
                                        <div className="flex gap-3">
                                            <button 
                                                onClick={() => handleReplySubmit(report.report_id)}
                                                disabled={submittingId === report.report_id || replyText.length < 10}
                                                className="bg-[hsl(var(--primary))] text-white px-5 py-2.5 rounded-md font-bold hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                                            >
                                                {submittingId === report.report_id ? "Sending..." : "Send Reply"}
                                            </button>
                                            <button 
                                                onClick={() => { setReplyingToId(null); setReplyText(""); setReplyError(""); }}
                                                className="text-gray-500 hover:text-gray-800 font-bold px-4 py-2"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {report.responded && report.response && (
                                    <div className="mt-2 border border-gray-300 p-4 rounded-md">
                                        <h4 className="text-xs font-bold text-[hsl(var(--primary))] uppercase tracking-wider mb-2">You Replied:</h4>
                                        <p className="text-gray-900">{report.response}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}