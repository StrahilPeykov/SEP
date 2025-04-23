// Self-assessment form data
export interface SelfAssessmentFormData {
  companyName: string;
  industrySector: string;
  employeeCount: string;
  location: string;
  annualRevenue?: string;
  hasEnvironmentalPolicy: boolean;
}

// Manufacturing data form
export interface ManufacturingFormData {
  productType: string;
  annualProduction: number;
  electricityConsumption: number;
  electricityRenewablePercentage: number;
  fuelConsumption: number;
  fuelType: string;
  waterConsumption: number;
  wasteProduction: number;
  recycledWastePercentage: number;
}

// Supplier data
export interface SupplierData {
  id: string;
  name: string;
  component: string;
  sharesCO2Data: boolean;
  dataFormat?: string;
  carbonFootprint?: number;
  carbonFootprintUnit?: string;
  useEstimates: boolean;
}

// Supply chain form data
export interface SupplyChainFormData {
  hasSuppliers: boolean;
  suppliers: SupplierData[];
}

// Complete form data for the carbon footprint calculator
export interface CarbonFootprintFormData {
  selfAssessment: SelfAssessmentFormData;
  manufacturing: ManufacturingFormData;
  supplyChain: SupplyChainFormData;
}

// Results data
export interface ResultsData {
  totalCarbonFootprint: number;
  carbonIntensity: number;
  circularityIndex: number;
  emissionsByCategory: {
    directOperations: number;
    purchasedElectricity: number;
    supplyChain: number;
  };
  recommendations: {
    title: string;
    description: string;
    potentialReduction: number;
  }[];
}

// Form step type
export type FormStep = 'selfAssessment' | 'manufacturing' | 'supplyChain' | 'results';