export type Token = string;

export interface User {
  id?: number;
  name: string;
  email: string;
  role?: "Client" | "Business"
}

export interface Package {
  id: number;
}

