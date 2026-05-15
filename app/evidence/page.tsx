import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

export default function EvidencePage() {
    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 py-10 bg-muted/20">
                <div className="container mx-auto max-w-[800px]">
                    <div className="mb-8 text-center space-y-2">
                        <h1 className="font-serif text-3xl font-bold">The Science Behind the Menu</h1>
                        <p className="text-muted-foreground">
                            Annapurna shows general wellness references where local curated data exists.
                            Optional online literature search stays disabled unless you enable it.
                        </p>
                    </div>

                    <Card>
                        <CardHeader>
                            <CardTitle>Core Principles</CardTitle>
                            <CardDescription>
                                Why we recommend what we recommend.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Accordion type="single" collapsible className="w-full">
                                <AccordionItem value="item-1">
                                    <AccordionTrigger className="font-serif text-lg text-primary">Protein Complementation</AccordionTrigger>
                                    <AccordionContent className="text-muted-foreground leading-relaxed">
                                        Vegetarian diets often need careful pairing to achieve a complete amino acid profile.
                                        Combining cereals (rice, wheat) with pulses (dal, beans) creates a complete protein.
                                        Annapurna favors familiar cereal-and-pulse pairings such as rice with dal.
                                        <br />
                                        <span className="text-xs mt-2 block font-semibold text-foreground">Source: National Institute of Nutrition (NIN) - Dietary Guidelines for Indians</span>
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-2">
                                    <AccordionTrigger className="font-serif text-lg text-primary">Fermented Foods (Probiotics)</AccordionTrigger>
                                    <AccordionContent className="text-muted-foreground leading-relaxed">
                                        South Indian breakfasts like idli and dosa use natural fermentation and familiar pantry staples.
                                        <br />
                                        <span className="text-xs mt-2 block font-semibold text-foreground">Source status: general culinary context</span>
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-3">
                                    <AccordionTrigger className="font-serif text-lg text-primary">Iron Absorption</AccordionTrigger>
                                    <AccordionContent className="text-muted-foreground leading-relaxed">
                                        Greens, tomato, lemon, and tamarind can be useful variety in vegetarian meals.
                                        This is general food-planning context, not a treatment recommendation.
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-4">
                                    <AccordionTrigger className="font-serif text-lg text-primary">Seasonal Eating (Rutucharya)</AccordionTrigger>
                                    <AccordionContent className="text-muted-foreground leading-relaxed">
                                        Seasonal vegetables help keep the grocery list practical and culturally familiar.
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        </CardContent>
                    </Card>
                </div>
            </main>
            <Footer />
        </div>
    )
}
