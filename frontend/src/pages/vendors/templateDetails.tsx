import React, {useState} from "react";
import { useNavigate } from "react-router-dom";
import { createTemplate } from "../../api/templates";

export default function TemplateDetails() {
    const navigate = useNavigate();

    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [cost, setCost] = useState("");
    const [estimatedValue, setEstimatedValue] = useState("");
    const [weight, setWeight] = useState("");
    const [meatPercent, setMeatPercent] = useState("");
    const [carbPercent, setCarbPercent] = useState("");
    const [vegPercent, setVegPercent] = useState("");
    const [allergens, setAllergens] = useState<string[]>([]);
    const [inclusions, setInclusions] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState<{ [key: string]: string }>({});

    const validateForm = () => {
        const newErrors: { [key: string]: string } = {};
        if (!title.trim()) newErrors.title = "Title is required";
        if (!description.trim()) newErrors.description = "Description is required";
        if (!cost) newErrors.cost = "Cost is required";
        if (!estimatedValue) newErrors.estimatedValue = "Estimated value is required";
        if (!weight) newErrors.weight = "Weight is required";
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!validateForm()) return;

        setIsLoading(true);
        try {
        await createTemplate({
            title: title,
            description: description,
            cost: parseFloat(cost),
            estimated_value: parseFloat(estimatedValue),
            weight: parseFloat(weight),
            meat_percent: (parseFloat(meatPercent) || 0) / 100,
            carb_percent: (parseFloat(carbPercent) || 0) / 100,
            veg_percent: (parseFloat(vegPercent) || 0) / 100,
            is_vegan: inclusions.includes("vegan"),
            is_vegetarian: inclusions.includes("vegetarian"),
            allergen_titles: allergens 
        });
        navigate("/vendor/dashboard"); 
        } catch (error) {
        console.error("Template creation failed:", error);
        } finally {
        setIsLoading(false);
        }
    }

    const handleAllergenChange = (allergen: string) => {
        setAllergens((prev) =>
        prev.includes(allergen) ? prev.filter((a) => a !== allergen) : [...prev, allergen]
        );
    };
    const handleInclusionChange = (inclusion: string) => {
        setInclusions((prev) =>
        prev.includes(inclusion) ? prev.filter((i) => i !== inclusion) : [...prev, inclusion]
        );
    };

    const getInputClass = (error?: string) => { 
        return `
        /* YOUR original styles */
        mt-1 block w-full rounded-md p-3 text-sm bg-white shadow-sm transition-colors text-gray-800
        focus:outline-none focus:ring-2 focus:border-transparent
        
        /* THE dynamic error borders */
        border 
        ${error ? "border-red-500 focus:ring-red-500" : "border-gray-200 focus:ring-primary"}
        `;
    };

  const cardStyle = `
    bg-white rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] 
    p-6 border border-gray-100
  `;

  return (
    <div className="min-h-screen w-full flex justify-center bg-background p-10 font-sans">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-[1100px] w-full">
        
        {/* --- Left Column --- */}
            <div className="md:col-span-1 relative md:border-r border-gray-200 md:pr-12 flex flex-col">
            
                <div className="bg-grayed border-2 border-dashed border-gray-300 rounded-xl h-[250px] flex items-center justify-center text-gray-500 text-sm mt-8 mb-8 cursor-pointer hover:bg-white transition-colors shadow-sm">
                    <span>+ Upload Image</span>
                </div>

                <label className="block mb-4">
                    <span className="text-sm font-medium text-gray-700">Bundle Name</span>
                    <input 
                        type="text" 
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        className={getInputClass(errors.title)} 
                        placeholder="Enter bundle name" 
                    />
                    {errors.title && <p className="text-red-500 text-xs mt-1">{errors.title}</p>}
                </label>
            </div>

            {/* --- Right Column --- */}
            <div className="md:col-span-2 flex flex-col gap-6 pt-8">
            
                <div className={cardStyle}>
                    <label className="block">
                    <span className="text-sm font-medium text-gray-700 block mb-2">Description</span>
                    <textarea
                        rows={5}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        className={`${getInputClass(errors.description)} resize-y leading-relaxed`}
                        placeholder="Describe the items in this bundle..."
                    />
                    {errors.description && <p className="text-red-500 text-xs mt-1">{errors.description}</p>}
                    </label>
                </div>

                <div className={`${cardStyle} grid grid-cols-1 sm:grid-cols-3 gap-6`}>
                    <label className="block">
                        <span className="block mb-1 text-xs uppercase tracking-wider text-gray-500">Cost</span>
                    <input 
                        type="number" step="0.01" 
                        value={cost} onChange={(e) => setCost(e.target.value)}
                        className={getInputClass(errors.cost)} placeholder="£ 0.00"
                    />
                    {errors.cost && <p className="text-red-500 text-xs mt-1">{errors.cost}</p>}
                    </label>
                    <label className="block">
                    <span className="block mb-1 text-xs uppercase tracking-wider text-gray-500">Est. Value</span>
                        <input 
                            type="number" step="0.01" 
                            value={estimatedValue} onChange={(e) => setEstimatedValue(e.target.value)}
                            className={getInputClass(errors.estimatedValue)} placeholder="£ 0.00"
                        />
                        {errors.estimatedValue && <p className="text-red-500 text-xs mt-1">{errors.estimatedValue}</p>}
                    </label>
                    <label className="block">
                        <span className="block mb-1 text-xs uppercase tracking-wider text-gray-500">Weight</span>
                        <input 
                            type="number" step="1" 
                            value={weight} onChange={(e) => setWeight(e.target.value)}
                            className={getInputClass(errors.weight)} placeholder="e.g. 500g"
                        />
                        {errors.weight && <p className="text-red-500 text-xs mt-1">{errors.weight}</p>}
                    </label>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-[1fr_1fr_1.5fr] gap-6">
                
                    <div className={cardStyle}>
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Allergens</h3>
                    <div className="space-y-3 text-sm text-gray-600">
                        {["Celery", "Gluten", "Crustaceans", "Eggs", "Fish", "Lupin", "Milk", "Molluscs", "Mustard", "Treenuts", "Peanuts", "Sesame", "Soybean", "Sulphur Dioxide"].map((allergen) => (
                        <label key={allergen} className="flex items-center cursor-pointer hover:text-gray-900">
                        <input 
                            type="checkbox" 
                            checked={allergens.includes(allergen)}
                            onChange={() => handleAllergenChange(allergen)}
                            className="mr-3 w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary cursor-pointer"
                        />
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
                        <input 
                            type="checkbox" 
                            checked={inclusions.includes(inclusion)}
                            onChange={() => handleInclusionChange(inclusion)}
                            className="mr-3 w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary cursor-pointer"
                        />
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
                    <input 
                        type="number" 
                        value={meatPercent} onChange={(e) => setMeatPercent(e.target.value)}
                        className={getInputClass()} placeholder="e.g. 20" 
                    />
                    </label>
                    <label className="block">
                    <span className="block mb-1 text-xs uppercase tracking-wider text-gray-500">Carbs</span>
                    <input 
                        type="number" 
                        value={carbPercent} onChange={(e) => setCarbPercent(e.target.value)}
                        className={getInputClass()} placeholder="e.g. 50" 
                    />
                    </label>
                    <label className="block">
                    <span className="block mb-1 text-xs uppercase tracking-wider text-gray-500">Plant Based</span>
                    <input 
                        type="number" 
                        value={vegPercent} onChange={(e) => setVegPercent(e.target.value)}
                        className={getInputClass()} placeholder="e.g. 30"
                    />
                    </label>
                </div>
                </div>
                
            </div>

            <div className="flex justify-end mt-4">
                {/* Matches CustomerSignUp button exactly */}
                <button
                type="submit"
                disabled={isLoading}
                className="bg-primary text-white py-3 px-8 rounded-md font-medium hover:bg-primaryHover transition-colors shadow-sm min-w-[200px] disabled:opacity-50"
                >
                {isLoading ? "Creating..." : "Create Bundle"}
                </button>
            </div>
        </div>
      </form>
    </div>
  );
}