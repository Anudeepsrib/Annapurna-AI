"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { toast } from "sonner"
import { Loader2, Check, AlertCircle, Database, Server, Globe, Shield } from "lucide-react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { ApiClient, ApiError, type SettingsResponse } from "@/lib/api"

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [testingConnection, setTestingConnection] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<"idle" | "success" | "error">("idle")
  const [availableModels, setAvailableModels] = useState<string[]>([])
  const [loadingModels, setLoadingModels] = useState(false)

  useEffect(() => {
    fetchSettings()
  }, [])

  async function fetchSettings() {
    try {
      const data = await ApiClient.getSettings()
      setSettings(data)
    } catch {
      toast.error("Error connecting to backend")
    } finally {
      setLoading(false)
    }
  }

  async function testLLMConnection() {
    setTestingConnection(true)
    setConnectionStatus("idle")
    try {
      await ApiClient.testLLM()
      setConnectionStatus("success")
      toast.success("LLM connection successful!")
    } catch (error) {
      setConnectionStatus("error")
      const message = error instanceof ApiError ? error.message : "Could not connect to LLM endpoint"
      toast.error(message)
    } finally {
      setTestingConnection(false)
    }
  }

  async function fetchAvailableModels() {
    setLoadingModels(true)
    try {
      const data = await ApiClient.listModels()
      setAvailableModels(data.models || [])
      if (data.error) {
        toast.warning(data.error)
      } else if (data.models?.length > 0) {
        toast.success(`Found ${data.models.length} models`)
      } else {
        toast.info("No models found. Is Ollama running?")
      }
    } catch {
      toast.error("Failed to fetch models")
    } finally {
      setLoadingModels(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </main>
        <Footer />
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container mx-auto py-8 px-4 max-w-4xl">
        <div className="space-y-6">
          {/* Privacy Banner */}
          <div className="rounded-lg bg-green-50 border border-green-200 p-4">
            <div className="flex items-start gap-3">
              <Shield className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-green-900">Your data stays on your computer</h3>
                <p className="text-sm text-green-700 mt-1">
                  Annapurna-AI stores meal plans and preferences in local SQLite by default. USDA and PubMed lookups are optional, disabled by default, and require explicit environment settings.
                </p>
              </div>
            </div>
          </div>

          {/* LLM Configuration */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Server className="h-5 w-5 text-primary" />
                <CardTitle>LLM Configuration</CardTitle>
              </div>
              <CardDescription>
                Configure your local LLM endpoint. Default is Ollama at localhost:11434.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="provider">Provider</Label>
                  <Select value={settings?.llm_provider} disabled>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ollama">Ollama</SelectItem>
                      <SelectItem value="lmstudio">LM Studio</SelectItem>
                      <SelectItem value="llamacpp">llama.cpp</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="model">Model Name</Label>
                  <Input id="model" value={settings?.llm_model} disabled />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="baseUrl">Endpoint URL</Label>
                <Input id="baseUrl" value={settings?.llm_base_url} disabled />
                <p className="text-xs text-muted-foreground">
                  Edit via environment variables or .env file to change these values
                </p>
              </div>

              <div className="flex gap-2 pt-2">
                <Button
                  onClick={testLLMConnection}
                  disabled={testingConnection}
                  variant="outline"
                >
                  {testingConnection && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {connectionStatus === "success" && <Check className="mr-2 h-4 w-4 text-green-500" />}
                  {connectionStatus === "error" && <AlertCircle className="mr-2 h-4 w-4 text-red-500" />}
                  Test Connection
                </Button>
                <Button
                  onClick={fetchAvailableModels}
                  disabled={loadingModels}
                  variant="outline"
                >
                  {loadingModels && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  List Available Models
                </Button>
              </div>

              {availableModels.length > 0 && (
                <div className="rounded-md bg-muted p-3">
                  <p className="text-sm font-medium mb-2">Available Models:</p>
                  <ul className="text-sm space-y-1">
                    {availableModels.map((model) => (
                      <li key={model} className="text-muted-foreground">{model}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="rounded-md bg-blue-50 p-3 text-sm text-blue-700">
                <p className="font-medium">Model Recommendations:</p>
                <ul className="mt-1 list-disc list-inside space-y-1">
                  <li>Llama 3.2 3B (~2GB) - Good for structured meal plans</li>
                  <li>Llama 3.2 7B (~4GB) - Very good quality</li>
                  <li>Mistral 7B (~4GB) - Excellent for this task</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Data & Storage */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Database className="h-5 w-5 text-primary" />
                <CardTitle>Data & Storage</CardTitle>
              </div>
              <CardDescription>
                Your data is stored locally in a SQLite database file.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Database Location</Label>
                <code className="block rounded bg-muted p-2 text-sm">
                  {settings?.database_url}
                </code>
                <p className="text-xs text-muted-foreground">
                  To back up your data, simply copy this file. To reset, delete it and restart the app.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Optional Online Features */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-primary" />
                <CardTitle>Optional Online Features</CardTitle>
              </div>
              <CardDescription>
                These features require internet connection and are disabled by default for privacy.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="external-network">External Network Access</Label>
                  <p className="text-xs text-muted-foreground">
                    Master switch required before optional online fetchers can run.
                  </p>
                </div>
                <Switch
                  id="external-network"
                  checked={settings?.enable_external_network}
                  disabled
                />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="usda">USDA Nutrition Lookups</Label>
                  <p className="text-xs text-muted-foreground">
                    Requires external network access and a USDA API key.
                  </p>
                </div>
                <Switch
                  id="usda"
                  checked={settings?.enable_usda}
                  disabled
                />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="pubmed">PubMed Evidence Search</Label>
                  <p className="text-xs text-muted-foreground">
                    Searches PubMed abstracts when external network access is explicitly enabled.
                  </p>
                </div>
                <Switch
                  id="pubmed"
                  checked={settings?.enable_pubmed}
                  disabled
                />
              </div>

              <div className="rounded-md bg-amber-50 p-3 text-sm text-amber-700">
                <p>
                  <strong>Note:</strong> To enable these features, edit your <code>.env</code> file and restart the application.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Quick Start Guide */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Start Guide</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <ol className="list-decimal list-inside space-y-2 text-sm">
                <li>
                  <strong>Install Ollama:</strong>{" "}
                  <a
                    href="https://ollama.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary underline"
                  >
                    Download from ollama.com
                  </a>
                </li>
                <li>
                  <strong>Pull a model:</strong>{" "}
                  <code className="bg-muted px-1 rounded">ollama pull llama3.2:latest</code>
                </li>
                <li>
                  <strong>Start Ollama:</strong> It runs automatically in the background
                </li>
                <li>
                  <strong>Test the connection:</strong> Use the Test Connection button above
                </li>
              </ol>
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  )
}
