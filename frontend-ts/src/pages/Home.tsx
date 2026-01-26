import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { User } from '../types'

export default function Home() {
	const navigate = useNavigate()

    const userString = localStorage.getItem('user')
    const user = userString ? (JSON.parse(userString) as User) : null;

    const [userName, setUsername] = useState(user?.name);

	function handleLogout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('loggedIn');
		navigate('/login')
	}

	return (
		<div className="min-h-screen flex items-center justify-center bg-gray-100">
			<div className="w-full max-w-md bg-white p-10 rounded-xl shadow-lg text-center mx-4">
				<h1 className="text-3xl font-bold mb-4">Welcome</h1>
                <p className="text-black mb-2">Hello {userName}</p>
				<p className="text-gray-700 mb-8">You are signed in. This is the home page.</p>
				<button onClick={handleLogout} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
					Log out
				</button>
			</div>
		</div>
	)
}
