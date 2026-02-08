import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerCustomer } from "../../api/auth";

export default function CustomerSignUp() {
  const navigate = useNavigate();

  // User
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Customer
  const [name, setName] = useState("");
  const [postCode, setPostCode] = useState("");

  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (!name.trim()) {
      newErrors.name = "Name is required"; 
    } else if (name.length > 32) {
      newErrors.name = "Name cannot exceed 32 characters"; 
    }

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (email.length > 256) {
      newErrors.email = "Email cannot exceed 256 characters";
    } else if (!emailRegex.test(email)) {
      newErrors.email = "Please enter a valid email";
    }

    if (!password.trim()) { 
      newErrors.password = "Password is required";
    } else {
      const passwordIssues: string[] = [];

      if (password.length < 8) {
        passwordIssues.push("Password must exceed 8 charactors");
      }  
      if (password.length > 64) {
        passwordIssues.push("Password cannot exceed 64 characters");
      }  
      if (!/[A-Z]/.test(password)) {
        passwordIssues.push("Password must contain at least one capital letter");
      } 
      if (!/\d/.test(password)) {
        passwordIssues.push("Password must contain at least one number");
      }
      if (passwordIssues.length > 0) {
        newErrors.password = passwordIssues.join("\n");
      }
    }
      
    const postCodeRegex = /^[a-zA-Z]{1,2}\d[a-zA-Z\d]?\s\d[a-zA-Z]{2}$/;
    if (!postCode.trim()) {
      newErrors.postCode = "Post Code is required";
    } else if (!postCodeRegex.test(postCode)) {
      newErrors.postCode = "Invalid Post Code format."
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };  

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validateForm()) {
      return;
    }
    console.log("Here");
    try {
      await registerCustomer(
        { email: email, password: password, role: "customer" },
        { name: name, post_code: postCode },
      );
      navigate("/login");
    } catch (error) {
      console.error("Signup failed" + error);
    }
  }

  const getInputClass = (error: string | undefined) => {
    return `mt-1 block w-full rounded border shadow-sm outline-none p-2 ${
      error
        ? "border-red-500 focus:border-red-500 focus:ring-red-200" // Error style
        : "border-gray-300 focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-100" // Normal style
    }`;
  };

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md bg-white p-4 space-y-4 rounded-xl shadow-lg">
        <button 
          type="button" 
          onClick={() => navigate("/login")}
          className="rounded-full hover:bg-gray-100 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 15 3 9m0 0 6-6M3 9h12a6 6 0 0 1 0 12h-3" />
          </svg>
        </button>
        
        <div className="p-4 space-y-4">
          <form onSubmit={handleSubmit}>
          <h2 className="text-2xl font-semibold mb-6">Create Customer</h2>
          
          <label className="block mb-4">
            <span className="text-sm text-gray-700">Name</span>
            <input
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (errors.name) setErrors({...errors, name: ""});
              }}
              className={getInputClass(errors.name)}
              placeholder="Name"
            />
            {errors.name && (
                <p className="text-red-500 text-xs mt-1">{errors.name}</p>
              )}
          </label>

          <label className="block mb-4">
            <span className="text-sm text-gray-700">Email</span>
            <input
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errors.email) setErrors({...errors, email: ""});
              }}
              className={getInputClass(errors.email)}
              placeholder="you@example.com"
            />
            {errors.email && (
                <p className="text-red-500 text-xs mt-1">{errors.email}</p>
              )}
          </label>

          <label className="block mb-6">
            <span className="text-sm text-gray-700">Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (errors.password) setErrors({...errors, password: ""});
              }}
              className={getInputClass(errors.password)}
              placeholder="••••••••"
            />
            {errors.password && (
                <p className="text-red-500 text-xs mt-1 whitespace-pre-line">{errors.password}</p>
              )}
          </label>

          

          <label className="block mb-4">
            <span className="text-sm text-gray-700">Post Code</span>
            <input
              value={postCode}
              onChange={(e) => {
                setPostCode(e.target.value);
                if (errors.postCode) setErrors({...errors, postCode: ""});
              }}
              className={getInputClass(errors.postCode)}
              placeholder="EX0 0EX"
            />
            {errors.postCode && (
                <p className="text-red-500 text-xs mt-1">{errors.postCode}</p>
              )}
          </label>

          <button
            type="submit"
            className="w-full bg-primary text-white py-2 rounded hover:bg-primaryHover"
          >
            Create account
          </button>
        </form>
        <div className="flex flex-col items-center">
          <p className="text-gray-500 text-sm">
            Are you a vendor?{" "}
            
          </p>
          <button
              onClick={() => navigate("/vendor/signUp")}
              className="text-primary font-bold hover:underline hover:text-primaryHover "
            >
              Create a vendor account
            </button>
        </div>
        </div>
        
      </div>
    </div>
  );
}
