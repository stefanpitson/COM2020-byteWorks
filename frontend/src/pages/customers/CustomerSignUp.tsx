import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerCustomer } from "../../api/auth";

type PasswordStrength = "very-weak" | "weak" | "medium" | "strong" | "very-strong";

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

export default function CustomerSignUp() {
  const navigate = useNavigate();

  // User
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Customer
  const [name, setName] = useState("");
  const [postCode, setPostCode] = useState("");

  const [signUpError, setSignUpError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [shakeKey, setShakeKey] = useState(0);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>("very-weak");

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
    setIsLoading(true);
    try {
      await registerCustomer(
        { email: email.toLowerCase(), password: password, role: "customer" },
        { name: name, post_code: postCode },
      );
      navigate("/login");
    } catch (error) {
      console.error("Signup failed:" + error);
      setSignUpError(true);
      setShakeKey(prev => prev + 1);
    } finally {
      setIsLoading(false);
    }
  }

  const strengthConfig: Record<PasswordStrength, { label: string; color: string }> = {
    "very-weak": { label: "Very weak", color: "bg-red-500" },
    "weak": { label: "Weak", color: "bg-red-400" },
    "medium": { label: "Medium", color: "bg-yellow-400" },
    "strong": { label: "Strong", color: "bg-green-500" },
    "very-strong": { label: "Very strong", color: "bg-green-700" },
  };

  const getInputClass = (error?: string) => {
  return `mt-1 block w-full rounded shadow-sm p-2 ${
    error
      ? "border-red-500 focus:border-red-500 focus:ring focus:ring-red-200 focus:ring-opacity-50"
      : "border-gray-300 focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
  }`;
};

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md bg-white p-4 rounded-xl shadow-lg">
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
          <form onSubmit={handleSubmit} className="space-y-4">
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
              placeholder="name@domain.com"
            />
            {errors.email && (
                <p className="text-red-500 text-xs mt-1">{errors.email}</p>
              )}
          </label>

          <label className="block mb-4">
            <span className="text-sm text-gray-700">Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => {
                const value = e.target.value;
                setPassword(value);
                setPasswordStrength(getPasswordStrength(value));
                if (errors.password) setErrors({...errors, password: ""});
              }}
              className={getInputClass(errors.password)}
              placeholder="••••••••"
            />
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
                if (errors.postCode) setErrors({...errors, postCode: ""});
              }}
              className={getInputClass(errors.postCode)}
              placeholder="EX0 0EX"
            />
            {errors.postCode && (
                <p className="text-red-500 text-xs mt-1">{errors.postCode}</p>
              )}
          </label>

          {signUpError && (
            <div 
              key={shakeKey}
              className="p-3 rounded bg-red-50 border border-red-200 animate-shake">
              <span className="text-red-700 text-sm font-medium">
                Generic placeholder error message
              </span>
            </div>
          )}

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
