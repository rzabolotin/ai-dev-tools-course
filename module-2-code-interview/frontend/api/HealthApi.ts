import { BaseApi } from './base/BaseApi'
import type { HealthStatus } from './types'

/**
 * API class for health checks
 */
export class HealthApi extends BaseApi {
  /**
   * Check API health status
   */
  async check(): Promise<HealthStatus> {
    return this.get<HealthStatus>('/health')
  }
}
