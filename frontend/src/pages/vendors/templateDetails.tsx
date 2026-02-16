export default function templateDetails() {
    const inputStyle = `
    mt-1 block w-full rounded-md p-3 text-sm
    border border-gray-200 bg-white
    shadow-sm
    focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
    transition-colors text-gray-800
  `;

  const cardStyle = `
    bg-white rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] 
    p-6 border border-gray-100
  `;

  return (
    <div className="min-h-screen w-full flex justify-center bg-background p-10 font-sans">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-[1100px] w-full">
        
        {/* --- Left Column --- */}
        <div className="md:col-span-1 relative md:border-r border-gray-200 md:pr-12 flex flex-col">
          
          <div className="bg-grayed border-2 border-dashed border-gray-300 rounded-xl h-[250px] flex items-center justify-center text-gray-500 text-sm mt-8 mb-8 cursor-pointer hover:bg-white transition-colors shadow-sm">
            <span>+ Upload Image</span>
          </div>

          <label className="block mb-4">
            <span className="text-sm font-medium text-gray-700">Bundle Name</span>
            <input type="text" className={inputStyle} placeholder="Enter bundle name" />
          </label>
        </div>

        {/* --- Right Column --- */}
        <div className="md:col-span-2 flex flex-col gap-6 pt-8">
          
          <div className={cardStyle}>
            <label className="block">
              <span className="text-sm font-medium text-gray-700 block mb-2">Description</span>
              <textarea
                rows={5}
                className={`${inputStyle} resize-y leading-relaxed`}
                defaultValue="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
              />
            </label>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-[1fr_1fr_1.5fr] gap-6">
            
            <div className={cardStyle}>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Allergens</h3>
              <div className="space-y-3 text-sm text-gray-600">
                {["gluten", "dairy", "eggs", "shellfish", "soy", "nuts", "sesame"].map((allergen) => (
                  <label key={allergen} className="flex items-center cursor-pointer hover:text-gray-900">
                    <input type="checkbox" className="mr-3 w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary cursor-pointer" />
                    {allergen}
                  </label>
                ))}
              </div>
            </div>

            <div className={cardStyle}>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Inclusions</h3>
              <div className="space-y-3 text-sm text-gray-600">
                {["vegan", "vegetarian"].map((inclusion) => (
                  <label key={inclusion} className="flex items-center cursor-pointer hover:text-gray-900">
                    <input type="checkbox" className="mr-3 w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary cursor-pointer" />
                    {inclusion}
                  </label>
                ))}
              </div>
            </div>

            <div className={cardStyle}>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Percentages</h3>
              <div className="space-y-4 text-sm text-gray-600">
                <label className="block">
                  <span className="block mb-1 text-xs uppercase tracking-wider text-gray-500">Meat</span>
                  <input type="text" className={inputStyle} placeholder="e.g. 20%" />
                </label>
                <label className="block">
                  <span className="block mb-1 text-xs uppercase tracking-wider text-gray-500">Carbs</span>
                  <input type="text" className={inputStyle} placeholder="e.g. 50%" />
                </label>
                <label className="block">
                  <span className="block mb-1 text-xs uppercase tracking-wider text-gray-500">Plant Based</span>
                  <input type="text" className={inputStyle} placeholder="e.g. 30%" />
                </label>
              </div>
            </div>
            
          </div>

          <div className="flex justify-end mt-4">
            {/* Matches CustomerSignUp button exactly */}
            <button
              type="button"
              className="bg-primary text-white py-3 px-8 rounded-md font-medium hover:bg-primaryHover transition-colors shadow-sm min-w-[200px]"
            >
              Create Bundle
            </button>
          </div>
          
        </div>
      </div>
    </div>
  );
}