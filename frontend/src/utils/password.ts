export type PasswordStrength = 
| "very-weak" 
| "weak" 
| "medium" 
| "strong" 
| "very-strong";

export function getPasswordStrength(password: string): PasswordStrength {
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

export const strengthConfig: Record<PasswordStrength, { label: string; color: string }> = {
    "very-weak": { label: "Very weak", color: "bg-red-500" },
    "weak": { label: "Weak", color: "bg-red-400" },
    "medium": { label: "Medium", color: "bg-yellow-400" },
    "strong": { label: "Strong", color: "bg-green-500" },
    "very-strong": { label: "Very strong", color: "bg-green-700" },
  };