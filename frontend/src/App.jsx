import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [users, setUsers] = useState([])
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")

  // 1. Fetch users from the backend
  const fetchUsers = async () => {
    const response = await fetch("http://localhost:8000/users/")
    const data = await response.json()
    setUsers(data)
  }

  // Run fetch on initial load
  useEffect(() => {
    fetchUsers()
  }, [])

  // 2. Handle Form Submit
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const newUser = { name, email }

    await fetch("http://localhost:8000/users/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newUser)
    })

    // Clear inputs and refresh the list
    setName("")
    setEmail("")
    fetchUsers()
  }

  return (
    <div style={{ padding: "50px", fontFamily: "Arial" }}>
      <h1>User Management System</h1>

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
        <input 
          type="text" 
          placeholder="Name" 
          value={name} 
          onChange={(e) => setName(e.target.value)} 
          style={{ marginRight: "10px", padding: "5px" }}
        />
        <input 
          type="text" 
          placeholder="Email" 
          value={email} 
          onChange={(e) => setEmail(e.target.value)} 
          style={{ marginRight: "10px", padding: "5px" }}
        />
        <button type="submit" style={{ padding: "5px 15px" }}>Add User</button>
      </form>

      {/* User List */}
      <h2>Current Users:</h2>
      <ul>
        {users.map((user) => (
          <li key={user.id}>
            <strong>{user.name}</strong> - {user.email}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default App