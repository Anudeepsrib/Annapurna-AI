"use client";

import { useEffect, useState } from "react";

export default function TestBackend() {
    const [data, setData] = useState<{ message: string } | null>(null);
    const [health, setHealth] = useState<{ status: string } | null>(null);

    useEffect(() => {
        // Fetch from root
        fetch("http://localhost:8000/")
            .then((res) => res.json())
            .then((data) => setData(data))
            .catch((err) => console.error("Failed to fetch root:", err));

        // Fetch from health
        fetch("http://localhost:8000/api/health")
            .then((res) => res.json())
            .then((data) => setHealth(data))
            .catch((err) => console.error("Failed to fetch health:", err));
    }, []);

    return (
        <div className="p-10 font-sans">
            <h1 className="text-2xl font-bold mb-4">FastAPI Backend Connection Test</h1>

            <div className="mb-6 p-4 border rounded shadow-sm bg-gray-50 text-black">
                <h2 className="font-semibold mb-2">Root Endpoint (/)</h2>
                {data ? (
                    <pre className="text-green-600">{JSON.stringify(data, null, 2)}</pre>
                ) : (
                    <p className="text-gray-500">Loading or Error...</p>
                )}
            </div>

            <div className="p-4 border rounded shadow-sm bg-gray-50 text-black">
                <h2 className="font-semibold mb-2">Health Endpoint (/api/health)</h2>
                {health ? (
                    <pre className="text-green-600">{JSON.stringify(health, null, 2)}</pre>
                ) : (
                    <p className="text-gray-500">Loading or Error...</p>
                )}
            </div>

            <div className="mt-8 text-sm text-gray-500">
                <p>Make sure the backend is running:</p>
                <code className="block bg-gray-100 p-2 mt-2 rounded">
                    cd backend && .\venv\Scripts\uvicorn main:app --reload
                </code>
            </div>
        </div>
    );
}
