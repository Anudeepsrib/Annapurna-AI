"use client"

import { useEffect, useState } from "react"
import { ApiClient, EvidenceResponse } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, CheckCircle, BookOpen } from "lucide-react"

export function EvidencePanel({ topic = "protein" }: { topic?: string }) {
    const [data, setData] = useState<EvidenceResponse | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true)
            const result = await ApiClient.getEvidence(topic)
            setData(result)
            setLoading(false)
        }
        fetchData()
    }, [topic])

    if (loading) {
        return <div className="p-4 text-center text-muted-foreground text-sm animate-pulse">Consulting Annapurna Intelligence...</div>
    }

    if (!data) return null;

    return (
        <Card className="border-primary/10 bg-primary/5">
            <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg font-serif text-primary">
                    <BookOpen className="h-5 w-5" />
                    Evidence & Guidelines
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex flex-col gap-3">
                    {data.claims.map((claim) => (
                        <div key={claim.id} className="bg-white p-3 rounded-lg border border-border shadow-sm">
                            <div className="flex items-start justify-between gap-2 mb-2">
                                <Badge variant="outline" className="text-[10px] uppercase tracking-wider text-primary border-primary/20 bg-primary/5">
                                    {claim.evidence_type}
                                </Badge>
                                <span className="text-[10px] text-muted-foreground">{claim.citation.source}, {claim.citation.year}</span>
                            </div>
                            <p className="text-sm font-medium text-foreground mb-2">{claim.claim}</p>
                            <div className="text-xs text-muted-foreground bg-muted/30 p-2 rounded">
                                <span className="font-semibold">Context:</span> {claim.population}. <br />
                                {claim.limitations && <span><span className="font-semibold">Note:</span> {claim.limitations}</span>}
                            </div>
                        </div>
                    ))}
                    {data.claims.length === 0 && (
                        <div className="text-sm text-muted-foreground italic">
                            No specific guidelines found for "{topic}". Falling back to general wellness principles.
                        </div>
                    )}
                </div>

                {data.disclaimer && (
                    <div className="flex gap-2 p-3 bg-amber-50 border border-amber-100 rounded-lg text-xs text-amber-800">
                        <AlertCircle className="h-4 w-4 shrink-0" />
                        <p>{data.disclaimer}</p>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
