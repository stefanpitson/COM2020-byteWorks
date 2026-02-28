import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axiosConfig";
import { getCustomerProfile } from "../../api/customers";

const CreditCardIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Z" />
    </svg>
);

const LockClosedIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
    </svg>
);

const CheckCircleIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="size-6 text-green-500">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
);

const AlertIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="size-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
    </svg>
);

// Function to mathematically verify a card number
const isValidLuhn = (number: string) => {
    const digits = number.replace(/\D/g, "");
    let sum = 0;
    let shouldDouble = false;

    for (let i = digits.length - 1; i >= 0; i--) {
        let digit = parseInt(digits.charAt(i));
        if (shouldDouble) {
        if ((digit *= 2) > 9) digit -= 9;
        }
        sum += digit;
        shouldDouble = !shouldDouble;
    }
    return sum % 10 === 0;
};

const getCardType = (number: string) => {
    const clean = number.replace(/\D/g, "");
    if (/^4/.test(clean)) return "Visa";
    if (/^5[1-5]/.test(clean) || /^2[2-7]/.test(clean)) return "Mastercard";
    if (/^3[47]/.test(clean)) return "Amex";
    return "Unknown";
    };

export default function CustomerCredit() {
    const navigate = useNavigate();
    const [balance, setBalance] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [serverError, setServerError] = useState("");

    const [amount, setAmount] = useState<string>("10");
    const [cardName, setCardName] = useState("");
    const [cardNumber, setCardNumber] = useState("");
    const [expiry, setExpiry] = useState("");
    const [cvc, setCvc] = useState("");
    const [address, setAddress] = useState("");
    const [postcode, setPostcode] = useState("");

    const [cardType, setCardType] = useState<string>("Unknown");
    const [isLuhnValid, setIsLuhnValid] = useState<boolean>(true);
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        getCustomerProfile().then((data) => setBalance(data.store_credit));
    }, []);

    const numericAmount = parseFloat(amount);
    const totalAmount = isNaN(numericAmount) ? 0 : numericAmount;

    const getInputClass = (error?: string, hasLeftIcon?: boolean) => {
        return `
            mt-1 block w-full rounded shadow-sm p-3
            border
            ${error ? "border-red-500" : "border-gray-200"} 
            ring-0
            focus:ring-2
            ${error ? "focus:ring-red-500 focus:border-transparent" : "focus:ring-[hsl(var(--primary))] focus:border-transparent"}
            focus:outline-none
            transition-all
            ${hasLeftIcon ? "pl-10" : ""}
        `;
    };

    const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        let val = e.target.value.replace(/\D/g, "");

        if (val.length > 16) val = val.slice(0, 19);
        const formatted = val.replace(/(\d{4})(?=\d)/g, "$1 ");

        setCardNumber(formatted);
        setCardType(getCardType(val));

        if (val.length > 12) {
            setIsLuhnValid(isValidLuhn(val));
        } else {
            setIsLuhnValid(true);
        }
    };

    const handleExpiryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        let val = e.target.value.replace(/\D/g, "");
        if (val.length >= 2) {
            val = val.slice(0, 2) + "/" + val.slice(2, 4);
        }
        setExpiry(val);
    };

    const validateForm = () => {
        const newErrors: Record<string, string> = {};
        const cleanCard = cardNumber.replace(/\D/g, "");

        if (isNaN(numericAmount) || numericAmount < 5 || numericAmount > 100) {
        newErrors.amount = "Amount must be between £5 and £100";
        }

        if (!cleanCard || !isValidLuhn(cleanCard) || cleanCard.length < 13) {
        newErrors.cardNumber = "Invalid card number";
        }

        if (!/^\d{2}\/\d{2}$/.test(expiry)) {
        newErrors.expiry = "Invalid date";
        } else {
        const [month, year] = expiry.split("/").map(Number);
        const now = new Date();
        const currentYear = parseInt(now.getFullYear().toString().slice(-2));
        const currentMonth = now.getMonth() + 1;

        if (month < 1 || month > 12) {
            newErrors.expiry = "Invalid month";
        } else if (year < currentYear || (year === currentYear && month < currentMonth)) {
            newErrors.expiry = "Card has expired";
        }
        }

        const requiredCvcLen = cardType === "Amex" ? 4 : 3;
        if (cvc.length !== requiredCvcLen) {
            newErrors.cvc = `Must be ${requiredCvcLen} digits`;
        }

        if (!address.trim()) newErrors.address = "Address is required";
        if (!postcode.trim() || postcode.length < 5) newErrors.postcode = "Valid postcode required";
        if (!cardName.trim()) newErrors.cardName = "Name is required";

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setServerError("");

        if (!validateForm()) return;

        setLoading(true);

        try {
            const payload = {
                credit_top_up: totalAmount,
                first_line_address: address,
                postcode: postcode,
                name_on_card: cardName,
                card_number: cardNumber.replace(/\s/g, ""),
                expiry_date: `20${expiry.split('/')[1]}-${expiry.split('/')[0]}-01`,
                cvv: cvc
            };

            await api.post("/customer/addcredit", payload);

            setSuccess(true);
            setTimeout(() => {
                navigate("/customer/home");
            }, 2000);

        } catch (err: any) {
            console.error(err);
            setServerError(err.response?.data?.detail || "Transaction failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
        <div className="min-h-screen bg-pattern flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-xl p-8 max-w-md w-full text-center animate-in zoom-in duration-300">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <CheckCircleIcon />
                </div>
                <h2 className="text-2xl font-extrabold text-gray-800 mb-2">Top Up Successful!</h2>
                <p className="text-gray-500 mb-6">£{totalAmount.toFixed(2)} has been added to your wallet.</p>
                <div className="animate-pulse text-[hsl(var(--primary))] font-bold">Redirecting...</div>
            </div>
        </div>
        );
    }

    return (
        <div className="min-h-screen bg-pattern pb-12 pt-24 px-4 sm:px-6">
            <div className="max-w-3xl mx-auto">

                {/* Header */}
                <div className="text-center mb-10">
                    <h1 className="text-3xl font-extrabold text-[hsl(var(--text-main))] mb-2">
                        Top Up Wallet
                    </h1>
                    <p className="text-gray-500">Add funds to purchase meal bundles.</p>
                    {balance !== null && (
                        <div className="mt-4 inline-block bg-white px-4 py-2 rounded-full shadow-sm border border-gray-100">
                            <span className="text-gray-500 text-sm">Current Balance: </span>
                            <span className="font-bold text-[hsl(var(--primary))]">£{balance.toFixed(2)}</span>
                        </div>
                    )}
                </div>

                {/* Payment Form */}
                <div className="bg-white rounded-xl shadow-lg p-6 md:p-8">

                    <form onSubmit={handleSubmit} className="space-y-6">

                        {/* Transaction Amount Entry */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-3">Select Amount</label>
                            <div className="grid grid-cols-3 gap-3 mb-3">
                                {["10", "20", "50"].map((val) => (
                                    <button
                                        key={val}
                                        type="button"
                                        onClick={() => { setAmount(val); setErrors((prev) => ({ ...prev, amount: "" })) }}
                                        className={`py-3 rounded shadow-sm border font-bold transition-all ring-0 focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))] ${amount === val
                                            ? "bg-[hsl(var(--primary))] text-white border-[hsl(var(--primary))]"
                                            : "bg-white text-gray-600 border-gray-200 hover:border-[hsl(var(--primary))]"
                                        }`}
                                    >
                                        £{val}
                                    </button>
                                ))}
                            </div>
                            
                            <div className="relative">
                                <span className="absolute left-3 top-4 text-gray-400 font-bold z-10">£</span>
                                <input
                                    type="number"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    className={getInputClass(errors.amount, true)}
                                    placeholder="£0.00"
                                />
                            </div>

                            <div className="flex justify-between text-xs text-gray-400 mt-2 px-1 font-medium">
                                <span>Min: £5.00</span>
                                <span>Max: £100.00</span>
                            </div>
                        {errors.amount && <p className="text-red-500 text-xs mt-1 ml-1">{errors.amount}</p>}
                        </div>

                        <div className="h-px bg-gray-100 my-6"></div>

                        {/* Card Details */}
                        <div>
                            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                                Card Details
                            </h3>

                            <div className="space-y-4">
                                {/* Card Number */}
                                <div className="relative">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1 block">Card Number</label>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            value={cardNumber}
                                            onChange={handleCardNumberChange}
                                            maxLength={19}
                                            placeholder="0000 0000 0000 0000"
                                            className={getInputClass(!isLuhnValid || errors.cardNumber ? "error" : undefined)}
                                        />
                                        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                                            {/* Card Provider Icons */}
                                            {cardType === 'Visa' && <span className="text-blue-700 font-extrabold italic">VISA</span>}
                                            {cardType === 'Mastercard' && (
                                                <div className="flex -space-x-2">
                                                    <div className="w-6 h-6 rounded-full bg-red-500 opacity-80"></div>
                                                    <div className="w-6 h-6 rounded-full bg-yellow-500 opacity-80"></div>
                                                </div>
                                            )}
                                            {cardType === 'Amex' && <span className="text-blue-500 font-bold border border-blue-500 px-1 rounded text-xs">AMEX</span>}
                                            {cardType === 'Unknown' && <CreditCardIcon />}
                                        </div>
                                    </div>
                                    {!isLuhnValid && <p className="text-red-500 text-xs mt-1">Invalid card number</p>}
                                    {errors.cardNumber && <p className="text-red-500 text-xs mt-1">{errors.cardNumber}</p>}
                                </div>

                                {/* Name */}
                                <div>
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1 block">Cardholder Name</label>
                                    <input
                                        type="text"
                                        value={cardName}
                                        onChange={(e) => setCardName(e.target.value)}
                                        className={getInputClass(errors.cardName)}
                                    />
                                    {errors.cardName && <p className="text-red-500 text-xs mt-1">{errors.cardName}</p>}
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    {/* Expiry */}
                                    <div>
                                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1 block">Expiry</label>
                                        <input
                                            type="text"
                                            value={expiry}
                                            onChange={handleExpiryChange}
                                            placeholder="MM/YY"
                                            maxLength={5}
                                            className={`${getInputClass(errors.expiry)} text-center`}
                                        />
                                        {errors.expiry && <p className="text-red-500 text-xs mt-1">{errors.expiry}</p>}
                                    </div>

                                    {/* CVC - CVV */}
                                    <div>
                                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1 block">CVC / CVV</label>
                                        <div className="relative">
                                            <input
                                                type="text"
                                                value={cvc}
                                                onChange={(e) => setCvc(e.target.value.replace(/\D/g, "").slice(0, 4))}
                                                placeholder="123"
                                                className={`${getInputClass(errors.cvc)} text-center`}
                                            />
                                        </div>
                                        {errors.cvc && <p className="text-red-500 text-xs mt-1">{errors.cvc}</p>}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="h-px bg-gray-100 my-6"></div>

                        {/* Address Section */}
                        <div>
                            <h3 className="text-lg font-bold text-gray-800 mb-4">Billing Address</h3>
                            <div className="space-y-3">
                                <input
                                    type="text"
                                    placeholder="Address Line 1"
                                    value={address}
                                    onChange={(e) => setAddress(e.target.value)}
                                    className={getInputClass(errors.address)}
                                />
                                <input
                                    type="text"
                                    placeholder="Postcode"
                                    value={postcode}
                                    onChange={(e) => setPostcode(e.target.value.replace(/\s/g, "").toUpperCase())}
                                    className={getInputClass(errors.postcode)}
                                />
                            </div>
                            {(errors.address || errors.postcode) && <p className="text-red-500 text-xs mt-1">Address and valid postcode are required.</p>}
                        </div>

                        {/* Amount and Submit Button */}
                        <div className="pt-4">
                            <div className="bg-gray-50 rounded p-4 mb-6 border border-gray-100">
                                <div className="flex justify-between font-bold text-gray-800">
                                    <span>Total to Pay</span>
                                    <span className="text-[hsl(var(--primary))]">£{totalAmount.toFixed(2)}</span>
                                </div>
                            </div>

                            {serverError && (
                                <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm flex items-center gap-2">
                                    <AlertIcon /> {serverError}
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={loading || totalAmount <= 0}
                                className="w-full bg-[hsl(var(--primary))] text-white font-bold text-lg py-3 rounded shadow-md shadow-green-200 hover:shadow-lg hover:translate-y-[-1px] active:translate-y-[0px] transition-all disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center gap-2"
                            >
                                {loading ? (
                                <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                                ) : (
                                <span>Pay £{totalAmount.toFixed(2)}</span>
                                )}
                            </button>
                            <p className="text-center text-xs text-gray-400 mt-4 flex items-center justify-center gap-1">
                                <LockClosedIcon /> Payments are secure and encrypted.
                            </p>
                        </div>

                    </form>
                </div>
            </div>
        </div>
    );
}