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
                            Our recommendations are grounded in nutritional science and traditional wisdom.
                            We believe in transparency, not "magic" algorithms.
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
                                        This is why our menu always pairs Rice with Dal (Pappu) or Khichdi.
                                        <br />
                                        <span className="text-xs mt-2 block font-semibold text-foreground">Source: National Institute of Nutrition (NIN) - Dietary Guidelines for Indians</span>
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-2">
                                    <AccordionTrigger className="font-serif text-lg text-primary">Fermented Foods (Probiotics)</AccordionTrigger>
                                    <AccordionContent className="text-muted-foreground leading-relaxed">
                                        South Indian breakfasts like Idli and Dosa utilize natural fermentation, which enhances
                                        bioavailability of nutrients (especially B vitamins) and promotes gut health.
                                        <br />
                                        <span className="text-xs mt-2 block font-semibold text-foreground">Source: Journal of Ethnic Foods</span>
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-3">
                                    <AccordionTrigger className="font-serif text-lg text-primary">Iron Absorption</AccordionTrigger>
                                    <AccordionContent className="text-muted-foreground leading-relaxed">
                                        We pair iron-rich greens (Palakura, Thotakura) with Vitamin C sources (Tomato, Lemon, Tamarind)
                                        to maximize non-heme iron absorption, crucial for vegetarian diets.
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="item-4">
                                    <AccordionTrigger className="font-serif text-lg text-primary">Seasonal Eating (Rutucharya)</AccordionTrigger>
                                    <AccordionContent className="text-muted-foreground leading-relaxed">
                                        Following Ayurvedic principles of Rutucharya, we prioritize local, seasonal vegetables
                                        (Bottle Gourd in summer, Root veggies in winter) to align with natural digestion cycles.
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
