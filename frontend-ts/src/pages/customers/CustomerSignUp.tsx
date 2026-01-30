import React, { useState } from 'react'
import { useNavigate,  } from "react-router-dom"
import { registerCustomer } from "../../api/auth";


export default function CustomerSignUp () {
    const navigate = useNavigate()

    // User
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    // Customer
    const [name, setName] = useState('')
    const [postCode, setPostCode] = useState('')

    async function handleSubmit (e: React.FormEvent) {
        console.log("Here");
        e.preventDefault();
        try {
            await registerCustomer(
            {   email: email, 
                password: password,
                role: "customer"
            },
            {   name: name, 
                post_code: postCode } 
            );
            navigate('/login');
        } catch (error) {
            console.error("Signup failed" + error);
        }
    };


    return (
        <div className="h-screen w-screen flex items-center justify-center bg-background">
            <div className="w-full max-w-md bg-white p-8 space-y-4 rounded-xl shadow-lg">
                <form onSubmit={handleSubmit}>
					<h2 className="text-2xl font-semibold mb-6">Create Customer</h2>
					<label className="block mb-4">
						<span className="text-sm text-gray-700">Email</span>
						<input
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 p-2"
							placeholder="you@example.com"
						/>
					</label>

					<label className="block mb-6">
						<span className="text-sm text-gray-700">Password</span>
						<input
							// type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 p-2"
							placeholder="••••••••"
						/>
					</label>

                    <label className="block mb-4">
						<span className="text-sm text-gray-700">Name</span>
						<input
							value={name}
							onChange={(e) => setName(e.target.value)}
							className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 p-2"
							placeholder="name"
						/>
					</label>

                    <label className="block mb-4">
						<span className="text-sm text-gray-700">Post Code</span>
						<input
							value={postCode}
							onChange={(e) => setPostCode(e.target.value)}
							className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 p-2"
							placeholder="EX0 0EX"
						/>
					</label>

					<button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-800">
						Create account
					</button>
				</form>
                <p className="text-gray-500 text-sm">
                    Are you a vendor?{' '}
                    <button 
                        onClick={() => navigate("/vendor/signUp")}
                        className="text-primary font-bold hover:underline hover:text-primaryHover "
                    >
                        Create a vendor account
                    </button>
                </p>
            </div>
        </div>
    )
}