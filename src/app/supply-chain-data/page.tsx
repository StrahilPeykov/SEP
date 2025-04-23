import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Link from "next/link";

export default function SupplyChainPage() {
  return (
    <div className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
          Supply Chain Data
        </h1>
        <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
          Step 3: Add information about your suppliers and their carbon footprint
        </p>
      </div>

      <div className="space-y-10">
        <Card className="max-w-3xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Do you have suppliers?</h2>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center space-x-4">
              <button className="px-4 py-2 border-2 border-green-500 rounded-md font-medium text-green-600 hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                Yes
              </button>
              <button className="px-4 py-2 border-2 border-gray-300 rounded-md font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800">
                No
              </button>
            </div>
          </div>
        </Card>

        <Card className="max-w-3xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Supplier Information</h2>
            <Button variant="outline" size="sm">+ Add Supplier</Button>
          </div>
          
          <div className="space-y-6">
            <div className="border border-gray-200 rounded-md p-4 dark:border-gray-700">
              <h3 className="font-medium">Supplier #1</h3>
              
              <div className="mt-4 space-y-4">
                <div>
                  <label htmlFor="supplier-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Supplier Name
                  </label>
                  <input
                    type="text"
                    id="supplier-name"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
                    placeholder="Supplier company name"
                  />
                </div>

                <div>
                  <label htmlFor="supplier-component" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Component/Material Supplied
                  </label>
                  <input
                    type="text"
                    id="supplier-component"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
                    placeholder="e.g. Electronic components, raw materials"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Does this supplier share CO₂ data?
                  </label>
                  <div className="mt-1 flex items-center space-x-4">
                    <button className="px-3 py-1 border-2 border-green-500 rounded-md text-sm font-medium text-green-600 hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                      Yes
                    </button>
                    <button className="px-3 py-1 border-2 border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800">
                      No
                    </button>
                  </div>
                </div>

                <div>
                  <label htmlFor="supplier-format" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    CO₂ Data Format
                  </label>
                  <select
                    id="supplier-format"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
                  >
                    <option>Digital Product Passport (DPP in AASX format)</option>
                    <option>Other digital format</option>
                    <option>Manual data entry</option>
                    <option>No data available (use estimates)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-between pt-6">
            <Link href="/manufacturing-data">
              <Button variant="outline">Back to Manufacturing Data</Button>
            </Link>
            <Link href="/results">
              <Button>Calculate Results</Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}