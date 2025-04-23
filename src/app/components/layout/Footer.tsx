export default function Footer() {
    return (
      <footer className="bg-white dark:bg-gray-900 mt-auto">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <p className="text-center text-sm text-gray-500 dark:text-gray-400">
              &copy; {new Date().getFullYear()} Carbon Footprint Calculator. Funded by the European Union.
            </p>
            <p className="text-center text-xs text-gray-400 dark:text-gray-500 mt-2">
              Views and opinions expressed are those of the authors only and do not necessarily reflect those of the European Union or Health and Digital Executive Agency (HaDEA).
            </p>
          </div>
        </div>
      </footer>
    );
  }