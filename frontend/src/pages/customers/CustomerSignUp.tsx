import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerCustomer } from "../../api/auth";
import EyeIcon from "../../assets/icons/eye.svg?react";
import EyeOffIcon from "../../assets/icons/eye-off.svg?react";
import BackButton from "../../assets/icons/back-button.svg?react";

export default function CustomerSignUp() {
  const navigate = useNavigate();

  // User
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Customer
  const [name, setName] = useState("");
  const [postCode, setPostCode] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [showPassword, setShowPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>("very-weak");

  type PasswordStrength = "very-weak" | "weak" | "medium" | "strong" | "very-strong";

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
        passwordIssues.push("Password must exceed 8 characters");
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
    setIsLoading(true);
    try {
      await registerCustomer(
        { email: email.toLowerCase(), password: password, role: "customer" },
        { name: name, post_code: postCode },
      );
      navigate("/login");
    } catch (error) {
      console.error("Signup failed:" + error);
    } finally {
      setIsLoading(false);
    }
  }

  function getPasswordStrength(password: string): PasswordStrength {
    const length = password.length;
    const hasUpper = /[A-Z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSymbol = /[^A-Za-z0-9]/.test(password);

    if (length < 8 || !hasUpper || !hasNumber ) {
      if (length < 4) {
        return "very-weak";
      } else {
        return "weak";
      }
    } else if (length < 12 && !hasSymbol) {
      return "medium";
    } else if (length > 11 && hasSymbol) {
      return "very-strong";
    } else {
      return "strong";
    }
  }

  const strengthConfig: Record<PasswordStrength, { label: string; color: string }> = {
    "very-weak": { label: "Very weak", color: "bg-red-500" },
    "weak": { label: "Weak", color: "bg-red-400" },
    "medium": { label: "Medium", color: "bg-yellow-400" },
    "strong": { label: "Strong", color: "bg-green-500" },
    "very-strong": { label: "Very strong", color: "bg-green-700" },
  };

  const getInputClass = (error?: string) => { return `
    mt-1 block w-full rounded shadow-sm p-2
    border
    ${error ? "border-red-500" : "border-transparent"}
    ring-0
    focus:ring-2
    ${error ? "focus:ring-red-500 focus:border-transparent" : "focus:ring-primary"}
    focus:outline-none
  `;
};

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md bg-white p-4 rounded-xl shadow-lg">
        <button 
          type="button" 
          onClick={() => navigate("/login")}
          className="rounded-full hover:bg-gray-100 transition-colors"
        >
          <BackButton/>
        </button>
        
        <div className="p-4 space-y-4">
          <form onSubmit={handleSubmit} className="space-y-4">
          <h2 className="text-2xl font-semibold mb-6">Create Customer</h2>
          
          <label className="block mb-4">
            <span className="text-sm text-gray-700">Name</span>
            <input
              value={name}
              onChange={(e) => {
                setName(e.target.value);
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
              }}
              className={getInputClass(errors.email)}
              placeholder="name@domain.com"
            />
            {errors.email && (
                <p className="text-red-500 text-xs mt-1">{errors.email}</p>
              )}
          </label>

          <label className="block mb-4">
            <span className="text-sm text-gray-700">Password</span>

            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => {
                  const value = e.target.value;
                  setPassword(value);
                  setPasswordStrength(getPasswordStrength(value));
                }}
                className={`${getInputClass(errors.password)} pr-10`}
                placeholder="••••••••"
              />

              <button
                type="button"
                onMouseDown={(e) => e.preventDefault()} // stops focus border from flashing when button is clicked
                onClick={() => setShowPassword(prev => !prev)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 hover:text-gray-700"
              >
                {showPassword ? <EyeOffIcon/> : <EyeIcon/>}
              </button>
            </div>

            {errors.password && (
                <p className="text-red-500 text-xs mt-1 whitespace-pre-line">{errors.password}</p>
              )}
          </label>

          {password && (
            <div className="mt-2">
              <div className="h-2 w-full rounded bg-gray-200">
                <div
                  className={`h-2 rounded transition-all ${strengthConfig[passwordStrength].color}`}
                  style={{
                    width:
                      passwordStrength === "very-weak" ? "20%" :
                      passwordStrength === "weak" ? "40%" :
                      passwordStrength === "medium" ? "60%" :
                      passwordStrength === "strong" ? "80%" :
                      "100%",
                  }}
                />
              </div>
              <p className="text-xs mt-1 text-gray-600">
                {strengthConfig[passwordStrength].label}
              </p>
            </div>
          )}

          <label className="block mb-4">
            <span className="text-sm text-gray-700">Post Code</span>
            <input
              value={postCode}
              onChange={(e) => {
                setPostCode(e.target.value);
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
            disabled={isLoading}
            className="w-full bg-primary text-white py-2 rounded hover:bg-primaryHover"
          >
            {isLoading ? 'Creating account...' : 'Create account'}
          </button>
        
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-500 text-sm">
            Are you a vendor?{" "}
            <button
              onClick={() => navigate("/customer/signup")}
              className="text-primary font-bold hover:underline hover:text-primaryHover "
            >
              Create vendor account
            </button>
          </p>
        </div>
        </div>
        
      </div>
    </div>
  );
}
