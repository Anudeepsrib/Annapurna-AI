export function Footer() {
    return (
        <footer className="border-t border-muted bg-muted/30 py-6 md:py-0">
            <div className="container mx-auto flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row px-4">
                <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
                    Built for Andhra Telugu home cooking.
                    <span className="block md:inline ml-1">
                        Respecting tradition, enabling wellness.
                    </span>
                </p>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <p> MVP v0.1 </p>
                </div>
            </div>
        </footer>
    )
}
