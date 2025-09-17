/**
 * Application settings management
 */

'use client'

import React, { useState, useEffect } from 'react'

export interface AppSettings {
  theme: 'light' | 'dark' | 'auto'
  language: 'ru' | 'en'
  notifications: {
    enabled: boolean
    sound: boolean
    vibration: boolean
  }
  qrScanner: {
    autoFocus: boolean
    showOverlay: boolean
    flashMode: 'auto' | 'on' | 'off'
  }
  api: {
    baseUrl: string
    timeout: number
    retryAttempts: number
  }
  cache: {
    enabled: boolean
    ttl: number
  }
  analytics: {
    enabled: boolean
    trackErrors: boolean
    trackPerformance: boolean
  }
}

const defaultSettings: AppSettings = {
  theme: 'light',
  language: 'ru',
  notifications: {
    enabled: true,
    sound: true,
    vibration: true,
  },
  qrScanner: {
    autoFocus: true,
    showOverlay: true,
    flashMode: 'auto',
  },
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    timeout: 10000,
    retryAttempts: 3,
  },
  cache: {
    enabled: true,
    ttl: 15 * 60 * 1000,
  },
  analytics: {
    enabled: true,
    trackErrors: true,
    trackPerformance: true,
  },
}

export class SettingsManager {
  private settings: AppSettings
  private listeners: Array<(settings: AppSettings) => void> = []

  constructor() {
    this.settings = this.loadSettings()
  }

  private loadSettings(): AppSettings {
    if (typeof window === 'undefined') {
      return defaultSettings
    }

    try {
      const stored = localStorage.getItem('pte_qr_settings')
      if (stored) {
        const parsed = JSON.parse(stored)
        return { ...defaultSettings, ...parsed }
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
    }

    return defaultSettings
  }

  private saveSettings(): void {
    if (typeof window === 'undefined') return

    try {
      localStorage.setItem('pte_qr_settings', JSON.stringify(this.settings))
    } catch (error) {
      console.error('Failed to save settings:', error)
    }
  }

  getSettings(): AppSettings {
    return { ...this.settings }
  }

  updateSettings(updates: Partial<AppSettings>): void {
    this.settings = { ...this.settings, ...updates }
    this.saveSettings()
    this.notifyListeners()
  }

  resetSettings(): void {
    this.settings = { ...defaultSettings }
    this.saveSettings()
    this.notifyListeners()
  }

  subscribe(listener: (settings: AppSettings) => void): () => void {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener)
    }
  }

  private notifyListeners(): void {
    this.listeners.forEach((listener) => listener(this.getSettings()))
  }

  get<K extends keyof AppSettings>(key: K): AppSettings[K] {
    return this.settings[key]
  }

  set<K extends keyof AppSettings>(key: K, value: AppSettings[K]): void {
    this.updateSettings({ [key]: value } as Partial<AppSettings>)
  }
}

export const settingsManager = new SettingsManager()

export const settings = {
  get: <K extends keyof AppSettings>(key: K) => settingsManager.get(key),
  set: <K extends keyof AppSettings>(key: K, value: AppSettings[K]) =>
    settingsManager.set(key, value),
  getAll: () => settingsManager.getSettings(),
  update: (updates: Partial<AppSettings>) =>
    settingsManager.updateSettings(updates),
  reset: () => settingsManager.resetSettings(),
  subscribe: (listener: (settings: AppSettings) => void) =>
    settingsManager.subscribe(listener),
}

export function useSettings() {
  const [settings, setSettings] = useState(settingsManager.getSettings())

  useEffect(() => {
    const unsubscribe = settingsManager.subscribe(setSettings)
    return unsubscribe
  }, [])

  return {
    settings,
    update: (updates: Partial<AppSettings>) =>
      settingsManager.updateSettings(updates),
    reset: () => settingsManager.resetSettings(),
  }
}

export function getSettings(): AppSettings {
  const stored = localStorage.getItem('pte_qr_settings')
  if (stored) {
    try {
      return JSON.parse(stored)
    } catch {
      return defaultSettings
    }
  }
  return defaultSettings
}

export function setSettings(settings: AppSettings): void {
  localStorage.setItem('pte_qr_settings', JSON.stringify(settings))
}

export function resetSettings(): void {
  localStorage.removeItem('pte_qr_settings')
}

export function updateSetting(key: string, value: any): void {
  const settings = getSettings()
  ;(settings as any)[key] = value
  setSettings(settings)
}

export function getSetting(key: string): any {
  const settings = getSettings()
  return (settings as any)[key]
}

export function hasSetting(key: string): boolean {
  const settings = getSettings()
  return key in settings
}

export function removeSetting(key: string): void {
  const settings = getSettings()
  delete (settings as any)[key]
  setSettings(settings)
}

export function clearSettings(): void {
  localStorage.clear()
}

export function exportSettings(): string {
  return JSON.stringify(getSettings(), null, 2)
}

export function importSettings(settingsJson: string): void {
  try {
    const settings = JSON.parse(settingsJson)
    setSettings(settings)
  } catch (error) {
    console.error('Failed to import settings:', error)
  }
}
