/**
 * Analytics and tracking utilities
 */

'use client';

import React, { useState, useEffect } from 'react';

export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
  timestamp: number;
  userId?: string;
  sessionId: string;
}

export class AnalyticsManager {
  private sessionId: string;
  private userId?: string;
  private events: AnalyticsEvent[] = [];
  private isEnabled: boolean = true;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.loadUserId();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private loadUserId(): void {
    if (typeof window !== 'undefined') {
      this.userId = localStorage.getItem('pte_qr_user_id') || undefined;
    }
  }

  setUserId(userId: string): void {
    this.userId = userId;
    if (typeof window !== 'undefined') {
      localStorage.setItem('pte_qr_user_id', userId);
    }
  }

  clearUserId(): void {
    this.userId = undefined;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('pte_qr_user_id');
    }
  }

  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  track(event: Omit<AnalyticsEvent, 'timestamp' | 'sessionId' | 'userId'>): void {
    if (!this.isEnabled) return;

    const analyticsEvent: AnalyticsEvent = {
      ...event,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      userId: this.userId,
    };

    this.events.push(analyticsEvent);
    this.sendEvent(analyticsEvent);
  }

  private async sendEvent(event: AnalyticsEvent): Promise<void> {
    try {
      console.log('Analytics Event:', event);
      // Send to analytics service
    } catch (error) {
      console.error('Failed to send analytics event:', error);
    }
  }

  getEvents(): AnalyticsEvent[] {
    return [...this.events];
  }

  clearEvents(): void {
    this.events = [];
  }

  getSessionId(): string {
    return this.sessionId;
  }

  getUserId(): string | undefined {
    return this.userId;
  }
}

export const analytics = new AnalyticsManager();

export const track = {
  qrScan: (properties: any) => analytics.track({ name: 'qr_scan', properties }),
  documentStatus: (properties: any) => analytics.track({ name: 'document_status_check', properties }),
  error: (properties: any) => analytics.track({ name: 'error', properties }),
  pageView: (page: string) => analytics.track({ name: 'page_view', properties: { page } }),
  buttonClick: (button: string, context?: string) => 
    analytics.track({ name: 'button_click', properties: { button, context } }),
  apiCall: (endpoint: string, method: string, success: boolean, responseTime: number) =>
    analytics.track({ name: 'api_call', properties: { endpoint, method, success, responseTime } }),
};

export function useAnalytics() {
  const [events, setEvents] = useState(analytics.getEvents());

  useEffect(() => {
    const interval = setInterval(() => {
      setEvents(analytics.getEvents());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return {
    events,
    track: (event: Omit<AnalyticsEvent, 'timestamp' | 'sessionId' | 'userId'>) => 
      analytics.track(event),
    setUserId: (userId: string) => analytics.setUserId(userId),
    clearUserId: () => analytics.clearUserId(),
    setEnabled: (enabled: boolean) => analytics.setEnabled(enabled),
  };
}