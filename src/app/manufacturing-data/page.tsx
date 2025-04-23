import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Link from "next/link";

export default function ManufacturingDataPage() {
  return (
    <div className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
          Manufacturing Data
        </h1>
        <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
          Step 2: Input data about your manufacturing processes
        </p>
      </div>

      <Card className="max-w-3xl mx-auto">
        <h2 className="text-xl font-semibold mb-6">Energy & Resource Consumption</h2>
        
        {/* Placeholder form - will be replaced with actual form components */}
        <div className="space-y-6">
          <div>
            <label htmlFor="product-type" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Primary Product Type
            </label>
            <input
              type="text"
              id="product-type"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
              placeholder="e.g. Electronic component, Automotive part"
            />
          </div>

          <div>
            <label htmlFor="electricity" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Annual Electricity Consumption (kWh)
            </label>
            <input
              type="number"
              id="electricity"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
              placeholder="0"
            />
          </div>

          <div>
            <label htmlFor="fuel" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Annual Fuel Consumption (Liters)
            </label>
            <input
              type="number"
              id="fuel"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
              placeholder="0"
            />
          </div>

          <div>
            <label htmlFor="water" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Annual Water Consumption (m³)
            </label>
            <input
              type="number"
              id="water"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
              placeholder="0"
            />
          </div>

          <div>
            <label htmlFor="waste" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Annual Waste Production (kg)
            </label>
            <input
              type="number"
              id="waste"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
              placeholder="0"
            />
          </div>

          <div className="flex justify-between pt-6">
            <Link href="/self-assessment">
              <Button variant="outline">Back to Self-Assessment</Button>
            </Link>
            <Link href="/supply-chain-data">
              <Button>Continue to Supply Chain</Button>
            </Link>
          </div>
        </div>
      </Card>
    </div>
  );
}