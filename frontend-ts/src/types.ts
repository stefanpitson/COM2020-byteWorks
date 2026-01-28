export type Token = string;

export interface Customer {
  id: number;
  name: string;
  email: string;
  postCode: string;
  storeCredit: number;
  carbonSaved: number
  rating: number;
}

export interface Seller {
  id: number
  name: string;
  email: string;
  address: string;
  phoneNumber: string;
  carbonSaved: number;
}

export interface TemplateBundle {
  id: number;
  estimatedValue: number;
  cost: number;
  title: string;
  description: string;
  estCarbonSaved: number;
}

export interface Bundle {
  id: number;
  templateID: number;
  pickedIp: boolean;
  date: Date;
}

