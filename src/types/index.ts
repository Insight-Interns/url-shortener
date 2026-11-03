export interface ShortenURLRequest {
  url: string;
  custom_alias?: string;
  topic?: string;
}

export interface ShortenURLResponse {
  short_url: string;
  original_url: string;
  created_at?: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
}

