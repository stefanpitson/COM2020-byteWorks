import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerVendor, loginUser, uploadImage} from "../../api/auth";
import type { User } from "../../types";

export default function VendorSignUp() {
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    street: '',
    city: '',
    post_code: '',
    opening_hours: '',
    phone_number: '',
    photo: '',
  });

  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const steps = ["User Details", "Vendor Details", "Image"];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleNext = () => setStep((s) => s + 1);
  const handlePrev = () => setStep((s) => s - 1);

  async function handleSubmit(e: React.SubmitEvent) {
    e.preventDefault();
    if (step < steps.length) return;

    try {
      // 1. register the vendor
      await registerVendor(
        { email: formData.email, password: formData.password, role: "vendor" },
        {   name: formData.name,
            street: formData.street,
            city: formData.city,
            post_code: formData.post_code,
            opening_hours: formData.opening_hours,
            phone_number: formData.phone_number,
        },
      );
      
      // 2. Automatically login in the background
      const loginResponse = await loginUser({
        email: formData.email, 
        password:formData.password
      });

      const token: string = loginResponse.access_token;
      const token_type: string = loginResponse.token_type;
      const user: User = loginResponse.user;

      localStorage.setItem("token", token);
      localStorage.setItem("tokenType", token_type);
      localStorage.setItem("user", JSON.stringify(user));
      localStorage.setItem("role", user.role);


      // Upload the image
      if (selectedImage) {
      const imageData = new FormData();
      imageData.append("image", selectedImage);
      uploadImage(imageData);
    }

    // Navigate to dashboard
    navigate("/vendor/dashboard")
    } catch (error) {
      console.error("Signup failed" + error);
    }
  }

  // Handle Image imagePreview
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedImage(file);
      // Create a temporary local URL for imagePreview
      setImagePreview(URL.createObjectURL(file));
    }
  };


  return (
    <div className="h-screen w-screen flex items-start justify-center bg-background pt-20 md:pt-[20vh]">
      <div className="w-full max-w-md bg-white p-8 space-y-4 rounded-xl shadow-lg transition-all duration-300">

        <div className="relative pt-1">
          <div className="flex mb-2 items-center justify-between">
            <span className="text-xs font-semibold inline-block text-green-600 uppercase">
              Step {step} of {steps.length}
            </span>
          </div>
          <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-200">
            <div
              style={{ width: `${((step) / steps.length) * 100}%` }}
              className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-green-500 transition-all duration-500"
            ></div>
          </div>
        </div>


        <form onSubmit={handleSubmit}>
        
        {/* Page 1: User Details */}
        {step === 1 && (
          <div className="space-y-1 animate-fadeIn">
            <h2 className="text-xl font-bold">Account Details</h2>
            <p>Name:</p>
            <input
              name="name"
              placeholder="Vendor Name"
              className="w-full border p-2 rounded"
              value={formData.name}
              onChange={handleChange}
              required
            />
            <p>Email:</p>
            <input
              name="email"
              placeholder="Vendor@example.com"
              className="w-full border p-2 rounded"
              value={formData.email}
              onChange={handleChange}
              required
            />
            <p>Password:</p>
            <input
              name="password"
              placeholder="Password"
              type="password"
              className="w-full border p-2 rounded"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
        )}

        {/* Page 2: Vendor Details */}
        {step === 2 && (
          <div className="space-y-4 animate-fadeIn">
            <h2 className="text-xl font-bold">Where are you?</h2>
            <input
              name="street"
              placeholder="Street"
              className="w-full border p-2 rounded"
              value={formData.street}
              onChange={handleChange}
              required
            />
            <input
              name="city"
              placeholder="City"
              className="w-full border p-2 rounded"
              value={formData.city}
              onChange={handleChange}
              required
            />
            <input
              name="post_code"
              placeholder="Post Code"
              className="w-full border p-2 rounded"
              value={formData.post_code}
              onChange={handleChange}
              required
            />
            <input
              name="opening_hours"
              placeholder="Opening Hours"
              className="w-full border p-2 rounded"
              value={formData.opening_hours}
              onChange={handleChange}
              required
            />
            <input
              name="phone_number"
              placeholder="+44 xxxx xxx xxx"
              className="w-full border p-2 rounded"
              value={formData.phone_number}
              onChange={handleChange}
              required
            />
          </div>
        )}

        {/* Page 3: Image upload */}
        {step === 3 && (
          <div className="space-y-4 animate-fadeIn">
            <h2 className="text-xl font-bold">Upload your logo to be used</h2>
            
              <div className="flex flex-col items-center gap-4">
                {/* Circle imagePreview Area */}
                <div className="w-52 h-32 rounded-3xl overflow-hidden border-2 border-gray-300 relative">
                  {imagePreview ? (
                    <img src={imagePreview} alt="imagePreview" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full bg-gray-100 flex items-center justify-center text-gray-400">
                      No Image
                    </div>
                  )}
                </div>

                {/* Hidden Input + Custom Button */}
                <label className="cursor-pointer text-green-700 px-4 rounded hover:bg-gray-200">
                  Select Image
                  <input 
                    type="file" 
                    accept="image/*" 
                    className="hidden" 
                    onChange={handleFileChange} 
                  />
                </label>
              </div>

          </div>
        )}

        {/* NAVIGATION BUTTONS */}
        <div className="flex justify-between mt-8">
          <button
            type="button"
            key="back-button"
            onClick={handlePrev}
            disabled={step === 1}
            className={`px-4 py-2 rounded ${step === 1 ? 'bg-gray-300' : 'bg-gray-500 text-white'}`}
          >
            Previous
          </button>

          {step < steps.length ? (
            <button
              type="button"
              key="next-button"
              onClick={handleNext}
              className="px-4 py-2 bg-green-600 text-white rounded"
            >
              Next
            </button>
          ) : (
            <button
              type="submit"
              key="submit-button"
              className="px-4 py-2 bg-blue-600 text-white rounded"
            >
              Submit Profile
            </button>
          )}
        </div>
      </form>
        <p className="text-gray-500 text-sm">
          Are you a customer?{" "}
          <button
            onClick={() => navigate("/customer/signUp")}
            className="text-primary font-bold hover:underline hover:text-primaryHover "
          >
            Create a customer account
          </button>
        </p>
      </div>
    </div>
  );
}
