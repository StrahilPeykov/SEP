import Image from "next/image";
import Link from "next/link";
import Button from "./components/ui/Button";
import Card from "./components/ui/Card";

export default function Home() {
  return (
    <div className="py-12 sm:py-16">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-5xl md:text-6xl">
            <span className="block">Carbon Footprint Calculator</span>
            <span className="block text-green-600">for SMEs</span>
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 dark:text-gray-400 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Calculate your product carbon footprint and create Digital Product Passports (DPPs) with our easy-to-use tool. No technical knowledge required.
          </p>
          <div className="mt-10 flex justify-center">
            <div className="mr-4">
              <Link href="/self-assessment">
                <Button size="lg">Get Started</Button>
              </Link>
            </div>
            <Link href="#how-it-works">
              <Button variant="outline" size="lg">Learn More</Button>
            </Link>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div id="how-it-works" className="mt-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            How It Works
          </h2>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
            Our simple 4-step process helps you calculate your product carbon footprint
          </p>
        </div>

        <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <Card className="flex flex-col items-center text-center p-6">
            <div className="h-12 w-12 rounded-md bg-green-500 flex items-center justify-center text-white text-xl font-bold mb-4">1</div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Self-Assessment</h3>
            <p className="mt-2 text-base text-gray-500 dark:text-gray-400">
              Complete a simple self-assessment about your organization and operations
            </p>
          </Card>

          <Card className="flex flex-col items-center text-center p-6">
            <div className="h-12 w-12 rounded-md bg-green-500 flex items-center justify-center text-white text-xl font-bold mb-4">2</div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Manufacturing Data</h3>
            <p className="mt-2 text-base text-gray-500 dark:text-gray-400">
              Input your manufacturing process data to enhance accuracy
            </p>
          </Card>

          <Card className="flex flex-col items-center text-center p-6">
            <div className="h-12 w-12 rounded-md bg-green-500 flex items-center justify-center text-white text-xl font-bold mb-4">3</div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Supply Chain</h3>
            <p className="mt-2 text-base text-gray-500 dark:text-gray-400">
              Connect with your suppliers or use default emission factors
            </p>
          </Card>

          <Card className="flex flex-col items-center text-center p-6">
            <div className="h-12 w-12 rounded-md bg-green-500 flex items-center justify-center text-white text-xl font-bold mb-4">4</div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Results & DPP</h3>
            <p className="mt-2 text-base text-gray-500 dark:text-gray-400">
              Receive your carbon footprint results and digital product passport
            </p>
          </Card>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="mt-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            Benefits
          </h2>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
            Why use our carbon footprint calculator
          </p>
        </div>

        <div className="mt-12 grid gap-8 md:grid-cols-3">
          <Card className="p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">No Technical Knowledge Required</h3>
            <p className="mt-2 text-base text-gray-500 dark:text-gray-400">
              Our tool is designed for non-technical users, with a simple interface that guides you through each step
            </p>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Compliant Digital Product Passports</h3>
            <p className="mt-2 text-base text-gray-500 dark:text-gray-400">
              Generate DPPs in Asset Administration Shell (AAS) format, compliant with industry standards
            </p>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">AI-Powered Reduction Advice</h3>
            <p className="mt-2 text-base text-gray-500 dark:text-gray-400">
              Receive personalized recommendations to reduce your carbon footprint across your supply chain
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}