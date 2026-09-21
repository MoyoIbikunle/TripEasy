  import { useState } from 'react'

function AddAccommodationForm({ tripId, onAccommodationAdded }) {
  const [address, setAddress] = useState("")
  const [checkInDate, setCheckInDate] = useState("")
  const [checkOutDate, setCheckOutDate] = useState("")

  async function handleSubmit(event) {
    event.preventDefault()
    const token = localStorage.getItem("token")

    const response = await fetch(`http://localhost:8000/trips/${tripId}/accommodation`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        address: address,
        check_in_date: checkInDate,
        check_out_date: checkOutDate
      })
    })

    const data = await response.json()
    onAccommodationAdded(data)

    //clear the form for next entry
    setAddress("")
    setCheckInDate("")
    setCheckOutDate("")
  }

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" placeholder="Address" value={address} onChange={(e) => setAddress(e.target.value)} required />
      <input type="date" value={checkInDate} onChange={(e) => setCheckInDate(e.target.value)} />
      <input type="date" value={checkOutDate} onChange={(e) => setCheckOutDate(e.target.value)} />
      <button type="submit">Add Accommodation</button>
    </form>
  )
}

export default AddAccommodationForm