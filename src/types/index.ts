export * from './atoms'
export * from './slides'

/**
 * API Response Types
 */
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

/**
 * WebSocket Message Types
 */
export interface WSMessage {
  type: 'atom_executed' | 'prediction' | 'sync' | 'error'
  data: any
  timestamp: number
}

/**
 * User Session
 */
export interface UserSession {
  id: string
  userId: string
  startTime: number
  endTime?: number
  operations: number
  presentationId: string
}

/**
 * AI Model Response
 */
export interface AIModelResponse {
  prediction: any
  confidence: number
  reasoning: string
  alternatives: any[]
  processingTime: number
}