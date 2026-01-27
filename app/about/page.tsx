import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Card, CardContent } from "@/components/ui/card"
import { ShieldCheck, Heart, Leaf } from "lucide-react"

export default function AboutPage() {
    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 py-10 bg-muted/20">
                <div className="container mx-auto max-w-[800px] space-y-8">
                    <div className="text-center space-y-4">
                        <h1 className="font-serif text-4xl font-bold">About Annapurna</h1>
                        <p className="text-xl text-muted-foreground font-serif italic">
                            "Food is medicine, when eaten with mindfulness."
                        </p>
                    </div>

                    <div className="grid gap-6 md:grid-cols-2">
                        <Card>
                            <CardContent className="pt-6 space-y-4">
                                <Heart className="h-8 w-8 text-primary" />
                                <h3 className="font-serif text-xl font-bold">Our Mission</h3>
                                <p className="text-muted-foreground">
                                    To help Indian home cooks plan authentic, nutritious meals without the stress.
                                    We believe technology should support tradition, not replace it.
                                </p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="pt-6 space-y-4">
                                <Leaf className="h-8 w-8 text-accent" />
                                <h3 className="font-serif text-xl font-bold">Cultural Integrity</h3>
                                <p className="text-muted-foreground">
                                    We focus specifically on South Indian Vegetarian cuisine, respecting the flavors,
                                    pairings, and wisdom of Andhra cooking.
                                </p>
                            </CardContent>
                        </Card>
                    </div>

                    <Card className="border-secondary/20 bg-secondary/5">
                        <CardContent className="pt-6 flex gap-4">
                            <ShieldCheck className="h-10 w-10 text-secondary shrink-0" />
                            <div className="space-y-2">
                                <h3 className="font-serif text-lg font-bold">Safety Disclaimer</h3>
                                <p className="text-sm text-muted-foreground leading-relaxed">
                                    Annapurna provides general wellness and educational information only.
                                    It does not provide medical advice, diagnosis, or treatment.
                                    Always consult a qualified healthcare professional regarding any medical condition
                                    or dietary changes. The meal plans are generated suggestions and should be reviewed
                                    for your personal allergies and needs.
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </main>
            <Footer />
        </div>
    )
}
