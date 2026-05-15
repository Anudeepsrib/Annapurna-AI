"use client"

import { useEffect, useState } from "react"
import { ApiClient } from "@/lib/api"

interface HealthState {
    status: string
    mode: string
    external_network_enabled: boolean
}

export default function TestBackend() {
    const [health, setHealth] = useState<HealthState | null>(null)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        ApiClient.health()
            .then((data) => {
                setHealth(data)
                setError(null)
            })
            .catch(() => setError("Backend health check failed. Start FastAPI on port 8000."))
    }, [])

    return (
        <div className="p-10 font-sans">
            <h1 className="text-2xl font-bold mb-4">FastAPI Backend Connection Test</h1>

            <div className="p-4 border rounded shadow-sm bg-gray-50 text-black">
                <h2 className="font-semibold mb-2">Health Endpoint</h2>
                {health ? (
                    <pre className="text-green-600">{JSON.stringify(health, null, 2)}</pre>
                ) : (
                    <p className="text-gray-500">{error || "Loading..."}</p>
                )}
            </div>

            <div className="mt-8 text-sm text-gray-500">
                <p>Backend command:</p>
                <code className="block bg-gray-100 p-2 mt-2 rounded">
                    cd backend && python -m uvicorn app.main:app --reload
                </code>
            </div>
        </div>
    )
}
