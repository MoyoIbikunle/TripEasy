import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function RegisterForm() {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [phone, setPhone] = useState("")
  const [errorMessage, setErrorMessage] = useState("")

  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage("")

    //step 1 - register the new user
    const response = await fetch("http://localhost:8000/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name: name, email: email, password: password, phone_number: phone })
    })

    const data = await response.json()

    if (!response.ok) {
      setErrorMessage(data.detail)
      return
    }

    //step 2 - registration succeeded, now log in automatically using the same credentials
    const loginResponse = await fetch("http://localhost:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email: email, password: password })
    })

    const loginData = await loginResponse.json()

    if (!loginResponse.ok) {
      //registration worked, but auto-login somehow failed - rare, but handle it
      setErrorMessage("Registered, but automatic login failed. Please log in manually.")
      return
    }

    //save the token, same as LoginForm does
    localStorage.setItem("token", loginData.access_token)
    console.log("Registered and logged in! Token saved.")
    navigate("/dashboard")
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>TripEasy</h1>

      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}

      <label>Name</label>
      <input type="text" value={name} onChange={(e) => setName(e.target.value)} required/>

      <label>Phone</label>
      <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} required/>

      <label>Email</label>
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required/>

      <label>Password</label>
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required/>

      <button type="submit">Register</button>
    </form>
  )
}

export default RegisterForm