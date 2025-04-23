import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Link from "next/link";

export default function SelfAssessmentPage() {
  return (
    <div className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
          Self-Assessment
        </h1>
        <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
          Step 1: Tell us about your organization and operations
        </p>
      </div>

      <Card className="max-w-3xl mx-auto">
        <h2 className="text-xl font-semibold mb-6">Company Information</h2>
        
        {/* Placeholder form - will be replaced with actual form components */}
        <div className="space-y-6">
          <div>
            <label htmlFor="company-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Company Name
            </label>
            <input
              type="text"
              id="company-name"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
              placeholder="Your company name"
            />
          </div>

          <div>
            <label htmlFor="industry" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Industry Sector
            </label>
            <select
              id="industry"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
            >
              <option>Manufacturing - Electronics</option>
              <option>Manufacturing - Automotive</option>
              <option>Manufacturing - Textiles</option>
              <option>Manufacturing - Food & Beverage</option>
              <option>Other</option>
            </select>
          </div>

          <div>
            <label htmlFor="employees" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Number of Employees
            </label>
            <select
              id="employees"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
            >
              <option>1-10</option>
              <option>11-50</option>
              <option>51-250</option>
              <option>More than 250</option>
            </select>
          </div>

          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Primary Manufacturing Location
            </label>
            <input
              type="text"
              id="location"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600"
              placeholder="City, Country"
            />
          </div>

          <div className="flex justify-end pt-6">
            <Link href="/manufacturing-data">
              <Button>Continue to Manufacturing Data</Button>
            </Link>
          </div>
        </div>
      </Card>
    </div>
  );
}