export interface ShortenURLRequest {
  long_url: string;
  custom_alias?: string;
  expires_at?: string;
}

export interface ShortenURLResponse {
  short_url: string;
  short_code: string;
  long_url: string;
  created_at: string;
  expires_at?: string | null;
}

export interface User {
  id: string;
  email: string;
  full_name?: string;
  tier?: string;
}

