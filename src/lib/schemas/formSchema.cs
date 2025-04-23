import { z } from 'zod';

// Self-assessment schema
export const selfAssessmentSchema = z.object({
  companyName: z.string().min(1, 'Company name is required'),
  industrySector: z.string().min(1, 'Industry sector is required'),
  employeeCount: z.string().min(1, 'Employee count is required'),
  location: z.string().min(1, 'Location is required'),
  annualRevenue: z.string().optional(),
  hasEnvironmentalPolicy: z.boolean().default(false),
});

// Manufacturing data schema
export const manufacturingSchema = z.object({
  productType: z.string().min(1, 'Product type is required'),
  annualProduction: z.number().min(1, 'Annual production must be greater than 0'),
  electricityConsumption: z.number().min(0, 'Electricity consumption cannot be negative'),
  electricityRenewablePercentage: z.number().min(0).max(100, 'Percentage must be between 0 and 100'),
  fuelConsumption: z.number().min(0, 'Fuel consumption cannot be negative'),
  fuelType: z.string().min(1, 'Fuel type is required'),
  waterConsumption: z.number().min(0, 'Water consumption cannot be negative'),
  wasteProduction: z.number().min(0, 'Waste production cannot be negative'),
  recycledWastePercentage: z.number().min(0).max(100, 'Percentage must be between 0 and 100'),
});

// Supplier data schema
export const supplierSchema = z.object({
  id: z.string(),
  name: z.string().min(1, 'Supplier name is required'),
  component: z.string().min(1, 'Component/material is required'),
  sharesCO2Data: z.boolean(),
  dataFormat: z.string().optional(),
  carbonFootprint: z.number().optional(),
  carbonFootprintUnit: z.string().optional(),
  useEstimates: z.boolean().default(false),
});

// Supply chain schema
export const supplyChainSchema = z.object({
  hasSuppliers: z.boolean(),
  suppliers: z.array(supplierSchema).default([]),
});

// Complete carbon footprint form schema
export const carbonFootprintSchema = z.object({
  selfAssessment: selfAssessmentSchema,
  manufacturing: manufacturingSchema,
  supplyChain: supplyChainSchema,
});

// Results schema
export const resultsSchema = z.object({
  totalCarbonFootprint: z.number(),
  carbonIntensity: z.number(),
  circularityIndex: z.number(),
  emissionsByCategory: z.object({
    directOperations: z.number(),
    purchasedElectricity: z.number(),
    supplyChain: z.number(),
  }),
  recommendations: z.array(z.object({
    title: z.string(),
    description: z.string(),
    potentialReduction: z.number(),
  })),
});