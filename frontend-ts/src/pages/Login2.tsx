import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { Token, User } from '../types'
import { mockToken, mockUser } from '../mocks'

export default function Login2() {

	const navigate = useNavigate()
    const [activeTab, setActiveTab] = useState<'Customer' | 'Business'>('Customer');

    const isUser = activeTab === 'Customer';
    const signupPath = isUser ? '/CustomerSignUp' : '/BusinessSignUp';

    return (
    <div className="h-screen w-screen flex items-center justify-center bg-gray-100">
      <div className="w-full max-w-md bg-white rounded-xl shadow-2xl overflow-hidden">
    
        {/* TAB HEADER */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab('Customer')}
            className={`flex-1 py-4 font-semibold transition-colors ${
              isUser ? 'bg-white text-green-700 border-b-2 border-green-700' : 'bg-gray-50 text-gray-400'
            }`}
          >
            Customers
          </button>
          <button
            onClick={() => setActiveTab('Business')}
            className={`flex-1 py-4 font-semibold transition-colors ${
              !isUser ? 'bg-white text-green-700 border-b-2 border-green-700' : 'bg-gray-50 text-gray-400'
            }`}
          >
            Businesses
          </button>
        </div>

        {/* FORM CONTENT */}
        <div className="p-8">
          <h2 className="text-2xl font-bold text-center mb-6">
            {isUser ? 'User Login' : 'Business Portal'}
          </h2>

          <form className="space-y-4">
            <input 
              type="text" 
              placeholder={isUser ? "Username" : "Business ID"} 
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-700 outline-none"
            />
            <input 
              type="password" 
              placeholder="Password" 
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-700 outline-none"
            />
            
            <button className="w-full bg-green-700 text-white py-3 rounded-lg font-bold hover:bg-green-600 transition-colors">
              Sign In
            </button>
          </form>

          {/* DYNAMIC FOOTER */}
          <div className="mt-6 text-center">
            <p className="text-gray-500 text-sm">
              Don't have an account?{' '}
              <button 
                onClick={() => navigate(signupPath)}
                className="text-green-700 font-bold hover:underline hover:text-green-600 "
              >
                Create {activeTab} account
              </button>
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}