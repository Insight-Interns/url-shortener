export interface ShortenURLRequest {
  long_url: string;
  custom_alias?: string;
  expires_in_days?: number;
  expires_at?: string;
}

export interface ShortenURLResponse {
  short_url: string;
  short_code: string;
  long_url: string;
  created_at: string;
  expires_at?: string | null;
}

export interface URLHistoryItem extends ShortenURLResponse {
  id?: string;
  click_count?: number;
}

export interface User {
  id: string;
  email: string;
  full_name?: string;
  tier?: string;
}


