import { $fetch, type FetchOptions } from 'ofetch'
import type { ApiError, RequestConfig } from '../types'

/**
 * Base API class that handles all HTTP requests
 * All API classes should extend this class
 */
export abstract class BaseApi {
  protected baseURL: string
  protected defaultHeaders: Record<string, string>

  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  }

  /**
   * Build full URL with base URL and path
   */
  protected buildUrl(path: string): string {
    // Remove leading slash from path if present
    const cleanPath = path.startsWith('/') ? path.slice(1) : path
    // Remove trailing slash from baseURL if present
    const cleanBase = this.baseURL.endsWith('/')
      ? this.baseURL.slice(0, -1)
      : this.baseURL

    return `${cleanBase}/${cleanPath}`
  }

  /**
   * Merge headers with defaults
   */
  protected mergeHeaders(customHeaders?: Record<string, string>): Record<string, string> {
    return {
      ...this.defaultHeaders,
      ...customHeaders
    }
  }

  /**
   * Handle API errors
   */
  protected handleError(error: any): never {
    const apiError: ApiError = {
      message: error?.data?.message || error?.message || 'Unknown error occurred',
      code: error?.status || error?.statusCode,
      details: error?.data
    }

    console.error('API Error:', apiError)
    throw apiError
  }

  /**
   * Generic GET request
   */
  protected async get<T = any>(
    path: string,
    config?: RequestConfig
  ): Promise<T> {
    try {
      const url = this.buildUrl(path)
      const options: FetchOptions = {
        method: 'GET',
        headers: this.mergeHeaders(config?.headers),
        query: config?.query,
        timeout: config?.timeout
      }

      return await $fetch<T>(url, options)
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * Generic POST request
   */
  protected async post<T = any>(
    path: string,
    body?: any,
    config?: RequestConfig
  ): Promise<T> {
    try {
      const url = this.buildUrl(path)
      const options: FetchOptions = {
        method: 'POST',
        headers: this.mergeHeaders(config?.headers),
        body: body,
        query: config?.query,
        timeout: config?.timeout
      }

      return await $fetch<T>(url, options)
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * Generic PUT request
   */
  protected async put<T = any>(
    path: string,
    body?: any,
    config?: RequestConfig
  ): Promise<T> {
    try {
      const url = this.buildUrl(path)
      const options: FetchOptions = {
        method: 'PUT',
        headers: this.mergeHeaders(config?.headers),
        body: body,
        query: config?.query,
        timeout: config?.timeout
      }

      return await $fetch<T>(url, options)
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * Generic DELETE request
   */
  protected async delete<T = any>(
    path: string,
    config?: RequestConfig
  ): Promise<T> {
    try {
      const url = this.buildUrl(path)
      const options: FetchOptions = {
        method: 'DELETE',
        headers: this.mergeHeaders(config?.headers),
        query: config?.query,
        timeout: config?.timeout
      }

      return await $fetch<T>(url, options)
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * Generic PATCH request
   */
  protected async patch<T = any>(
    path: string,
    body?: any,
    config?: RequestConfig
  ): Promise<T> {
    try {
      const url = this.buildUrl(path)
      const options: FetchOptions = {
        method: 'PATCH',
        headers: this.mergeHeaders(config?.headers),
        body: body,
        query: config?.query,
        timeout: config?.timeout
      }

      return await $fetch<T>(url, options)
    } catch (error) {
      return this.handleError(error)
    }
  }
}
