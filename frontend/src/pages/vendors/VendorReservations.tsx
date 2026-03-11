import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { VendorReservation } from "../../types";

export default function VendorReservations() {
  const navigate = useNavigate();
  const [reservations, setReservations] = useState<VendorReservation[]>([]);
  const [loading, setLoading] = useState(true);
  const [codes, setCodes] = useState<Record<number, string>>({});
  const [checking, setChecking] = useState<Record<number, boolean>>({});

  useEffect(() => {
    async function fetchReservations() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("/api/reservations/vendor", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) throw new Error("Failed to fetch");

        const data = await res.json();
        setReservations(data.bundles ?? []);
      } catch (err) {
        console.error(err);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    }

    fetchReservations();
  }, [navigate]);

  const handleCheckCode = async (id: number) => {
    try {
      const token = localStorage.getItem("token");
      setChecking(prev => ({ ...prev, [id]: true }));

      const res = await fetch(`/api/reservations/${id}/check`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ pickup_code: parseInt(codes[id]) }),
      });

      if (!res.ok) {
        const data = await res.json();
        alert(data.detail || "Incorrect code");
        return;
      }

      setReservations(prev =>
        prev.map(r =>
          r.reservation_id === id ? { ...r, status: "collected" } : r
        )
      );
    } catch (err) {
      console.error(err);
    } finally {
      setChecking(prev => ({ ...prev, [id]: false }));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  const active = reservations
    .filter(r => r.status === "booked")
    .sort((a, b) =>
      new Date(b.time_created).getTime() -
      new Date(a.time_created).getTime()
    );

  const previous = reservations
    .filter(r => r.status !== "booked")
    .sort((a, b) =>
      new Date(b.time_created).getTime() -
      new Date(a.time_created).getTime()
    );

  return (
    <div className="min-h-screen bg-pattern pb-20">
      <div className="max-w-5xl mx-auto px-6 pt-10">

        <h1 className="text-3xl font-bold mb-10">Vendor Reservations</h1>

        {active.length > 0 && (
          <>
            <h2 className="text-xl font-semibold mb-6">Active</h2>
            <div className="grid gap-6 mb-12">
              {active.map(r => (
                <div
                  key={r.reservation_id}
                  className="bg-white rounded-2xl shadow-sm border p-6"
                >
                  <div className="mb-2 text-sm text-gray-500">
                    Reservation ID: {r.reservation_id}
                  </div>

                  <div className="text-sm text-gray-500 mb-2">
                    Customer ID: {r.customer_id}
                  </div>

                  <div className="text-sm text-gray-500 mb-4">
                    Created: {new Date(r.time_created).toLocaleString()}
                  </div>

                  <div className="flex gap-3 items-center">
                    <input
                      type="number"
                      placeholder="Enter pickup code"
                      value={codes[r.reservation_id] ?? ""}
                      onChange={e =>
                        setCodes(prev => ({
                          ...prev,
                          [r.reservation_id]: e.target.value,
                        }))
                      }
                      className="border px-3 py-2 rounded-lg w-40"
                    />

                    <button
                      onClick={() => handleCheckCode(r.reservation_id)}
                      disabled={checking[r.reservation_id]}
                      className="px-4 py-2 rounded-lg bg-green-500 text-white font-semibold hover:bg-green-600 transition"
                    >
                      {checking[r.reservation_id]
                        ? "Checking..."
                        : "Mark Collected"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {previous.length > 0 && (
          <>
            <h2 className="text-xl font-semibold mb-6 text-gray-400">
              Previous
            </h2>

            <div className="grid gap-6">
              {previous.map(r => (
                <div
                  key={r.reservation_id}
                  className="bg-white rounded-2xl shadow-sm border p-6 opacity-70"
                >
                  <div className="mb-2 text-sm text-gray-500">
                    Reservation ID: {r.reservation_id}
                  </div>

                  <div className="text-sm text-gray-500 mb-2">
                    Customer ID: {r.customer_id}
                  </div>

                  <div className="text-sm text-gray-500 mb-2">
                    Created: {new Date(r.time_created).toLocaleString()}
                  </div>

                  <div className="text-xs uppercase tracking-wider text-gray-400">
                    {r.status}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {reservations.length === 0 && (
          <div className="text-center text-gray-500 py-20">
            No reservations yet.
          </div>
        )}
      </div>
    </div>
  );
}