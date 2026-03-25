import { API_BASE_URL } from '@/lib/utils/constants';

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number>;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private buildUrl(endpoint: string, params?: Record<string, string | number>): string {
    let url: string;

    // 处理相对路径和绝对路径的情况
    if (this.baseUrl.startsWith('http://') || this.baseUrl.startsWith('https://')) {
      // 绝对 URL，正常使用 URL 构造函数
      const urlObj = new URL(endpoint.replace(/^\//, ''), this.baseUrl);
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          urlObj.searchParams.append(key, String(value));
        });
      }
      url = urlObj.toString();
    } else {
      // 相对路径（浏览器环境），手动拼接
      const basePath = this.baseUrl.replace(/\/$/, '');
      const endpointPath = endpoint.replace(/^\//, '');
      url = basePath ? `${basePath}/${endpointPath}` : `/${endpointPath}`;

      // 添加查询参数
      if (params && Object.keys(params).length > 0) {
        const searchParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
          searchParams.append(key, String(value));
        });
        url += `?${searchParams.toString()}`;
      }
    }

    return url;
  }

  private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { params, ...init } = options;
    const url = this.buildUrl(endpoint, params);

    const headers = new Headers(init.headers);
    if (!(init.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(url, {
      ...init,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }

    return {} as T;
  }

  async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async patch<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
