import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Reservation } from "../../types";

export default function CustomerReservations() {
  const navigate = useNavigate();
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchReservations() {
      try {
        const token = localStorage.getItem("token");

        const res = await fetch("/api/reservations/customer", {
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

  const handleCancel = async (id: number) => {
    try {
      const token = localStorage.getItem("token");

      const res = await fetch(`/api/reservations/${id}/cancel`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error("Cancel failed");

      setReservations(prev =>
        prev.map(r =>
          r.reservation_id === id ? { ...r, status: "cancelled" } : r
        )
      );
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full" />
      </div>
    );
  }

    const today = new Date();
    today.setHours(0, 0, 0, 0); 

    const active = reservations.filter(r => {
        if (r.status !== "booked") return false;
        const createdDate = new Date(r.time_created);
        createdDate.setHours(0, 0, 0, 0);
        return createdDate.getTime() === today.getTime();
    });

    const previous = reservations.filter(r => !active.includes(r));

  return (
    <div className="min-h-screen bg-pattern pb-20">
      <div className="max-w-5xl mx-auto px-6 pt-10">

        <h1 className="text-3xl font-bold mb-10">My Reservations</h1>

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

                  <div className="text-2xl font-bold text-green-600 mb-4">
                    Pickup Code: {r.code}
                  </div>

                  <div className="text-sm text-gray-500 mb-4">
                    Created: {new Date(r.time_created).toLocaleString()}
                  </div>

                  <button
                    onClick={() => handleCancel(r.reservation_id)}
                    className="px-4 py-2 rounded-lg bg-red-50 text-red-600 font-semibold hover:bg-red-100 transition"
                  >
                    Cancel Reservation
                  </button>
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

                  <div className="text-lg font-bold mb-2">
                    Code: {r.code}
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
            You have no reservations.
          </div>
        )}
      </div>
    </div>
  );
}