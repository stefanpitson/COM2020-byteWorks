import { useEffect, useState } from "react";
import { getVendorProfile, updateVendorProfile, uploadImage, type VendorUpdatePayload } from "../../api/vendors";
import type { Vendor, User } from "../../types";
import EyeIcon from "../../assets/icons/eye.svg?react";
import EyeOffIcon from "../../assets/icons/eye-off.svg?react";
import { getPasswordStrength, type PasswordStrength, strengthConfig } from '../../utils/password';
import { passwordCheck } from "../../api/auth";
import { resolveImageUrl } from "../../utils/imageUrl";
import placeholder from "../../assets/placeholder.jpg";

const SettingsSection = ({ title, children }: { title: string, children: React.ReactNode }) => (
  <div className="rounded-lg overflow-hidden shadow-md border border-gray-300">
    <div className="bg-gray-100 px-4 py-2 text-xs font-bold uppercase tracking-widest ">
      {title}
    </div>
    <div className="bg-white divide-y divide-gray-200">
      {children}
    </div>
  </div>
);

const SettingsRow = ({ label, value, onChange, type = "text", placeholder, error }
  : { label: string, value: string, onChange: (val: string) => void, type?: string, placeholder?: string, error?: string }) => {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === "password";

  return (
    <div className="flex flex-col p-4 bg-white transition-colors">
      <label className="text-xs text-gray-500 font-bold uppercase tracking-wider mb-2">
        {label}
      </label>
      <div className="relative">
        <input
          type={isPassword ? (showPassword ? "text" : "password") : type}
          value={value}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          className={`w-full text-sm font-semibold bg-transparent focus:outline-none border-b pb-1 transition-colors ${
            error
              ? 'border-red-500 text-red-600 focus:border-red-600'
              : 'border-transparent focus:border-gray-200 text-gray-800'
          } ${isPassword ? 'pr-10 tracking-widest' : ''}`}
        />
        {isPassword && (
          <button
            type="button"
            onMouseDown={(e) => e.preventDefault()}
            onClick={() => setShowPassword(prev => !prev)}
            className="absolute inset-y-0 right-0 flex items-center pr-1 text-gray-500 hover:text-gray-700"
          >
            {showPassword ? <EyeIcon className="size-5" /> : <EyeOffIcon className="size-5" />}
          </button>
        )}
      </div>
      {error && <span className="text-[10px] text-red-500 font-bold mt-1 animate-in fade-in slide-in-from-top-1 whitespace-pre-line">{error}</span>}
    </div>
  );
};

export default function VendorSettings() {
  const [vendor, setVendor] = useState<Vendor>();
  const [user, setUser] = useState<User>();
  const [loading, setLoading] = useState(true);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [street, setStreet] = useState("");
  const [city, setCity] = useState("");
  const [postCode, setPostCode] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [openingHours, setOpeningHours] = useState("");

  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>("very-weak");
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const vendorData = await getVendorProfile();
        setVendor(vendorData);
        setName(vendorData.name);
        setStreet(vendorData.street);
        setCity(vendorData.city);
        setPostCode(vendorData.post_code);
        setPhoneNumber(vendorData.phone_number);
        setOpeningHours(vendorData.opening_hours);
        setImagePreview(resolveImageUrl(vendorData.photo) || placeholder);

        const storedUser = localStorage.getItem("user");
        if (storedUser) {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          setEmail(userData.email);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSave = async () => {
    const newErrors: { [key: string]: string } = {};
    const payload: VendorUpdatePayload = { user: {}, vendor: {} };

    // Validation & Payload construction
    if (!name.trim()) {
      newErrors.name = "Name is required";
    } else if (name.trim() !== vendor?.name) {
      if (name.length > 32) {
        newErrors.name = "Name cannot exceed 32 characters";
      } else {
        payload.vendor.name = name.trim();
      }
    }

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (email.trim() !== user?.email) {
      if (email.length > 256) {
        newErrors.email = "Email cannot exceed 256 characters";
      } else if (!emailRegex.test(email)) {
        newErrors.email = "Please enter a valid email";
      } else {
        payload.user.email = email.trim();
      }
    }

    if (!street.trim()) {
      newErrors.street = "Street is required";
    } else if (street.trim() !== vendor?.street) {
      payload.vendor.street = street.trim();
    }

    if (!city.trim()) {
      newErrors.city = "City is required";
    } else if (city.trim() !== vendor?.city) {
      payload.vendor.city = city.trim();
    }

    const postCodeRegex = /^[A-Z]{1,2}\d[A-Z\d]?\d[A-Z]{2}$/;
    if (!postCode.trim()) {
      newErrors.postCode = "Post Code is required";
    } else if (postCode.trim() !== vendor?.post_code) {
      if (!postCodeRegex.test(postCode)) {
        newErrors.postCode = "Invalid Post Code format.";
      } else {
        payload.vendor.post_code = postCode.toUpperCase().replace(/\s+/g, "");
      }
    }

    if (!phoneNumber.trim()) {
      newErrors.phoneNumber = "Phone Number is required";
    } else if (phoneNumber.trim() !== vendor?.phone_number) {
      payload.vendor.phone_number = phoneNumber.trim();
    }

    if (!openingHours.trim()) {
      newErrors.openingHours = "Opening Hours are required";
    } else if (openingHours.trim() !== vendor?.opening_hours) {
      payload.vendor.opening_hours = openingHours.trim();
    }

    // Password validation
    if (newPassword.trim()) {
      const passwordIssues: string[] = [];
      if (newPassword.length < 8) passwordIssues.push("Password must exceed 8 characters");
      if (newPassword.length > 64) passwordIssues.push("Password cannot exceed 64 characters");
      if (!/[A-Z]/.test(newPassword)) passwordIssues.push("Password must contain at least one capital letter");
      if (!/\d/.test(newPassword)) passwordIssues.push("Password must contain at least one number");
      if (passwordIssues.length > 0) newErrors.newPassword = passwordIssues.join("\n");

      if (!oldPassword.trim()) {
        newErrors.oldPassword = "Old password is required";
      } else if (oldPassword.trim() === newPassword.trim()) {
        newErrors.newPassword = "New password cannot be the same as old password";
      }
    }

    if (oldPassword.trim()) {
      if (!newPassword.trim()) {
        newErrors.newPassword = "New password is required";
      } else {
        const response = await passwordCheck(oldPassword.trim());
        if (!response.valid) {
          newErrors.oldPassword = "Incorrect password";
        }
      }
    }

    if (!newErrors.newPassword && !newErrors.oldPassword && oldPassword.trim() && newPassword.trim()) {
      payload.user.old_password = oldPassword.trim();
      payload.user.new_password = newPassword.trim();
    }

    // Stop the update if there are any errors
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    const hasImageChange = selectedImage !== null;
    const hasDataChange = Object.keys(payload.user).length > 0 || Object.keys(payload.vendor).length > 0;

    if (!hasImageChange && !hasDataChange) {
      alert("No changes detected.");
      return;
    }

    try {
      setLoading(true);

      // 1. Upload image if changed
      if (selectedImage) {
        const imageData = new FormData();
        imageData.append("image", selectedImage);
        await uploadImage(imageData);
      }

      // 2. Update profile if data changed
      if (hasDataChange) {
        await updateVendorProfile(payload);
      }

      setOldPassword("");
      setNewPassword("");
      window.location.reload();
    } catch (err: unknown) {
      console.error("Update failed", err);
      setLoading(false);
      const axiosError = err as { response?: { data?: { detail?: string } } };
      const detail = axiosError.response?.data?.detail;

      if (detail === "Email already registered") {
        setErrors(prev => ({ ...prev, email: "This email is already registered to another account" }));
      } else if (detail) {
        alert(`Update failed: ${detail}`);
      } else {
        alert("An unexpected error occurred during the update.");
      }
    }
  };

  const handleReset = () => {
    if (vendor) {
      setName(vendor.name);
      setStreet(vendor.street);
      setCity(vendor.city);
      setPostCode(vendor.post_code);
      setPhoneNumber(vendor.phone_number);
      setOpeningHours(vendor.opening_hours);
      setImagePreview(resolveImageUrl(vendor.photo) || placeholder);
    }
    if (user) {
      setEmail(user.email);
    }
    setOldPassword("");
    setNewPassword("");
    setSelectedImage(null);
    setErrors({});
  };

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))]">
      <div className="animate-spin w-8 h-8 border-4 border-[hsl(var(--primary))] border-t-transparent rounded-full"></div>
    </div>
  );

  const isChanged =
    name !== (vendor?.name ?? "") ||
    email !== (user?.email ?? "") ||
    street !== (vendor?.street ?? "") ||
    city !== (vendor?.city ?? "") ||
    postCode !== (vendor?.post_code ?? "") ||
    phoneNumber !== (vendor?.phone_number ?? "") ||
    openingHours !== (vendor?.opening_hours ?? "") ||
    selectedImage !== null ||
    (oldPassword.trim() !== "" && newPassword.trim() !== "");

  return (
    <div className="min-h-screen bg-background pt-20 px-4 pb-20 ">
      <div className="max-w-2xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-center sm:text-left">Account Settings</h1>
          <div className="flex gap-4">
            <button className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
              onClick={handleReset}>
              Reset
            </button>

            <button className={`px-4 py-2 rounded transition-all ${isChanged
                ? "bg-primary text-white hover:bg-primaryHover"
                : "bg-gray-300 text-gray-500 cursor-not-allowed"
              }`}
              disabled={!isChanged}
              onClick={handleSave}>
              Save
            </button>
          </div>
        </div>

        <SettingsSection title="Account Details">
          <SettingsRow label="Name" value={name} onChange={setName} error={errors.name} />
          <SettingsRow label="Email" value={email} onChange={setEmail} error={errors.email} />
          <SettingsRow label="Phone Number" value={phoneNumber} onChange={setPhoneNumber} error={errors.phoneNumber} />
        </SettingsSection>

        <SettingsSection title="Security">
          <SettingsRow 
            label="Old Password" 
            type="password" 
            value={oldPassword} 
            onChange={setOldPassword} 
            placeholder="Old Password" 
            error={errors.oldPassword} />
          <div>
            <SettingsRow 
              label="New Password" 
              type="password" 
              value={newPassword} 
              onChange={(e) => {
                setNewPassword(e);
                setPasswordStrength(getPasswordStrength(e));
              }} 
              placeholder="New Password" 
              error={errors.newPassword} />

            {newPassword && (
              <div className="p-4">
                <label className="text-xs text-gray-500 font-bold uppercase tracking-wider ">Strength</label>
                <div>
                  <div className="h-2 w-full rounded bg-gray-200">
                    <div className={`h-2 rounded transition-all ${strengthConfig[passwordStrength].color}`}
                      style={{
                        width:
                          passwordStrength === "very-weak" ? "20%" :
                          passwordStrength === "weak" ? "40%" :
                          passwordStrength === "medium" ? "60%" :
                          passwordStrength === "strong" ? "80%" :
                          "100%",
                      }} />
                  </div>
                  <p className="text-xs mt-1 text-gray-600">{strengthConfig[passwordStrength].label}</p>
                </div>
              </div>
            )}
          </div>
        </SettingsSection>

        <SettingsSection title="Availability">
          <SettingsRow 
            label="Opening Hours" 
            value={openingHours} 
            onChange={setOpeningHours} 
            error={errors.openingHours} />
        </SettingsSection>

        <SettingsSection title="Location">           
          <SettingsRow 
            label="Post Code" 
            value={postCode} 
            onChange={(e) => setPostCode(e.toUpperCase().replace(/\s+/g, ""))} 
            error={errors.postCode} />

          <SettingsRow 
            label="Street" 
            value={street} 
            onChange={setStreet} 
            error={errors.street} />

          <SettingsRow 
            label="City" 
            value={city} 
            onChange={setCity} 
            error={errors.city} />
        </SettingsSection>

        <SettingsSection title="Business Photo">
          <div className="p-6 flex flex-col items-center justify-center bg-white">
            <div className="text-center">
              <p className="text-xs text-gray-500 font-bold uppercase tracking-wider mb-2">Vendor Photo</p>
            </div>
            <div className="w-48 h-48 rounded-2xl overflow-hidden border-4 border-gray-100 relative group shadow-lg mb-4">
                {imagePreview ? (
                  <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full bg-gray-50 flex items-center justify-center text-gray-400">Image</div>
                )}
                <label className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                  <span className="text-white text-sm font-bold uppercase">Update Photo</span>
                  <input type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
                </label>
            </div>
          </div>
        </SettingsSection>
      </div>
    </div>
  );
}
