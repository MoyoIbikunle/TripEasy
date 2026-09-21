import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function CreateTrip(){
  const [name, setName] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [errorMessage, setErrorMessage] = useState("")

  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage("")

    const token = localStorage.getItem("token")

    const response = await fetch("http://localhost:8000/trips", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ name: name, start_date: startDate, end_date: endDate })
    })

    const data = await response.json()

    if (!response.ok) {
      setErrorMessage(data.detail)
      return
    }

    navigate("/dashboard")
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>TripEasy</h1>

      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}

      <label>Name</label>
      <input type="text" value={name} onChange={(e) => setName(e.target.value)} required/>

      <label>Start Date</label>
      <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required/>

      <label>End Date</label>
      <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} required/>

      <button type="submit">Create Trip</button>
    </form>
  )
}

export default CreateTrip