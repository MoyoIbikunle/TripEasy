import { useState } from 'react'

function AddActivityForm({ tripId, onActivityAdded }) {
  const [name, setName] = useState("")
  const [startTime, setStartTime] = useState("")
  const [endTime, setEndTime] = useState("")
  const [address, setAddress] = useState("")
  const [cost, setCost] = useState("")
  const [date, setDate] = useState("")

  async function handleSubmit(event) {
    event.preventDefault()
    const token = localStorage.getItem("token")

    const response = await fetch(`http://localhost:8000/trips/${tripId}/activities`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        name: name,
        date: date,
        start_time: startTime,
        end_time: endTime,
        address: address,
        cost: cost ? parseFloat(cost) : null
      })
    })

    const data = await response.json()
    onActivityAdded(data)

    //resetting each piece of state back to empty
    // right after a successful submission
    setName("")
    setDate("")
    setStartTime("")
    setEndTime("")
    setAddress("")
    setCost("")
  }

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" placeholder="Activity name" value={name} onChange={(e) => setName(e.target.value)} required />
      <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
      <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
      <input type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
      <input type="text" placeholder="Address" value={address} onChange={(e) => setAddress(e.target.value)} />
      <input type="number" placeholder="Cost" value={cost} onChange={(e) => setCost(e.target.value)} />
      <button type="submit">Add Activity</button>
    </form>
  )
}

export default AddActivityForm