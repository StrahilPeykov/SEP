import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Link from "next/link";

export default function ResultsPage() {
  return (
    <div className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
          Carbon Footprint Results
        </h1>
        <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
          Step 4: View your results and download your Digital Product Passport
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-2">
        <Card className="md:col-span-2">
          <h2 className="text-xl font-semibold mb-6">Carbon Footprint Overview</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-center">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Carbon Footprint</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">28.5</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">tons CO₂e</p>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-center">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Carbon Intensity</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">2.4</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">kg CO₂e per unit</p>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-center">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Circularity Index</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">68%</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">recycled materials</p>
            </div>
          </div>
          
          {/* Placeholder chart */}
          <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center mb-6">
            <p className="text-gray-500 dark:text-gray-400">Carbon footprint breakdown chart</p>
          </div>
          
          <div className="flex flex-wrap justify-center space-x-4">
            <Button>Download Digital Product Passport</Button>
            <Button variant="outline">Export as CSV</Button>
            <Button variant="outline">Print Report</Button>
          </div>
        </Card>
        
        <Card>
          <h2 className="text-xl font-semibold mb-6">Emissions by Category</h2>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Direct Operations</span>
              <span className="text-sm font-medium">8.2 tons CO₂e</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
              <div className="bg-green-600 h-2.5 rounded-full" style={{ width: "30%" }}></div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Purchased Electricity</span>
              <span className="text-sm font-medium">5.7 tons CO₂e</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
              <div className="bg-green-600 h-2.5 rounded-full" style={{ width: "20%" }}></div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Supply Chain</span>
              <span className="text-sm font-medium">14.6 tons CO₂e</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
              <div className="bg-green-600 h-2.5 rounded-full" style={{ width: "50%" }}></div>
            </div>
          </div>
        </Card>
        
        <Card>
          <h2 className="text-xl font-semibold mb-6">AI Reduction Recommendations</h2>
          
          <div className="space-y-4">
            <div className="p-3 bg-green-50 border border-green-200 rounded-md dark:bg-green-900/20 dark:border-green-900">
              <h3 className="font-medium text-green-800 dark:text-green-400">Renewable Energy</h3>
              <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                Switching to renewable energy sources could reduce your carbon footprint by up to 35%.
              </p>
            </div>
            
            <div className="p-3 bg-green-50 border border-green-200 rounded-md dark:bg-green-900/20 dark:border-green-900">
              <h3 className="font-medium text-green-800 dark:text-green-400">Supplier Collaboration</h3>
              <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                Working with your main suppliers to reduce their emissions could decrease your supply chain footprint by 20%.
              </p>
            </div>
            
            <div className="p-3 bg-green-50 border border-green-200 rounded-md dark:bg-green-900/20 dark:border-green-900">
              <h3 className="font-medium text-green-800 dark:text-green-400">Energy Efficiency</h3>
              <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                Implementing energy efficiency measures in your manufacturing process could save 15% of your current emissions.
              </p>
            </div>
          </div>
        </Card>
        
        <div className="md:col-span-2 flex justify-between mt-6">
          <Link href="/supply-chain-data">
            <Button variant="outline">Back to Supply Chain</Button>
          </Link>
          <Link href="/">
            <Button>Back to Home</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}