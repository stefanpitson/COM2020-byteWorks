import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { Token, User } from '../types'
import { mockToken, mockUser } from '../mocks'

export default function Login() {
	const navigate = useNavigate()
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')

	function handleSubmit(e: React.FormEvent) {
		e.preventDefault()
		// Replace with real auth call. For now, accept any non-empty credentials.
		if (username.trim() && password.trim()) {

			const token: Token = mockToken;
			const user: User = mockUser;

			localStorage.setItem('loggedIn', 'true')
            localStorage.setItem('token', token)
            localStorage.setItem('user', JSON.stringify(user));
			navigate('/home')
		}
	}

	return (
		<div className="min-h-screen flex items-center justify-center bg-red-50">
			<form onSubmit={handleSubmit} className="w-full max-w-md bg-white p-8 rounded-xl shadow-lg">
				<h2 className="text-2xl font-semibold mb-6">Sign in</h2>
				<label className="block mb-4">
					<span className="text-sm text-gray-700">Username</span>
					<input
						value={username}
						onChange={(e) => setUsername(e.target.value)}
						className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 p-2"
						placeholder="you@example.com"
					/>
				</label>

				<label className="block mb-6">
					<span className="text-sm text-gray-700">Password</span>
					<input
						type="password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 p-2"
						placeholder="••••••••"
					/>
				</label>

				<button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-800">
					Log in
				</button>
			</form>
		</div>
	)
}
