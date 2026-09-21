import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function LoginForm() {
    //email starts off as an empty string setEmail is what changes it
    //before typing, email is ""
    //value={email} displays whatever email is 
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  //tracks whether there's an error message to show on screen
  const [errorMessage, setErrorMessage] = useState("")

  const navigate = useNavigate()

  //async marks function as one waiting for something slow
async function handleSubmit(event) {
  event.preventDefault()
  //clear any old error before trying again
  setErrorMessage("")

  //await means pause until you get a response, fetch sends the request, if not the code would try move on before the server replied
  //goes to check backend /login
  const response = await fetch("http://localhost:8000/login", {
    method: "POST",
    //tells the server the data im sending is JSON
    headers: {
      "Content-Type": "application/json"
    },
    //builds JSON data being sent, JSON.stringify converts a js objet into JSON text
    //using what UserLogin expects
    body: JSON.stringify({ email: email, password: password })
  })

  //parses whatever the JSON the server sent back, converting it to usable js object
  const data = await response.json()

  //response.ok is true for 200s, false for anything else (like our 401)
  if (!response.ok) {
    //data.detail is the exact message our FastAPI HTTPException sent back
    //e.g. raise HTTPException(status_code=401, detail="Invalid email or password")
    setErrorMessage(data.detail)
    return
  }

  //login succeeded - save the token so it survives page refreshes
  localStorage.setItem("token", data.access_token)
  console.log("Logged in! Token saved.")
  navigate("/dashboard")
}
//if user enters anything onchange detects that e.target.value becomes that value and setEmail changes it to that value
//so value={email} is now value="b" 
  return (
    <form onSubmit={handleSubmit}>
      <h1>TripEasy</h1>
                                
      {/* only shows this paragraph if errorMessage actually has text in it */}
      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}

      <label>Email</label>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />

      <label>Password</label>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <button type="submit">Log in</button>
    </form>
  )
}

export default LoginForm